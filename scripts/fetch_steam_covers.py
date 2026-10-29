#!/usr/bin/env python3
"""
Bulk fetch Steam cover images for all games in the catalog.
Uses store.steampowered.com API: search -> appdetails -> header_image, capsule_image, screenshots.
"""

import json
import time
import requests
from pathlib import Path

CATALOG_PATH = Path("F:/study/projects/pirate-catalog/data/games.json")
SEARCH_URL = "https://store.steampowered.com/api/storesearch/"
APPDETAILS_URL = "https://store.steampowered.com/api/appdetails"

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search_steam(title):
    """Search Steam store for a game title, return appid if found."""
    try:
        params = {"term": title, "cc": "us", "l": "en"}
        r = requests.get(SEARCH_URL, params=params, headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            items = data.get("items", [])
            if items:
                return items[0]["id"]
    except Exception as e:
        pass
    return None

def get_app_details(appid):
    """Fetch app details from Steam API."""
    try:
        params = {"appids": str(appid)}
        r = requests.get(APPDETAILS_URL, params=params, headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            game_data = data.get(str(appid), {}).get("data", {})
            return game_data
    except Exception as e:
        pass
    return None

def sanitize_title(title):
    """Clean title for better Steam search results."""
    import re
    # Take first line only (many titles have descriptions after newlines)
    title = title.split('\n')[0]
    # Remove version numbers, "Repack", "GOG", etc.
    title = re.sub(r'\s+\(.*?\)\s*$', '', title)
    title = re.sub(r'\s+\[.*?\]\s*$', '', title)
    title = re.sub(r'\b(Repack|GOG|Steam|Crack|Torrent|Full|Game|Download)\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s+', ' ', title).strip()
    # Strip non-ASCII characters to avoid encoding issues in console output
    title = title.encode('ascii', 'replace').decode('ascii')
    return title

def main():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        games = json.load(f)

    total = len(games)
    updated = 0
    failed = 0
    skipped = 0

    print(f"Total games: {total}")

    for i, game in enumerate(games):
        title = game.get("title", "")
        if not title:
            skipped += 1
            continue

        # Skip if already has imageUrl
        if game.get("imageUrl"):
            skipped += 1
            continue

        clean_title = sanitize_title(title)
        print(f"[{i+1}/{total}] Searching: {clean_title[:60]}...")

        appid = search_steam(clean_title)
        if not appid:
            print(f"  Not found on Steam")
            failed += 1
            time.sleep(0.5)
            continue

        print(f"  Found appid: {appid}")
        details = get_app_details(appid)
        if not details:
            print(f"  No details returned")
            failed += 1
            time.sleep(0.5)
            continue

        header = details.get("header_image", "")
        capsule = details.get("capsule_image", "")
        background = details.get("background", "")
        background_raw = details.get("background_raw", "")
        screenshots = details.get("screenshots", [])

        if not header and not capsule:
            print(f"  No cover images found")
            failed += 1
            time.sleep(0.5)
            continue

        # Update game with Steam covers
        game["imageUrl"] = header
        game["capsuleUrl"] = capsule
        game["backgroundUrl"] = background or background_raw
        game["steamAppId"] = appid
        game["screenshots"] = [s["path_full"] for s in screenshots[:5]]
        game["screenshotThumbs"] = [s["path_thumbnail"] for s in screenshots[:5]]

        print(f"  OK | header: {header[:55]}...")
        print(f"  OK | capsule: {capsule[:55] if capsule else 'none'}...")
        print(f"  OK | screenshots: {len(game['screenshots'])}")
        updated += 1

        # Rate limit
        time.sleep(1.0)

        # Save progress every 25 games
        if updated % 25 == 0:
            with open(CATALOG_PATH, "w", encoding="utf-8") as f:
                json.dump(games, f, indent=2, ensure_ascii=False)
            print(f"  --- Progress saved ({updated} updated) ---")

    # Final save (must succeed — no Unicode issues now)
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=2, ensure_ascii=False)

    print(f"\n=== DONE ===")
    print(f"Total: {total}")
    print(f"Updated with Steam covers: {updated}")
    print(f"Failed (not on Steam): {failed}")
    print(f"Skipped: {skipped}")

if __name__ == "__main__":
    main()