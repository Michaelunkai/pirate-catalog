#!/usr/bin/env python3
"""Fix ElAmigos titles that have Spanish descriptions appended.
ElAmigos sitemap titles look like: "GAME NAME\n\nDescription in Spanish..."
"""
import json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "data", "games.json")

games = json.loads(open(CATALOG, 'rb').read().decode('utf-8'))

fixed = 0
for g in games:
    t = g.get('title', '')
    if '\n\n' in t:
        # Take only the first line (the game name)
        name = t.split('\n\n')[0].strip()
        if name != t:
            g['title'] = name
            g['id'] = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower()).strip('_')[:60]
            fixed += 1

with open(CATALOG, 'w', encoding='utf-8') as f:
    json.dump(games, f, indent=2, ensure_ascii=False)

print(f'Fixed {fixed} ElAmigos titles with descriptions')