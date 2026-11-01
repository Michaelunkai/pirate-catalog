#!/usr/bin/env python3
"""
Fetch actual game cover images for all games in the catalog.
Uses multiple sources and aggressive title cleaning.
"""

import json
import os
import sys
import time
import hashlib
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "data", "games.json")
COVERS_DIR = os.path.join(ROOT, "covers")

os.makedirs(COVERS_DIR, exist_ok=True)

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 15

STEAM_API = "https://store.steampowered.com/api"
STEAM_GRID_API = "https://www.steamgriddb.com/api/v2"


def slugify(title):
    s = re.sub(r"[^a-zA-Z0-9]+", "_", title.lower()).strip("_")
    return s[:60] or "game"


def clean_title_aggressive(title):
    """Aggressively clean game title for API matching."""
    t = title

    # Remove everything after common delimiters
    t = re.split(r"\s*[-–—]\s*(?:v?\d|MULTi|ElAmigos|FitGirl|DODI|CODEX|RELOADED|SKIDROW|PLAZA|HOODLUM|TiNYiSO|RUNE|FLT|GOG|Goldberg|Repack|Free Download)", t, flags=re.I)[0]
    t = re.split(r"\s*\([^)]*\)", t)[0]  # Remove parentheses
    t = re.split(r"\s*\[[^\]]*\]", t)[0]  # Remove brackets

    # Remove version numbers
    t = re.sub(r"\s+v?\d+(\.\d+)+\s*$", "", t)
    t = re.sub(r"\s+Build\s+\d+\s*$", "", t, flags=re.I)

    # Remove "Free Download" suffix
    t = re.sub(r"\s*Free Download\s*$", "", t, flags=re.I)

    # Spanish/foreign language cleanup - take only the game name part
    # Common pattern: "Game Name - Description in Spanish"
    if " - " in t:
        parts = t.split(" - ")
        # Take the shortest part that's likely the game name
        t = min(parts, key=len)

    # Remove common Spanish words
    spanish_patterns = [
        r"\s+un\s+juego\s+de.*$",
        r"\s+una\s+aventura.*$",
        r"\s+el\s+señor.*$",
        r"\s+la\s+guerra.*$",
        r"\s+los\s+.*$",
    ]
    for p in spanish_patterns:
        t = re.sub(p, "", t, flags=re.I)

    t = t.strip()

    # If still too long, truncate at word boundary
    if len(t) > 50:
        words = t.split()
        t = ""
        for w in words:
            if len(t) + len(w) + 1 <= 50:
                t += " " + w if t else w
            else:
                break

    return t.strip()


def get_cover_path(game_id):
    return os.path.join(COVERS_DIR, f"{game_id}.jpg")


def cover_exists(game_id):
    path = get_cover_path(game_id)
    return os.path.exists(path) and os.path.getsize(path) > 1000


def fetch_steam_cover(title):
    """Try Steam API with multiple title variations."""
    variations = [
        title,
        clean_title_aggressive(title),
        title.split(" - ")[0] if " - " in title else title,
    ]

    for clean in variations:
        if not clean or len(clean) < 2:
            continue

        try:
            search_url = f"{STEAM_API}/storesearch/?term={quote_plus(clean)}&l=english&cc=US"
            r = requests.get(search_url, headers=UA, timeout=TIMEOUT)

            if r.status_code == 200:
                data = r.json()
                items = data.get("items", [])
                if items:
                    app_id = items[0].get("id")
                    if app_id:
                        return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
        except Exception:
            continue
    return None


