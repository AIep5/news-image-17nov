# The Daily Globe — 17 November 2026

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/AIep5/news-image-17nov/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard)
[![reward](https://make.fun/badge/news-image-20261117/AIep5/news-image-17nov/reward.svg)](https://make.fun/bounty/news-image-20261117/leaderboard)

A single-file Python program that draws a newspaper front page summing up
Tuesday 17 November 2026 in one image: the U.S. strike on an IRGC missile
site on Qeshm Island and Iran's drone attack on a U.S. radar base in
Bahrain, the second Kerch Bridge strike, the Trump–Xi–Putin meeting set for
Shenzhen, Mongolia's president resigning, Japan scrambling jets, and three
briefs — all dated 17 November 2026.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

`main.py` is standard library only (no network, no randomness, no time, no
files read). Two runs write byte-identical output: a 1024×1024 PNG, well
under the 1 MiB cap. The grader runs it as `python3 -P -s /bot/main.py`,
which works because the program is a single file with no sibling imports.
