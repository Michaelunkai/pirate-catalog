#!/usr/bin/env python3
"""
Filter out non-game content from the catalog.
Removes TV shows, movies, sports events that were incorrectly scraped.
"""

import json
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "data", "games.json")

# Patterns that indicate non-game content
NON_GAME_PATTERNS = [
    # TV Shows
    r"S\d+E\d+",  # Season/Episode format
    r"S\d{4}E\d+",  # 2026 Season format
    r"\d{4}\.\d{2}\.\d{2}",  # Date format like 2026.10.29
    r"HDTV",
    r"WEB-DL",
    r"WEBRip",
    r"BluRay",
    r"BDRip",
    r"DVDRip",
    r"x264",
    r"x265",
    r"H264",
    r"H265",
    r"HEVC",
    r"1080p",
    r"720p",
    r"2160p",
    r"4K",
    r"AMZN",
    r"NF",
    r"DSNP",
    r"HULU",
    r"ATVP",
    # Sports
    r"UFC",
    r"WWE",
    r"NFL",
    r"NBA",
    r"MLB",
    r"NHL",
    r"MotoGP",
    r"F1",
    r"Formula",
    r"Boxing",
    r"MMA",
    # Movies
    r"\d{4}\s+(1080p|720p|BluRay|BDRip|WEB)",
    r"Remastered\s+1080p",
    r"Criterion",
    # TV Show names
    r"Morning Joe",
    r"The Chase",
    r"Tipping Point",
    r"Wheel Of Fortune",
    r"Big Brother",
    r"The Block",
    r"Country Calendar",
    r"BBC",
    r"News",
    r"Show",
    r"Episode",
    r"Season",
]

# Compile patterns
PATTERNS = [re.compile(p, re.IGNORECASE) for p in NON_GAME_PATTERNS]


def is_likely_game(title):
    """Check if title is likely a game (not TV/movie/sports)."""
    # Check for non-game patterns
    for pattern in PATTERNS:
        if pattern.search(title):
            return False

    # Must not be too short or too generic
    if len(title) < 3:
        return False

    return True


def main():
    print("Loading catalog...")
    with open(CATALOG, "rb") as f:
        games = json.loads(f.read().decode("utf-8"))

    print(f"Original count: {len(games)}")

    # Filter games
    filtered = []
    removed = []

    for game in games:
        title = game.get("title", "")
        if is_likely_game(title):
            filtered.append(game)
        else:
            removed.append(title)

    print(f"Filtered count: {len(filtered)}")
    print(f"Removed: {len(removed)} non-game entries")

    # Show sample of removed items
    print(f"\nSample removed items:")
    for t in removed[:15]:
        print(f"  - {t[:60]}")

    # Save filtered catalog
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)

    print(f"\nSaved filtered catalog with {len(filtered)} games.")


if __name__ == "__main__":
    main()
