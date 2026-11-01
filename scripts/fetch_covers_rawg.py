#!/usr/bin/env python3
"""
Fetch game covers using RAWG API (free, no key required for basic use).
"""

import json
import os
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "data", "games.json")
COVERS_DIR = os.path.join(ROOT, "covers")

os.makedirs(COVERS_DIR, exist_ok=True)

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
TIMEOUT = 15


def slugify(title):
    s = re.sub(r"[^a-zA-Z0-9]+", "_", title.lower()).strip("_")
    return s[:60] or "game"


def clean_title(title):
    """Extract clean game name from title."""
    t = title

    # Remove newlines and extra whitespace
    t = re.sub(r"\s+", " ", t)

    # Remove everything after common patterns
    t = re.split(r"\s*[-–—]\s*(?:v?\d|MULTi|ElAmigos|FitGirl|DODI|CODEX|RELOADED|SKIDROW|PLAZA|HOODLUM|TiNYiSO|RUNE|FLT|GOG|Goldberg|Repack|Free Download|TENOKE|Update)", t, flags=re.I)[0]
    t = re.split(r"\s*Update\s+v?\d", t, flags=re.I)[0]
    t = re.split(r"\s*,\s*v?\d", t)[0]
    t = re.split(r"\s*\([^)]*\)", t)[0]
    t = re.split(r"\s*\[[^\]]*\]", t)[0]

    # Remove special characters
    t = re.sub(r"[�]", "", t)
    t = re.sub(r"[^\x00-\x7F]+", " ", t)  # Remove non-ASCII

    # Remove version numbers at end
    t = re.sub(r"\s+v?\d+(\.\d+)+\s*$", "", t)

    t = t.strip()

    # Take first part if contains description
    if " - " in t:
        t = t.split(" - ")[0]
    if ": " in t and len(t) > 30:
        # Keep the part before colon if it's short (likely the game name)
        parts = t.split(": ")
        if len(parts[0]) < 30:
            t = parts[0] + ": " + parts[1].split()[0] if len(parts) > 1 else parts[0]

    return t.strip()


def get_cover_path(game_id):
    return os.path.join(COVERS_DIR, f"{game_id}.jpg")


def cover_exists(game_id):
    path = get_cover_path(game_id)
    return os.path.exists(path) and os.path.getsize(path) > 1000


def fetch_rawg_cover(title):
    """Fetch cover from RAWG API."""
    clean = clean_title(title)
    if not clean or len(clean) < 2:
        return None

    try:
        # RAWG API - free tier
        url = f"https://api.rawg.io/api/games?key=&search={quote_plus(clean)}&page_size=1"
        r = requests.get(url, headers=UA, timeout=TIMEOUT)

        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            if results:
                game = results[0]
                # Get background image
                img = game.get("background_image")
                if img:
                    return img
    except Exception:
        pass
    return None


def fetch_steam_cover(title):
    """Fetch from Steam as fallback."""
    clean = clean_title(title)
    if not clean or len(clean) < 2:
        return None

    try:
        url = f"https://store.steampowered.com/api/storesearch/?term={quote_plus(clean)}&l=english&cc=US"
        r = requests.get(url, headers=UA, timeout=TIMEOUT)

        if r.status_code == 200:
            data = r.json()
            items = data.get("items", [])
            if items:
                app_id = items[0].get("id")
                if app_id:
                    return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
    except Exception:
        pass
    return None


def download_cover(url, game_id):
    if not url:
        return False

    try:
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
        if r.status_code == 200 and len(r.content) > 1000:
            path = get_cover_path(game_id)
            with open(path, "wb") as f:
                f.write(r.content)
            return True
    except Exception:
        pass
    return False


def fetch_and_download(game):
    game_id = game.get("id", slugify(game.get("title", "unknown")))
    title = game.get("title", "")

    if cover_exists(game_id):
        return game_id, True, "exists"

    # Try RAWG first
    cover_url = fetch_rawg_cover(title)

    # Fallback to Steam
    if not cover_url:
        cover_url = fetch_steam_cover(title)

    if cover_url and download_cover(cover_url, game_id):
        return game_id, True, cover_url

    return game_id, False, None


def main():
    print("Loading catalog...")
    with open(CATALOG, "rb") as f:
        games = json.loads(f.read().decode("utf-8"))

    # Filter to games without covers
    games_without_covers = []
    for g in games:
        game_id = g.get("id", slugify(g.get("title", "")))
        if not cover_exists(game_id):
            games_without_covers.append(g)

    print(f"Games without covers: {len(games_without_covers)}")

    success = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_and_download, game): game for game in games_without_covers}

        for i, future in enumerate(as_completed(futures), 1):
            game_id, ok, url = future.result()
            if ok:
                if url != "exists":
                    success += 1
            else:
                failed += 1

            if i % 50 == 0:
                print(f"Progress: {i}/{len(games_without_covers)} - {success} new, {failed} failed")

    print(f"\nComplete!")
    print(f"  New downloads: {success}")
    print(f"  Failed: {failed}")

    cover_files = [f for f in os.listdir(COVERS_DIR) if f.endswith(".jpg")]
    print(f"  Total covers: {len(cover_files)}")


if __name__ == "__main__":
    main()
