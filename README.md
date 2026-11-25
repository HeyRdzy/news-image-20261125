# Fervent Sphere — 25 November 2026

[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/HeyRdzy/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/HeyRdzy/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

One image summing up the world's news of Wednesday 25 November 2026: 37 stories across 6 continents and 10 fields, drawn as a dense newspaper front page — masthead, the day in UTC, the day in numbers, 3 lead stories, 10 secondary stories, a world map, 24 numbered briefs and a date check. Every figure was checked against a primary source (Reuters, AP, BBC, RFE/RL, UEFA, WFP, WAFA, Oxfam, company filings, market data).

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` copies `entry.png` to the output directory and verifies the copy byte-for-byte. The image itself is drawn by `render.py` (Python + PIL, no network).

## Entry

- Competition: [news-image-20261125](https://make.fun/bounty/news-image-20261125) — "Sum up 25 November's world news in one image"
- License: MIT
