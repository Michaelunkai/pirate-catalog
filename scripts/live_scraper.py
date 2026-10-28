#!/usr/bin/env python3
"""Live catalog updater -- pulls real cracks from every reachable repacker feed.

For each source we try several candidate URLs until one answers over plain
HTTP. Feed items become catalog entries when their title is not already in
data/games.json, so re-running only ever ADDS what has genuinely dropped
newly. Everything else (gradients, genres, sizes) is derived from the feed.

Usage:
    python scripts/live_scraper.py            # update data/games.json in place
    python scripts/live_scraper.py --dry-run  # show what would be added
"""

import json
import os
import re
import sys
import html
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "data", "games.json")

# name -> list of candidate URLs tried in order; first success wins.
SOURCES = {
    "DODI": ["https://dodi-repacks.site/feed/", "https://www.dodi-repacks.site/feed/"],
    "FitGirl": [
        "https://www.fitgirl-repacks.site/feed/",
        "https://fitgirl-repacks.site/feed/",
    ],
    "CODEX": ["https://codex-team.org/feed/", "https://www.codex-team.org/feed/"],
    "RELOADED": ["https://reloaded-games.net/feed/", "https://www.reloaded-games.net/feed/"],
    "SKIDROW": ["http://skidrow.co/feed/", "https://www.skidrow.co/feed/"],
    "ElAmigos": ["https://elamigos.co/feed/", "https://www.elamigos.co/feed/"],
    "TOKYO": ["https://tokyobrothers.com/feed/", "https://www.tokyobrothers.com/feed/"],
    "NINTENDO CAVE": ["https://nintendocave.io/feed/", "https://www.nintendocave.io/feed/"],
}

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TIMEOUT = 12

GRADIENTS = [
    ("linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)", "deep blue"),
    ("linear-gradient(135deg, #2c003e 0%, #4a0e4e 50%, #833ab4 100%)", "violet"),
    ("linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)", "teal"),
    ("linear-gradient(135deg, #41295a 0%, #2F0743 100%)", "indigo"),
    ("linear-gradient(135deg, #141e30 0%, #243b55 100%)", "navy"),
    ("linear-gradient(135deg, #3a1c71 0%, #d76d77 100%)", "magenta"),
    ("linear-gradient(135deg, #000428 0%, #004e92 100%)", "ocean"),
    ("linear-gradient(135deg, #232526 0%, #414345 100%)", "slate"),
]

GENRE_KEYWORDS = [
    (("rpg",), "rpg", "RPG / Open World"),
    (("action", "adventure"), "action-adventure", "Action Adventure"),
    (("shooter", "fps", "shoot"), "shooter", "FPS / Shooter"),
    (("racing", "drift", "motorsport"), "racing", "Racing"),
    (("strategy", "rtss", "rts", "civilization"), "strategy", "Strategy"),
    (("sports", "football", "soccer", "nba"), "sports", "Sports"),
    (("simulation", "sim", "manager"), "simulation", "Simulation"),
    (("survival", "horror"), "survival-horror", "Survival Horror"),
    (("sandbox", "crafting", "building"), "sandbox", "Sandbox"),
    (("mmorpg", "mmo"), "mmorpg", "MMORPG"),
    (("fighting",), "fighting", "Fighting"),
    (("platformer", "metroidvania"), "platformer", "Platformer"),
    (("card", "roguelike", "deckbuilder"), "roguelike", "Roguelike"),
]


def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def parse_items(xml_bytes):
    """Yield (title, link, date_str, description) from RSS or Atom.

    Uses BeautifulSoup so feeds with malformed XML (DODI's embedded HTML
    spans inside <comments>) still parse cleanly.
    """
    soup = BeautifulSoup(xml_bytes, "xml")
    for item in soup.find_all(["item", "entry"]):
        t = item.find("title")
        title = t.get_text(strip=True) if t is not None else ""
        l = item.find("link")
        link = l.get_text(strip=True) if l is not None else ""
        d = item.find("pubDate") or item.find("updated")
        date_s = d.get_text(strip=True) if d is not None else ""
        desc_el = item.find("description") or item.find("summary")
        desc = strip_html(desc_el.decode_contents()) if desc_el is not None else ""
        if title and not title.endswith("Repacks") and not re.match(
            r"^(Updates Digest|Upcoming Repacks|Some important Messages)", title
        ):
            yield title, link, date_s, desc[:300]


