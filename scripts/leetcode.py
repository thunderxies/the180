#!/usr/bin/env python3
"""Fetch LeetCode stats and write leetcode.json.

Runs in GitHub Actions, not the browser: leetcode.com/graphql sends no CORS
headers, so the page can never call it directly. The Action fetches it here and
commits the result, which the page then reads from its own origin.
"""
import json, os, sys, urllib.request, datetime

USER = os.environ.get("LEETCODE_USER", "").strip()
OUT = "leetcode.json"
KEEP_DAYS = 120

# Two separate queries on purpose. A private calendar makes GraphQL null out the
# whole matchedUser object, which would take the solve counts down with it.
Q_STATS = """
query($u:String!){
  matchedUser(username:$u){
    username
    submitStatsGlobal{ acSubmissionNum{ difficulty count } }
  }
}"""

Q_CALENDAR = """
query($u:String!,$y:Int){
  matchedUser(username:$u){
    userCalendar(year:$y){ streak totalActiveDays submissionCalendar }
  }
}"""


def gql(query, variables, user):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://leetcode.com/graphql", data=body,
        headers={"Content-Type": "application/json",
                 "User-Agent": "the180-sync",
                 "Referer": "https://leetcode.com/%s/" % user})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    if not USER:
        print("LEETCODE_USER is not set", file=sys.stderr)
        return 1

    today = datetime.date.today()

    stats = gql(Q_STATS, {"u": USER}, USER)
    user = (stats.get("data") or {}).get("matchedUser")
    if not user:
        print("no such LeetCode user: %s" % USER, file=sys.stderr)
        return 1

    solved = {a["difficulty"]: a["count"] for a in user["submitStatsGlobal"]["acSubmissionNum"]}

    # the calendar can be private per account — the solve counts must survive that
    submissions, streak, active = {}, 0, 0
    try:
        cdata = gql(Q_CALENDAR, {"u": USER, "y": today.year}, USER)
        cuser = (cdata.get("data") or {}).get("matchedUser")
        cal = cuser.get("userCalendar") if cuser else None
        if cal:
            streak = cal.get("streak") or 0
            active = cal.get("totalActiveDays") or 0
            raw = cal.get("submissionCalendar")
            if raw:
                for ts, n in json.loads(raw).items():
                    d = datetime.datetime.fromtimestamp(int(ts), datetime.timezone.utc).date()
                    submissions[d.isoformat()] = submissions.get(d.isoformat(), 0) + n
        else:
            errs = cdata.get("errors") or []
            msg = errs[0].get("message") if errs else "unavailable"
            print("calendar unavailable (%s) — solve counts still tracked" % msg, file=sys.stderr)
    except Exception as e:
        print("calendar fetch failed (%s) — solve counts still tracked" % e, file=sys.stderr)

    # previous run, so solved-per-day can be derived from the running total
    prev = {}
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT))
        except Exception:
            prev = {}

    snaps = dict(prev.get("snapshots") or {})
    solved_by_day = dict(prev.get("solvedByDay") or {})

    key = today.isoformat()
    total = solved.get("All", 0)
    earlier = [v for k, v in sorted(snaps.items()) if k < key]
    if earlier:
        delta = total - earlier[-1]
        if delta > 0:
            solved_by_day[key] = delta
        elif key in solved_by_day and delta <= 0:
            solved_by_day[key] = max(0, delta)
    snaps[key] = total

    cutoff = (today - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    trim = lambda d: {k: v for k, v in d.items() if k >= cutoff}

    out = {
        "updated": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "solved": solved,
        "streak": streak,
        "activeDays": active,
        "submissions": trim(submissions),
        "solvedByDay": trim(solved_by_day),
        "snapshots": trim(snaps),
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("total solved %s, %d calendar days, streak %s" % (total, len(submissions), streak))
    return 0


if __name__ == "__main__":
    sys.exit(main())
