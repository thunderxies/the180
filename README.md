# The 180

A 180-day personal discipline tracker. One page, no build step, no dependencies,
no backend. Everything you log stays in your own browser.

## What it does

- **Today** — a segmented progress ring (one arc per task), streaks, and the day count.
- **Log** — a month calendar and a full 180-day grid; tap any day to see or fix it.
- **Mind** — a thought log. Tag a thought, then write the answer to it. Your thoughts
  for a day also show up inside that day's entry in the Log.
- **Tasks** — add your own. `DO` tasks tick off; `AVOID` tasks record whether you held
  or slipped. A daily target above 1 turns a task into a counter.
- **Health** — sleep, water and steps, with 14-day trends.
- **GitHub** — enter your username and it reads your public activity, showing commits
  per day and ticking the GitHub task on days you pushed.

## Your data

Stored in `localStorage` on the device you use it on. It is never uploaded anywhere
and this repo contains none of it.

Because it is per-browser, **back it up**: Settings → *Copy my data*, and paste the
result somewhere safe. Settings → *Restore* takes it back.

The default task list that ships here is deliberately generic. Add your own in the
Tasks tab — those live only on your phone.

## Running it

It is a static site. Open `index.html`, or serve the folder:

```sh
python3 -m http.server 8000
```

## Licence

MIT
