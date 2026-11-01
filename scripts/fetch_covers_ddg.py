#!/usr/bin/env python3
"""
Fetch game covers using DuckDuckGo image search.
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 20


def slugify(title):
    s = re.sub(r"[^a-zA-Z0-9]+", "_", title.lower()).strip("_")
    return s[:60] or "game"


def clean_title(title):
    """Extract clean game name."""
    t = title
    t = re.sub(r"\s+", " ", t)

    # Remove everything after common delimiters
    delimiters = [" - ", " – ", " — ", " v", " V", " (", " [", ", v", " Update", " MULTi", " ElAmigos", " FitGirl", " DODI", " CODEX", " RELOADED", " SKIDROW", " PLAZA", " RUNE", " FLT", " GOG", " TENOKE", " Free Download"]
    for d in delimiters:
        if d in t:
            t = t.split(d)[0]

    # Remove special characters
    t = re.sub(r"[�]", "", t)
    t = re.sub(r"[^\x00-\x7F]+", " ", t)

    t = t.strip()

    # Truncate if too long
    if len(t) > 40:
        words = t.split()
        t = ""
        for w in words:
            if len(t) + len(w) + 1 <= 40:
                t += " " + w if t else w
            else:
                break

    return t.strip()


def get_cover_path(game_id):
    return os.path.join(COVERS_DIR, f"{game_id}.jpg")


def cover_exists(game_id):
    path = get_cover_path(game_id)
    return os.path.exists(path) and os.path.getsize(path) > 1000


def fetch_ddg_image(title):
    """Fetch image from DuckDuckGo."""
    clean = clean_title(title)
    if not clean or len(clean) < 2:
        return None

    try:
        # DuckDuckGo image search
        query = f"{clean} game cover"
        url = f"https://duckduckgo.com/?q={quote_plus(query)}&iax=images&ia=images"

        r = requests.get(url, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return None

        # Extract vqd token
        vqd_match = re.search(r'vqd="([^"]+)"', r.text)
        if not vqd_match:
            vqd_match = re.search(r"vqd=([\d-]+)&", r.text)
        if not vqd_match:
            return None

        vqd = vqd_match.group(1)

        # Fetch images
        img_url = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={quote_plus(query)}&vqd={vqd}"
        r2 = requests.get(img_url, headers={**UA, "Referer": "https://duckduckgo.com/"}, timeout=TIMEOUT)

        if r2.status_code == 200:
            data = r2.json()
            results = data.get("results", [])
            if results:
                # Get first image
                return results[0].get("image")
    except Exception:
        pass
    return None


def fetch_steam_direct(title):
    """Try direct Steam CDN with common app IDs."""
    clean = clean_title(title).lower()

    # Known game mappings
    known_games = {
        "cyberpunk": "1091500",
        "elden ring": "1245620",
        "god of war": "1593500",
        "horizon": "1151640",
        "spider-man": "1817070",
        "the last of us": "1888930",
        "red dead redemption": "1174180",
        "gta": "271590",
        "witcher": "292030",
        "fallout": "377160",
        "skyrim": "489830",
        "dark souls": "570940",
        "sekiro": "814380",
        "bloodborne": "0",  # Not on Steam
        "diablo": "0",  # Battle.net
        "starfield": "1716740",
        "hogwarts": "990080",
        "call of duty": "1938090",
        "minecraft": "0",  # Not on Steam
        "fortnite": "0",  # Epic
        "apex": "1172470",
        "destiny": "1085660",
        "warframe": "230410",
        "path of exile": "238960",
        "lost ark": "1599340",
        "new world": "1063730",
        "final fantasy": "0",
        "monster hunter": "582010",
        "resident evil": "1196590",
        "devil may cry": "601150",
        "street fighter": "1172540",
        "tekken": "1778820",
        "mortal kombat": "1971870",
        "fifa": "1811260",
        "nba": "0",
        "madden": "0",
        "assassin": "812140",
        "far cry": "13520",
        "watch dogs": "0",
        "ghost recon": "0",
        "rainbow six": "359550",
        "division": "0",
        "borderlands": "397540",
        "bioshock": "8870",
        "doom": "379720",
        "wolfenstein": "612880",
        "quake": "0",
        "half-life": "70",
        "portal": "400",
        "left 4 dead": "550",
        "counter-strike": "730",
        "team fortress": "440",
        "dota": "570",
        "pubg": "578080",
        "rust": "252490",
        "ark": "346110",
        "valheim": "892970",
        "terraria": "105600",
        "stardew": "413150",
        "hollow knight": "367520",
        "celeste": "504230",
        "hades": "1145360",
        "dead cells": "588650",
        "ori": "1057090",
        "cuphead": "268910",
        "undertale": "391540",
        "deltarune": "1690940",
        "among us": "945360",
        "fall guys": "0",
        "phasmophobia": "739630",
        "lethal company": "1966720",
        "content warning": "2881650",
        "palworld": "1623730",
        "enshrouded": "1203620",
        "satisfactory": "526870",
        "factorio": "427520",
        "dyson sphere": "1366540",
        "rimworld": "294100",
        "oxygen": "457140",
        "cities": "255710",
        "civilization": "289070",
        "total war": "1142710",
        "age of empires": "1017900",
        "starcraft": "0",
        "warcraft": "0",
        "diablo": "0",
        "path of exile": "238960",
        "grim dawn": "219990",
        "torchlight": "200710",
        "titan quest": "475150",
        "last epoch": "899770",
        "wolcen": "424370",
        "baldur": "1086940",
        "divinity": "1086940",
        "pillars": "560130",
        "tyranny": "362960",
        "wasteland": "719040",
        "fallout": "377160",
        "outer worlds": "578650",
        "mass effect": "1328670",
        "dragon age": "0",
        "kotor": "32370",
        "jedi": "1172380",
        "battlefront": "0",
        "squadron": "1222730",
        "lego": "0",
        "harry potter": "990080",
        "lord of the rings": "0",
        "hobbit": "0",
        "shadow of mordor": "241930",
        "shadow of war": "356190",
        "middle-earth": "0",
        "batman": "208650",
        "arkham": "208650",
        "spider-man": "1817070",
        "avengers": "0",
        "guardians": "0",
        "xcom": "200510",
        "gears": "0",
        "halo": "976730",
        "destiny": "1085660",
        "titanfall": "1237970",
        "apex": "1172470",
        "battlefield": "0",
        "call of duty": "1938090",
        "modern warfare": "1938090",
        "warzone": "0",
        "black ops": "0",
        "zombies": "0",
        "overwatch": "0",
        "valorant": "0",
        "league": "0",
        "dota": "570",
        "csgo": "730",
        "counter-strike": "730",
        "rainbow six": "359550",
        "siege": "359550",
        "fortnite": "0",
        "pubg": "578080",
        "warzone": "0",
        "apex": "1172470",
        "escape from tarkov": "0",
        "hunt showdown": "594650",
        "dead by daylight": "381210",
        "friday 13th": "0",
        "evil dead": "1493760",
        "texas chainsaw": "0",
        "horror": "0",
        "resident evil": "1196590",
        "silent hill": "0",
        "dead space": "1693980",
        "callisto": "0",
        "alien": "0",
        "predator": "0",
        "terminator": "0",
        "robocop": "0",
        "rambo": "0",
        "expendables": "0",
        "john wick": "0",
        "matrix": "0",
        "cyberpunk": "1091500",
        "deus ex": "337000",
        "system shock": "0",
        "bioshock": "8870",
        "prey": "480490",
        "dishonored": "217980",
        "deathloop": "1252330",
        "redfall": "0",
        "starfield": "1716740",
        "elder scrolls": "489830",
        "skyrim": "489830",
        "oblivion": "22330",
        "morrowind": "22320",
        "fallout": "377160",
        "new vegas": "22380",
        "outer worlds": "578650",
        "avowed": "0",
        "fable": "0",
        "everwild": "0",
        "sea of thieves": "0",
        "state of decay": "0",
        "grounded": "0",
        "pentiment": "0",
        "hi-fi rush": "0",
        "psychonauts": "0",
        "banjo": "0",
        "conker": "0",
        "perfect dark": "0",
        "killer instinct": "0",
        "crackdown": "0",
        "sunset overdrive": "0",
        "quantum break": "0",
        "alan wake": "0",
        "control": "870780",
        "max payne": "0",
        "l.a. noire": "0",
        "bully": "0",
        "manhunt": "0",
        "midnight club": "0",
        "red dead": "1174180",
        "la noire": "0",
    }

    for key, app_id in known_games.items():
        if key in clean and app_id != "0":
            return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"

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

    # Try known Steam games first
    cover_url = fetch_steam_direct(title)

    # Try DuckDuckGo
    if not cover_url:
        cover_url = fetch_ddg_image(title)

    if cover_url and download_cover(cover_url, game_id):
        return game_id, True, cover_url

    return game_id, False, None


def main():
    print("Loading catalog...")
    with open(CATALOG, "rb") as f:
        games = json.loads(f.read().decode("utf-8"))

    games_without_covers = []
    for g in games:
        game_id = g.get("id", slugify(g.get("title", "")))
        if not cover_exists(game_id):
            games_without_covers.append(g)

    print(f"Games without covers: {len(games_without_covers)}")

    success = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_and_download, game): game for game in games_without_covers}

        for i, future in enumerate(as_completed(futures), 1):
            game_id, ok, url = future.result()
            if ok:
                if url != "exists":
                    success += 1
                    print(f"  + {game_id}")
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