def fetch_steamgriddb_cover(title):
    """Try SteamGridDB with multiple title variations."""
    variations = [
        title,
        clean_title_aggressive(title),
        title.split(" - ")[0] if " - " in title else title,
    ]

    for clean in variations:
        if not clean or len(clean) < 2:
            continue

        try:
            search_url = f"{STEAM_GRID_API}/search/autocomplete/{quote_plus(clean)}"
            r = requests.get(search_url, headers=UA, timeout=TIMEOUT)

            if r.status_code == 200:
                results = r.json()
                if results.get("data"):
                    game_id = results["data"][0].get("id")
                    if game_id:
                        grids_url = f"{STEAM_GRID_API}/grids/game/{game_id}"
                        r2 = requests.get(grids_url, headers=UA, timeout=TIMEOUT)
                        if r2.status_code == 200:
                            grids = r2.json()
                            if grids.get("data"):
                                for grid in grids["data"]:
                                    if grid.get("width") == 600 and grid.get("height") == 900:
                                        return grid.get("url")
                                return grids["data"][0].get("url")
        except Exception:
            continue
    return None


def download_cover(url, game_id):
    if not url:
        return False

    try:
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
        if r.status_code == 200 and len(r.content) > 1000:
            content_type = r.headers.get("Content-Type", "")
            if "image" in content_type or url.endswith((".jpg", ".jpeg", ".png", ".webp")):
                path = get_cover_path(game_id)
                with open(path, "wb") as f:
                    f.write(r.content)
                return True
    except Exception:
        pass
    return False


def fetch_and_download_cover(game):
    game_id = game.get("id", slugify(game.get("title", "unknown")))
    title = game.get("title", "")

    if cover_exists(game_id):
        return game_id, True, "exists"

    cover_url = None

    if game.get("imageUrl"):
        cover_url = game["imageUrl"]

    if not cover_url:
        cover_url = fetch_steam_cover(title)

    if not cover_url:
        cover_url = fetch_steamgriddb_cover(title)

    if cover_url and download_cover(cover_url, game_id):
        return game_id, True, cover_url

    return game_id, False, None


def main():
    print("Loading catalog...")
    with open(CATALOG, "rb") as f:
        games = json.loads(f.read().decode("utf-8"))

    # Filter out non-games first
    non_game_patterns = [
        r'S\d+E\d+', r'S\d{4}E\d+', r'\d{4}\.\d{2}\.\d{2}',
        r'HDTV', r'WEB-DL', r'WEBRip', r'BluRay', r'BDRip',
        r'x264', r'x265', r'H264', r'H265', r'HEVC',
        r'1080p', r'720p', r'2160p', r'4K',
        r'UFC', r'WWE', r'NFL', r'NBA', r'MotoGP',
        r'Morning Joe', r'The Chase', r'Tipping Point', r'Wheel Of Fortune',
        r'Big Brother', r'The Block', r'BBC', r'News'
    ]

    actual_games = []
    for g in games:
        title = g.get('title', '')
        is_non_game = any(re.search(p, title, re.I) for p in non_game_patterns)
        if not is_non_game:
            actual_games.append(g)

    print(f"Found {len(actual_games)} actual games (filtered from {len(games)} total)")
    print("Fetching covers...")

    success = 0
    failed = 0
    exists = 0
    failed_titles = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_and_download_cover, game): game for game in actual_games}

        for i, future in enumerate(as_completed(futures), 1):
            game_id, ok, url = future.result()
            if ok:
                if url == "exists":
                    exists += 1
                else:
                    success += 1
            else:
                failed += 1
                failed_titles.append(futures[future].get("title", "Unknown")[:50])

            if i % 100 == 0:
                print(f"Progress: {i}/{len(actual_games)} - {success} new, {exists} existing, {failed} failed")

    print(f"\nComplete!")
    print(f"  New downloads: {success}")
    print(f"  Already existed: {exists}")
    print(f"  Failed: {failed}")
    print(f"  Total with covers: {success + exists}")

    cover_files = [f for f in os.listdir(COVERS_DIR) if f.endswith(".jpg")]
    print(f"  Files in covers/: {len(cover_files)}")

    if failed_titles:
        print(f"\nSample failed titles:")
        for t in failed_titles[:15]:
            print(f"  - {t}")


if __name__ == "__main__":
    main()
