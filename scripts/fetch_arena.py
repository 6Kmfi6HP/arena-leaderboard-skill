#!/usr/bin/env python3
"""Fetch arena.ai leaderboard rankings (SSR RSC payload, no API key needed).

Usage:
  python3 fetch_arena.py --arena code/webdev [--category react] [--top 10]
  python3 fetch_arena.py --arena code/webdev --list-categories
  python3 fetch_arena.py --arena code/webdev --all --top 5
"""
import argparse, json, os, re, subprocess, sys

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
BASE = 'https://arena.ai/leaderboard'

def fetch_html(route, cache_dir='/tmp/arena-fetch'):
    os.makedirs(cache_dir, exist_ok=True)
    fp = os.path.join(cache_dir, route.replace('/', '_') + '.html')
    url = f'{BASE}/{route}'
    subprocess.run(['curl', '-sL', '-o', fp, url, '-A', UA], timeout=90, check=True)
    return open(fp, encoding='utf-8', errors='ignore').read()

def decode_rsc(html):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,(.*?)\]\)</script>', html, re.S)
    parts = []
    for c in chunks:
        c = c.strip()
        if c.startswith('"') and c.endswith('"'):
            try:
                parts.append(json.loads(c))
                continue
            except Exception:
                pass
        try:
            parts.append(json.loads('"' + c + '"'))
        except Exception:
            parts.append(c)
    return ''.join(parts).replace('"$undefined"', 'null')

def extract_balanced(text, key):
    idx = text.find(key)
    if idx < 0:
        return None
    s = text.find('[', idx)
    depth, in_str, esc = 0, False, False
    for j in range(s, len(text)):
        ch = text[j]
        if in_str:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': in_str = False
        else:
            if ch == '"': in_str = True
            elif ch == '[': depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    return json.loads(text[s:j+1])
    return None

def get_leaderboard(text):
    i = text.find('"leaderboard":{')
    if i < 0:
        return None
    o = text.find('{', i + len('"leaderboard":'))
    depth, in_str, esc = 0, False, False
    lb_end = None
    for j in range(o, len(text)):
        ch = text[j]
        if in_str:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': in_str = False
        else:
            if ch == '"': in_str = True
            elif ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    lb_end = j
                    break
    lb_text = text[o:lb_end + 1]
    # lb_text already contains "entries":[...] (balanced scan ends after it)
    return json.loads(lb_text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arena', default='code/webdev')
    ap.add_argument('--category', default=None)
    ap.add_argument('--top', type=int, default=10)
    ap.add_argument('--list-categories', action='store_true')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--json', action='store_true', help='output raw JSON')
    a = ap.parse_args()

    route = a.arena if not a.category else f'{a.arena}/{a.category}'
    text = decode_rsc(fetch_html(route))

    if a.list_categories:
        cats = extract_balanced(text, '41:')
        if cats and isinstance(cats[0], list):
            items = cats
        elif isinstance(cats, dict):
            items = list(cats.items())
        else:
            items = []
        for item in items:
            name, info = item[0], item[1]
            print(f"{name:28s} {info.get('title',''):28s} group={info.get('group')}")
        return

    lb = get_leaderboard(text)
    if not lb:
        print('FAILED: no leaderboard payload found', file=sys.stderr)
        sys.exit(1)
    tv = re.search(r'"totalVotes":(\d+)', text)
    co = re.search(r'"voteCutoffISOString":"([^"]+)"', text)
    print(f"# {lb['arenaSlug']}/{lb['leaderboardSlug']}  votes={tv.group(1) if tv else '?'}  "
          f"cutoff={co.group(1) if co else '?'}  models={len(lb['entries'])}", file=sys.stderr)
    if a.json:
        print(json.dumps(lb['entries'][:a.top], ensure_ascii=False, indent=1))
        return
    print(f"{'rank':>4} {'model':36s} {'org':10s} {'score':>5} {'votes':>7}")
    for e in lb['entries'][:a.top]:
        print(f"{e['rank']:>4} {e['modelDisplayName'][:36]:36s} "
              f"{(e['modelOrganization'] or '')[:10]:10s} {e['rating']:>5.0f} {e['votes']:>7,}")

if __name__ == '__main__':
    main()
