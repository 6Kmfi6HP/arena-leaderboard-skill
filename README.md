# arena-leaderboard-skill

Agent skill teaching AI coding agents to fetch AI model rankings from [arena.ai](https://arena.ai) leaderboards. Works in Claude Code, Codex, and Hermes Agent.

arena.ai has **no public REST API** — rankings ship inside page HTML as a Next.js RSC payload. This skill decodes that payload. No API key needed.

## Layout

```
SKILL.md                # skill instructions + verified category table
scripts/fetch_arena.py  # fetcher (stdlib only + curl)
```

## Usage

```bash
python3 scripts/fetch_arena.py --arena code/webdev --top 10
python3 scripts/fetch_arena.py --arena code/webdev --list-categories
python3 scripts/fetch_arena.py --arena code/webdev --category gaming --top 5
```

## License

MIT