def guess_genre(title):
    low = title.lower()
    for keys, genre, label in GENRE_KEYWORDS:
        if any(k in low for k in keys):
            return genre, label
    return "action-adventure", "Action Adventure"


def size_from_desc(desc):
    m = re.search(r"(?:size|download)[^0-9]*([\d.]+\s*(?:GB|MB))", desc, re.I)
    if m:
        return m.group(1).upper().replace(" MB", " MB").replace(" GB", " GB")
    return "Unknown"


def clean_title(title):
    """Strip DODI-style '1234- ...' prefixes and '[... Repack]' suffixes."""
    t = re.sub(r"^\d+\s*[-–]\s*", "", title).strip()
    t = re.sub(r"\s*\[[^\]]*(?:repack|MULTi\d+)[^\]]*\]$", "", t, flags=re.I).strip()
    return t


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "game"


def norm_title(title):
    t = re.sub(r"[^a-z0-9 ]+", "", title.lower())
    t = re.sub(r"\b(edition|repack|v\d+|\w+\.\d+(\.\d+)?)\b", "", t)
    return re.sub(r"\s+", " ", t).strip()


def parse_date(s):
    from email.utils import parsedate_to_datetime

    try:
        return parsedate_to_datetime(s.strip())
    except Exception:
        return datetime.now(timezone.utc)


def fetch_source(name, urls):
    """Return list of feed items from the first URL that answers."""
    for url in urls:
        try:
            r = requests.get(url, headers=UA, timeout=TIMEOUT)
            if r.status_code == 200 and (b"<item>" in r.content or b"<entry>" in r.content):
                items = [it for it in parse_items(r.content)]
                print(f"  {name}: {len(items)} items via {url}")
                return name, items
        except requests.RequestException as e:
            print(f"  {name}: {url} -> {type(e).__name__}", file=sys.stderr)
    print(f"  {name}: no reachable feed (skipped)")
    return name, []


def main():
    dry = "--dry-run" in sys.argv
    with open(CATALOG, encoding="utf-8") as f:
        games = json.load(f)

    known = set()
    for g in games:
        known.add(norm_title(g["title"]))
        known.add(slugify(g["title"]))

    today = datetime.now(timezone.utc).date()
    new_games = []
    seen = set(known)
    live_sources = []

    # Newest cracks first: process sources, keep only titles not already held.
    for source, urls in SOURCES.items():
        _, items = fetch_source(source, urls)
        if items:
            live_sources.append(source)
        for raw_title, link, date_s, desc in items:
            title = clean_title(raw_title)
            key = norm_title(title)
            if key in seen:
                continue
            seen.add(key)
            dt = parse_date(date_s)
            age_days = (today - dt.date()).days
            genre, label = guess_genre(title)
            size = size_from_desc(desc)
            entry = {
                "id": slugify(title),
                "title": title,
                "genre": genre,
                "genreLabel": label,
                "description": (desc[:160] + "...") if len(desc) > 160 else (desc or f"{source} repack."),
                "crackedBy": source,
                "crackedDate": dt.strftime("%Y-%m-%d"),
                "uploadedDate": dt.strftime("%Y-%m-%d"),
                "size": size,
                "sizeBytes": int(float(re.sub(r"[^0-9.]", "", size)) * (1e9 if "GB" in size else 1e6)) if re.search(r"\d", size) else 0,
                "version": "",
                "isUpcoming": False,
                "isJustDropped": age_days <= 7,
                "isLatest": age_days <= 3,
                "rating": round(4.0 + min(age_days, 5) * 0.02, 1),
                "tags": [genre],
                "imageGradient": GRADIENTS[abs(hash(title)) % len(GRADIENTS)][0],
                "repack": None,
                "sources": [source],
                "feedUrl": link,
            }
            new_games.append(entry)
            print(f"  + [{source}] {title}")

    if dry:
        print(f"\nDRY RUN: {len(new_games)} new games would be added.")
        return

    # Dedupe ids against existing and among themselves.
    used_ids = {g["id"] for g in games} | set()
    for g in new_games:
        base, n = g["id"], 2
        while g["id"] in used_ids:
            g["id"] = f"{base}-{n}"
            n += 1
        used_ids.add(g["id"])

    games = new_games + games
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=2, ensure_ascii=False)

    print(f"\nCatalog now holds {len(games)} games ({len(new_games)} live additions).")
    print(f"Live sources this run: {', '.join(live_sources) if live_sources else 'none'}")


if __name__ == "__main__":
    main()
