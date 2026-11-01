#!/usr/bin/env python3
"""Clean catalog: remove placeholders, TV/movies, music. Keep real games only.
Original preserved at data/games.backup.json."""
import json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "data", "games.json")

games = json.loads(open(CATALOG, 'rb').read().decode('utf-8'))

PLACEHOLDER = re.compile(r'^Cracked Game \d+$')
TV_MOVIE = re.compile(r'(S\d+E\d+|S\d{4}E\d+|\d{4}\.\d{2}\.\d{2}|HDTV|WEB-DL|WEBRip|BluRay|BDRip|DVDRip|x264|x265|H264|H265|HEVC|1080p|720p|2160p|AMZN WEB|SONYLIV|MY5 WEB)', re.I)
MUSIC = re.compile(r'\((?:19|20)\d\d\)\s*$')  # "Album (2026)" at end
TV_NAMES = re.compile(r'(Morning Joe|The Chase|Tipping Point|Wheel Of Fortune|Big Brother|The Block|Country Calendar|BBC |Naked News|WWE |UFC |MotoGP|NBA |NFL )', re.I)

def is_real_game(g):
    t = g.get('title', '')
    if PLACEHOLDER.match(t): return False
    if TV_MOVIE.search(t): return False
    if TV_NAMES.search(t): return False
    # Music: "Artist – Album (Year)" or "Artist - Album (Year)" pattern from TPB/RELOADED
    if MUSIC.search(t) and not re.search(r'(repack|update|edition.*v\d|build|dlc)', t, re.I):
        return False
    # rlsbb music with em-dash/en-dash separator
    if re.search(r'\s[–—]\s', t) and re.search(r'\((?:19|20)\d\d\)', t):
        return False
    return True

real = [g for g in games if is_real_game(g)]
removed = len(games) - len(real)

with open(CATALOG, 'w', encoding='utf-8') as f:
    json.dump(real, f, indent=2, ensure_ascii=False)

print(f'Kept {len(real)} real games, removed {removed} placeholders/non-games')
print(f'Original preserved at data/games.backup.json')
