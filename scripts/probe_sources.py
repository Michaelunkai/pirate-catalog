#!/usr/bin/env python3
"""Probe which external sources are reachable from this machine."""
import requests

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36'}
tests = {
    'apibay_general': 'https://apibay.net/v1/torrents?limit=25',
    'apibay_search': 'https://apibay.net/v1/torrents?query=elden+ring',
    'dodi_feed': 'https://dodi-repacks.site/feed/',
    'fitgirl_feed': 'https://www.fitgirl-repacks.site/feed/',
    'ocean_feed': 'https://oceanofgames.com/feed/',
    'skidrow_feed': 'https://skidrowgames.com/feed',
    'rawg_games': 'https://api.rawg.io/api/games?page_size=10',
    'rawg_search': 'https://api.rawg.io/api/games?search=Elden+Ring',
    'steam_search': 'https://store.steampowered.com/api/storesearch/?term=Elden&cc=us',
    'igdb_free': 'https://api.igdb.com/v1/games/search/all/1',
}

lines = []
for name, url in tests.items():
    try:
        r = requests.get(url, headers=UA, timeout=12, allow_redirects=True)
        ok = 200 <= r.status_code < 400
        lines.append(f"{name:18s} HTTP {r.status_code}  len={len(r.content):,}  {'OK' if ok else 'NO'}")
    except Exception as e:
        lines.append(f"{name:18s} FAIL {type(e).__name__} {str(e)[:50]}")

print('\n'.join(lines))
open('test_install/sources.txt', 'w').write('\n'.join(lines))
