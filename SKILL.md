---
name: arena-leaderboard
description: Use when fetching arena.ai leaderboard rankings.
---

# Arena Leaderboard Fetcher

arena.ai has no public REST API. Rankings ship inside the page HTML as a
Next.js RSC payload (`self.__next_f.push` chunks). This skill decodes that
payload — no API key needed.

## Quick start

```bash
python3 scripts/fetch_arena.py --arena code/webdev --top 10
python3 scripts/fetch_arena.py --arena code/webdev --list-categories
python3 scripts/fetch_arena.py --arena code/webdev --category gaming --top 5
python3 scripts/fetch_arena.py --arena code/webdev --category react --top 5 --json
```

Script lives in `scripts/fetch_arena.py` (stdlib only + `curl`). Cache dir
defaults to `/tmp/arena-fetch`; delete it for a fresh pull.

## Verified arenas and category slugs

WebDev arena (`code/webdev`, snapshot cutoff 2026-10-01, 12 categories):

| Route slug | Title | Group | Models | Votes |
|---|---|---|---|---|
| overall (default) | Overall | — | 138 | 838,388 |
| fullstack | Fullstack | — | 77 | 86,350 |
| frontend | Frontend | — | 138 | 745,814 |
| html | HTML | frontend-technology | 136 | 181,254 |
| react | React | frontend-technology | 122 | 562,661 |
| brand-marketing | Brand & Marketing | domain | 137 | 238,999 |
| reference-based-design | Reference-Based Design | domain | 137 | 197,867 |
| data-analytics | Data & Analytics | domain | 137 | 188,586 |
| consumer-product | Consumer Product | domain | 137 | 176,915 |
| gaming | Gaming | domain | 137 | 226,275 |
| simulations | Simulations | domain | 137 | 127,558 |
| content-creation-tools | Content Creation Tools | domain | 133 | 91,617 |

Other arenas use the same mechanism with different slugs —
`--list-categories` shows what's available, e.g. `--arena code` or
`--arena text`. Snapshot IDs look like
`leaderboard-sets/public/leaderboards/<slug>-raw/leaderboard-snapshots/latest`.

## Entry fields

Each entry: `rank, rankUpper, rankLower, modelKey, modelDisplayName,
rating (float), ratingUpper, ratingLower, votes, modelOrganization,
modelUrl, license, inputPricePerMillion, outputPricePerMillion,
contextLength`. Displayed score = `round(rating)`; CI shown as
`+upper/-lower` deltas; Rank Spread column = `rankUpper–rankLower`.

## Client-side filters (no new fetch needed)

URL params `rankBy=models|labs`, `license=all|proprietary|open-source`,
`q=<search>`, `autoeval=1`, `/pareto` suffix only re-slice the same snapshot
(verified: identical snapshot IDs). Ranges for score/input-price/
output-price/context sliders derive from entry min/max at runtime. Re-rank
locally after filtering (`rank=t+1`); Day1-marked rows keep original rank
with `overallRank` preserved.

## Pitfalls

- Do NOT probe `/api/*` — there is none; a 200 HTML page is the data source.
- Never `curl ... | python3` (security scanner blocks pipes); the script
  writes HTML to disk first, then parses.
- RSC chunks are JSON-string-encoded: decode each with `json.loads` on the
  quoted literal, then join. The `"$undefined"` sentinel must be replaced
  before `json.loads` of the payload.
- The `leaderboard` object already contains `entries` — parse it with one
  balanced-brace scan, not two.
- Category list key `41:` / groups key `42:` are positional RSC refs, not
  stable names — locate via `"categoryFilterSections"` context if they move.
- `hasStyleControl=false` on WebDev: skip style-control suffix logic.
