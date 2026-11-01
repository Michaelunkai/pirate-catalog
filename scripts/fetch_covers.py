#!/usr/bin/env python3
"""
Fetch actual game cover images for all games in the catalog.
Downloads real cover art from Steam, SteamGridDB, and other sources.
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

# Ensure covers directory exists
os.makedirs(COVERS_DIR, exist_ok=True)

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 15

# Steam API for game covers
STEAM_API = "https://store.steampowered.com/api"
STEAM_GRID_API = "https://www.steamgriddb.com/api/v2"


def slugify(title):
    """Convert title to safe filename."""
    s = re.sub(r"[^a-zA-Z0-9]+", "_", title.lower()).strip("_")
    return s[:60] or "game"


def clean_title_for_search(title):
    """Clean game title for better API matching."""
    # Remove common suffixes/prefixes
    t = title

    # Remove ElAmigos-style suffixes
    t = re.sub(r"\s*-\s*(Un |El |La |Los |Las )?[A-ZÁÉÍÓÚÑ].*$", "", t)
    t = re.sub(r"\s*\([^)]*\)\s*$", "", t)  # Remove trailing parentheses
    t = re.sub(r"\s*v?\d+(\.\d+)*\s*$", "", t)  # Remove version numbers
    t = re.sub(r"\s*(MULTi\d+|ElAmigos|FitGirl|DODI|CODEX|RELOADED|SKIDROW|PLAZA|HOODLUM|TiNYiSO|RUNE|FLT|GOG|Goldberg|Repack).*$", "", t, flags=re.I)
    t = re.sub(r"\s*-\s*.*Repack.*$", "", t, flags=re.I)

    # Spanish to English common translations
    replacements = {
        "un juego de": "",
        "la guerra": "war",
        "el señor": "lord",
        "los anillos": "rings",
        "de": "",
        "del": "",
        "y": "and",
    }

    t = t.strip()

    # If title is very long, take first part
    if len(t) > 40:
        parts = t.split(" - ")
        if parts:
            t = parts[0]

    return t.strip()


def get_cover_path(game_id):
    """Get local path for a game's cover image."""
    return os.path.join(COVERS_DIR, f"{game_id}.jpg")


def cover_exists(game_id):
    """Check if cover already exists locally."""
    path = get_cover_path(game_id)
    return os.path.exists(path) and os.path.getsize(path) > 1000


def fetch_steam_cover(title):
    """Try to fetch cover from Steam API."""
    try:
        clean = clean_title_for_search(title)
        if not clean or len(clean) < 3:
            return None

        # Search Steam
        search_url = f"{STEAM_API}/storesearch/?term={quote_plus(clean)}&l=english&cc=US"
        r = requests.get(search_url, headers=UA, timeout=TIMEOUT)

        if r.status_code == 200:
            data = r.json()
            items = data.get("items", [])
            if items:
                app_id = items[0].get("id")
                if app_id:
                    # Steam header image (landscape) - more reliable
                    return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
    except Exception:
        pass
    return None


def fetch_steamgriddb_cover(title):
    """Try to fetch cover from SteamGridDB."""
    try:
        clean = clean_title_for_search(title)
        if not clean or len(clean) < 3:
            return None

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
                            # Prefer 600x900 portrait covers
                            for grid in grids["data"]:
                                if grid.get("width") == 600 and grid.get("height") == 900:
                                    return grid.get("url")
                            # Fallback to first available
                            return grids["data"][0].get("url")
    except Exception:
        pass
    return None


def fetch_igdb_cover(title):
    """Try to fetch cover from IGDB via their public CDN."""
    # IGDB requires OAuth, skip for now
    return None


def download_cover(url, game_id):
    """Download a cover image to local storage."""
    if not url:
        return False

    try:
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
        if r.status_code == 200 and len(r.content) > 1000:
            # Verify it's an image
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
    """Fetch and download cover for a single game."""
    game_id = game.get("id", slugify(game.get("title", "unknown")))
    title = game.get("title", "")

    if cover_exists(game_id):
        return game_id, True, "exists"

    # Try multiple sources
    cover_url = None

    # Check if game already has imageUrl
    if game.get("imageUrl"):
        cover_url = game["imageUrl"]

    # Try Steam first (most reliable)
    if not cover_url:
        cover_url = fetch_steam_cover(title)

    # Try SteamGridDB
    if not cover_url:
        cover_url = fetch_steamgriddb_cover(title)

    # Download if we found a URL
    if cover_url and download_cover(cover_url, game_id):
        return game_id, True, cover_url

    return game_id, False, None


def main():
    print("Loading catalog...")
    with open(CATALOG, "rb") as f:
        games = json.loads(f.read().decode("utf-8"))

    print(f"Found {len(games)} games. Fetching covers...")

    # Track stats
    success = 0
    failed = 0
    exists = 0
    failed_titles = []

    # Process games in parallel
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_and_download_cover, game): game for game in games}

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

            # Progress update every 100 games
            if i % 100 == 0:
                print(f"Progress: {i}/{len(games)} - {success} downloaded, {exists} existing, {failed} failed")

    print(f"\nComplete!")
    print(f"  Downloaded: {success}")
    print(f"  Already existed: {exists}")
    print(f"  Failed: {failed}")
    print(f"  Total with covers: {success + exists}")

    # Count files in covers directory
    cover_files = [f for f in os.listdir(COVERS_DIR) if f.endswith(".jpg")]
    print(f"  Files in covers/: {len(cover_files)}")

    # Show some failed titles for debugging
    if failed_titles:
        print(f"\nSample failed titles:")
        for t in failed_titles[:10]:
            print(f"  - {t}")


if __name__ == "__main__":
    main()
