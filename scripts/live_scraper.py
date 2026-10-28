#!/usr/bin/env python3
"""Live catalog updater -- pulls real cracks from every reachable repacker feed.

For each source we try several candidate URLs until one answers over plain
HTTP. Feed items become catalog entries when their title is not already in
data/games.json, so re-running only ever ADDS what has genuinely dropped
newly. Everything else (gradients, genres, sizes) is derived from the feed.

Also fetches actual game cover images from SteamGridDB and other sources.

Usage:
    python scripts/live_scraper.py            # update data/games.json in place
    python scripts/live_scraper.py --dry-run  # show what would be added
"""

import json
import os
import re
import sys
import html
import time
import subprocess
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "data", "games.json")

# name -> list of candidate URLs tried in order; first success wins.
# Working sources as of 2026-10-29 (includes mirrors for blocked sites)
SOURCES = {
    "DODI": [
        "https://dodi-repacks.site/feed/",
        "https://www.dodi-repacks.site/feed/",
        "https://dodi-repacks.site/rss.xml",
    ],
    "FitGirl": [
        "https://www.fitgirl-repacks.site/feed/",
        "https://fitgirl-repacks.site/feed/",
    ],
    "SKIDROW": ["http://feeds.feedburner.com/SkidrowReloadedGames", "https://www.skidrowrepacks.com/"],
    "ElAmigos": ["https://www.elenemigos.com/sitemap-recent.xml", "https://www.elenemigos.com/sitemap-games-1.xml"],
    "Ocean of Games": ["https://oceanofgames.com/feed/"],
    # CODEX mirrors - working domains found via web search
    "CODEX": [
        "https://codexgames.com/feed/",
        "https://codexgames.net/feed/",
        "https://codex-reloaded.com/feed/",
        "https://codexscene.org/feed/",
    ],
    # RELOADED mirrors
    "RELOADED": [
        "https://reloaded-games.com/feed/",
        "https://reloadedgames.net/feed/",
        "https://rlsbb.com/feed/",
        "https://reloadedscene.org/feed/",
    ],
    # TOKYO mirrors
    "TOKYO": [
        "https://tokyo-repacks.com/feed/",
        "https://tokyogames.org/feed/",
        "https://tokyo-reloaded.net/feed/",
    ],
    # NINTENDO CAVE mirrors
    "NINTENDO CAVE": [
        "https://nintendocave.com/feed/",
        "https://nintendocave.net/feed/",
        "https://nintendocave.org/feed/",
    ],
    # Additional sources via APIs
    "The Pirate Bay": ["https://apibay.org/q.php?q=repack&cat=101"],
}

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TIMEOUT = 15

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

# SteamGridDB API for game covers
STEAMGRIDDB_API = "https://www.steamgriddb.com/api/v2"

# Browser-based scraping for sites that block plain HTTP
def scrape_steamrip():
    """Scrape SteamRIP using browser MCP via Playwright."""
    items = []
    try:
        # Use a Python script with Playwright to scrape
        script = '''
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://steamrip.com/", wait_until="domcontentloaded")

        articles = await page.query_selector_all("article, .post, .entry")
        results = []
        for a in articles:
            title_el = await a.query_selector("h1, h2, h3, .title, .entry-title, .post-title")
            link_el = await a.query_selector("a")
            img_el = await a.query_selector("img")
            if title_el:
                title = await title_el.inner_text()
                link = await link_el.get_attribute("href") if link_el else ""
                image = await img_el.get_attribute("src") if img_el else ""
                results.append({"title": title.strip(), "link": link, "image": image})
        await browser.close()
        import json
        print(json.dumps(results))

asyncio.run(scrape())
'''
        result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout.strip())
            for entry in data:
                title = entry.get("title", "")
                link = entry.get("link", "")
                image = entry.get("image", "")
                if title and "Free Download" in title:
                    # Extract clean title and size
                    clean = title.replace("Free Download", "").strip()
                    # Remove leading date/size like "2026 | 389 MB\n"
                    clean = re.sub(r"^\d{4}\s*\|\s*[\d.]+\s*(?:GB|MB)\s*\n", "", clean)
                    items.append((clean, link, "", f"SteamRIP: {clean}", image))
            print(f"  SteamRIP: {len(items)} items via browser")
    except Exception as e:
        print(f"  SteamRIP: browser scrape -> {type(e).__name__}: {e}", file=sys.stderr)
    return "SteamRIP", items


def scrape_fitgirl():
    """Scrape FitGirl using browser MCP."""
    items = []
    try:
        script = '''
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://fitgirl-repacks.site/", wait_until="domcontentloaded")

        articles = await page.query_selector_all("article, .post, .entry")
        results = []
        for a in articles:
            title_el = await a.query_selector("h1, h2, h3, .title, .entry-title, .post-title")
            link_el = await a.query_selector("a")
            img_el = await a.query_selector("img")
            if title_el:
                title = await title_el.inner_text()
                link = await link_el.get_attribute("href") if link_el else ""
                image = await img_el.get_attribute("src") if img_el else ""
                results.append({"title": title.strip(), "link": link, "image": image})
        await browser.close()
        import json
        print(json.dumps(results))

asyncio.run(scrape())
'''
        result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout.strip())
            for entry in data:
                title = entry.get("title", "")
                link = entry.get("link", "")
                image = entry.get("image", "")
                # Skip non-game entries
                if title and not any(x in title.lower() for x in ["upcoming", "updates digest", "important messages", "category/"]):
                    items.append((title, link, "", f"FitGirl: {title}", image))
            print(f"  FitGirl: {len(items)} items via browser")
    except Exception as e:
        print(f"  FitGirl: browser scrape -> {type(e).__name__}: {e}", file=sys.stderr)
    return "FitGirl", items


def scrape_dodi():
    """Scrape DODI using browser MCP."""
    items = []
    try:
        script = '''
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://dodi-repacks.site/", wait_until="domcontentloaded")

        articles = await page.query_selector_all("article, .post, .entry")
        results = []
        for a in articles:
            title_el = await a.query_selector("h1, h2, h3, .title, .entry-title, .post-title")
            link_el = await a.query_selector("a")
            img_el = await a.query_selector("img")
            if title_el:
                title = await title_el.inner_text()
                link = await link_el.get_attribute("href") if link_el else ""
                image = await img_el.get_attribute("src") if img_el else ""
                results.append({"title": title.strip(), "link": link, "image": image})
        await browser.close()
        import json
        print(json.dumps(results))

asyncio.run(scrape())
'''
        result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout.strip())
            for entry in data:
                title = entry.get("title", "")
                link = entry.get("link", "")
                image = entry.get("image", "")
                # Only keep actual game repacks (have version numbers and GB/MB)
                if title and re.search(r"v\d+\.\d+|GB|MB", title) and "repack" in title.lower():
                    items.append((title, link, "", f"DODI: {title}", image))
            print(f"  DODI: {len(items)} items via browser")
    except Exception as e:
        print(f"  DODI: browser scrape -> {type(e).__name__}: {e}", file=sys.stderr)
    return "DODI", items


def scrape_codex():
    """Scrape CODEX using browser MCP (blocked by Cloudflare on plain HTTP)."""
    items = []
    try:
        script = '''
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://codex-team.org/", wait_until="domcontentloaded", timeout=60000)

        articles = await page.query_selector_all("article, .post, .entry, .game-item")
        results = []
        for a in articles:
            title_el = await a.query_selector("h1, h2, h3, .title, .entry-title, .post-title, .game-title")
            link_el = await a.query_selector("a")
            img_el = await a.query_selector("img")
            if title_el:
                title = await title_el.inner_text()
                link = await link_el.get_attribute("href") if link_el else ""
                image = await img_el.get_attribute("src") if img_el else ""
                results.append({"title": title.strip(), "link": link, "image": image})
        await browser.close()
        import json
        print(json.dumps(results))

asyncio.run(scrape())
'''
        result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=90)
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout.strip())
            for entry in data:
                title = entry.get("title", "")
                link = entry.get("link", "")
                image = entry.get("image", "")
                if title and len(title) > 5:
                    items.append((title, link, "", f"CODEX: {title}", image))
            print(f"  CODEX: {len(items)} items via browser")
    except Exception as e:
        print(f"  CODEX: browser scrape -> {type(e).__name__}: {e}", file=sys.stderr)
    return "CODEX", items


def scrape_reloaded():
    """Scrape RELOADED using browser MCP (blocked by Cloudflare on plain HTTP)."""
    items = []
    try:
        script = '''
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://reloaded-games.net/", wait_until="domcontentloaded", timeout=60000)

        articles = await page.query_selector_all("article, .post, .entry, .game-item")
        results = []
        for a in articles:
            title_el = await a.query_selector("h1, h2, h3, .title, .entry-title, .post-title, .game-title")
            link_el = await a.query_selector("a")
            img_el = await a.query_selector("img")
            if title_el:
                title = await title_el.inner_text()
                link = await link_el.get_attribute("href") if link_el else ""
                image = await img_el.get_attribute("src") if img_el else ""
                results.append({"title": title.strip(), "link": link, "image": image})
        await browser.close()
        import json
        print(json.dumps(results))

asyncio.run(scrape())
'''
        result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=90)
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout.strip())
            for entry in data:
                title = entry.get("title", "")
                link = entry.get("link", "")
                image = entry.get("image", "")
                if title and len(title) > 5:
                    items.append((title, link, "", f"RELOADED: {title}", image))
            print(f"  RELOADED: {len(items)} items via browser")
    except Exception as e:
        print(f"  RELOADED: browser scrape -> {type(e).__name__}: {e}", file=sys.stderr)
    return "RELOADED", items


def scrape_elamigos():
    """Scrape ElAmigos using browser MCP (blocked by Cloudflare on plain HTTP)."""
    items = []
    try:
        script = '''
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://elenemigos.com/", wait_until="domcontentloaded", timeout=60000)

        # Get all /app/ links which are the game pages
        links = await page.query_selector_all('a[href*="/app/"]')
        results = []
        for link in links:
            href = await link.get_attribute("href")
            text = await link.inner_text()
            if href and len(text.strip()) > 3:
                clean = text.strip().replace("PC", "").strip()
                # Remove ranking markers like #1 TOP
                import re
                clean = re.sub(r"#\d+\s+TOP\s*", "", clean).strip()
                if len(clean) > 3:
                    results.append({"title": clean, "link": href, "image": ""})
        await browser.close()
        import json
        print(json.dumps(results))

asyncio.run(scrape())
'''
        result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=90)
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout.strip())
            for entry in data:
                title = entry.get("title", "")
                link = entry.get("link", "")
                image = entry.get("image", "")
                if title and len(title) > 5:
                    items.append((title, link, "", f"ElAmigos: {title}", image))
            print(f"  ElAmigos: {len(items)} items via browser")
    except Exception as e:
        print(f"  ElAmigos: browser scrape -> {type(e).__name__}: {e}", file=sys.stderr)
    return "ElAmigos", items


def scrape_tokyo():
    """Scrape TOKYO using browser MCP (blocked by DNS/Cloudflare on plain HTTP)."""
    items = []
    try:
        script = '''
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://tokyobrothers.com/", wait_until="domcontentloaded", timeout=60000)

        articles = await page.query_selector_all("article, .post, .entry, .game-item")
        results = []
        for a in articles:
            title_el = await a.query_selector("h1, h2, h3, .title, .entry-title, .post-title, .game-title")
            link_el = await a.query_selector("a")
            img_el = await a.query_selector("img")
            if title_el:
                title = await title_el.inner_text()
                link = await link_el.get_attribute("href") if link_el else ""
                image = await img_el.get_attribute("src") if img_el else ""
                results.append({"title": title.strip(), "link": link, "image": image})
        await browser.close()
        import json
        print(json.dumps(results))

asyncio.run(scrape())
'''
        result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=90)
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout.strip())
            for entry in data:
                title = entry.get("title", "")
                link = entry.get("link", "")
                image = entry.get("image", "")
                if title and len(title) > 5:
                    items.append((title, link, "", f"TOKYO: {title}", image))
            print(f"  TOKYO: {len(items)} items via browser")
    except Exception as e:
        print(f"  TOKYO: browser scrape -> {type(e).__name__}: {e}", file=sys.stderr)
    return "TOKYO", items


def scrape_nintendocave():
    """Scrape NINTENDO CAVE using browser MCP (blocked by DNS/Cloudflare on plain HTTP)."""
    items = []
    try:
        script = '''
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://nintendocave.io/", wait_until="domcontentloaded", timeout=60000)

        articles = await page.query_selector_all("article, .post, .entry, .game-item")
        results = []
        for a in articles:
            title_el = await a.query_selector("h1, h2, h3, .title, .entry-title, .post-title, .game-title")
            link_el = await a.query_selector("a")
            img_el = await a.query_selector("img")
            if title_el:
                title = await title_el.inner_text()
                link = await link_el.get_attribute("href") if link_el else ""
                image = await img_el.get_attribute("src") if img_el else ""
                results.append({"title": title.strip(), "link": link, "image": image})
        await browser.close()
        import json
        print(json.dumps(results))

asyncio.run(scrape())
'''
        result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=90)
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout.strip())
            for entry in data:
                title = entry.get("title", "")
                link = entry.get("link", "")
                image = entry.get("image", "")
                if title and len(title) > 5:
                    items.append((title, link, "", f"NINTENDO CAVE: {title}", image))
            print(f"  NINTENDO CAVE: {len(items)} items via browser")
    except Exception as e:
        print(f"  NINTENDO CAVE: browser scrape -> {type(e).__name__}: {e}", file=sys.stderr)
    return "NINTENDO CAVE", items


def scrape_1337x_games():
    """Scrape 1337x Games category using Playwright (Cloudflare protected)."""
    items = []
    try:
        script = '''
import asyncio
from playwright.async_api import async_playwright
import json

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to games category page 1
        await page.goto("https://1337x.to/search/games/1/",
                       wait_until="domcontentloaded", timeout=90000)

        # Wait for Cloudflare challenge to complete and table to load
        await page.wait_for_selector("table.torrent-list tbody tr", timeout=60000)

        # Extract torrent rows
        rows = await page.query_selector_all("table.torrent-list tbody tr")
        results = []
        for row in rows:
            # Columns: Name, Uploaded, Size, Seeders, Leechers
            name_cell = await row.query_selector("td.name a[href^='/torrent/']")
            seeders_cell = await row.query_selector("td.seeds")
            leechers_cell = await row.query_selector("td.leeches")
            size_cell = await row.query_selector("td.size")
            date_cell = await row.query_selector("td.coll-date")

            if name_cell:
                name = await name_cell.inner_text()
                link = await name_cell.get_attribute("href")
                seeders = await seeders_cell.inner_text() if seeders_cell else "0"
                leechers = await leechers_cell.inner_text() if leechers_cell else "0"
                size = await size_cell.inner_text() if size_cell else ""
                date = await date_cell.inner_text() if date_cell else ""
                results.append({
                    "title": name.strip(),
                    "link": f"https://1337x.to{link}" if link else "",
                    "seeders": seeders.strip(),
                    "leechers": leechers.strip(),
                    "size": size.strip(),
                    "date": date.strip()
                })

        await browser.close()
        print(json.dumps(results))

asyncio.run(scrape())
'''
        result = subprocess.run(["python", "-c", script], capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout.strip())
            for entry in data:
                title = entry.get("title", "")
                link = entry.get("link", "")
                if title and len(title) > 5:
                    desc = f"1337x: {title} (S:{entry.get('seeders')} L:{entry.get('leechers')} Size:{entry.get('size')})"
                    items.append((title, link, entry.get("date", ""), desc, ""))
            print(f"  1337x: {len(items)} items via browser")
    except Exception as e:
        print(f"  1337x: browser scrape -> {type(e).__name__}: {e}", file=sys.stderr)
    return "1337x", items


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


def parse_sitemap(xml_bytes):
    """Yield (title, link, date_str, description) from XML sitemap.

    Extracts game titles from URLs like:
    https://www.elenemigos.com/app/game-name-descargar-gratis/12345
    """
    soup = BeautifulSoup(xml_bytes, "xml")
    for url_el in soup.find_all("url"):
        loc = url_el.find("loc")
        lastmod = url_el.find("lastmod")
        link = loc.get_text(strip=True) if loc is not None else ""
        date_s = lastmod.get_text(strip=True) if lastmod is not None else ""
        if not link:
            continue
        # Extract title from URL path
        # Pattern: /app/game-name-descargar-gratis/12345
        m = re.search(r"/app/([^/]+)/\d+", link)
        if m:
            title = m.group(1).replace("-descargar-gratis", "").replace("-", " ").strip()
            # Clean up title casing
            title = re.sub(r"\b(\w+)\b", lambda x: x.group(1).capitalize(), title)
            yield title, link, date_s, ""


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


def fetch_tpb_games():
    """Fetch game torrents from The Pirate Bay via apibay.org API."""
    items = []
    try:
        # Expanded query list for better game coverage
        queries = [
            # Repacker-specific (current)
            ("fitgirl repack", 101),
            ("dodi repack", 101),
            ("elamigos repack", 101),
            # Broader game searches
            ("repack game", 101),
            ("cracked game", 101),
            ("fitgirl", 101),
            ("dodi", 101),
            ("codex game", 101),
            ("skidrow game", 101),
            ("v2024 repack", 101),
            ("v2025 repack", 101),
            ("update repack", 101),
        ]
        seen_hashes = set()
        for query, cat in queries:
            r = requests.get(f"https://apibay.org/q.php?q={quote_plus(query)}&cat={cat}", headers=UA, timeout=TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                for entry in data[:30]:  # Increase from 20
                    name = entry.get("name", "")
                    info_hash = entry.get("info_hash", "")
                    if not name or not info_hash or info_hash in seen_hashes:
                        continue
                    low = name.lower()
                    # Must be game-related (filter out music/soundtracks)
                    game_indicators = [
                        "repack", "crack", "fitgirl", "dodi", "elamigos",
                        "codex", "skidrow", "reloaded", "cpy", "rld", "emu"
                    ]
                    if not any(x in low for x in game_indicators):
                        continue
                    # Skip music/audio
                    if any(x in low for x in ["music", "album", "flac", "mp3", "cd ",
                        "vinyl", "remaster", "single", "ep ", "lp ", "discography",
                        "soundtrack", "ost ", "remix", "dj ", "beat ", "instrumental",
                        "song ", "track ", "feat.", "ft.", "vs.", "radio", "score"]):
                        continue
                    seen_hashes.add(info_hash)
                    magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={quote_plus(name)}"
                    # Add common trackers
                    magnet += "&tr=udp://tracker.opentrackr.org:1337/announce"
                    magnet += "&tr=udp://open.tracker.cl:1337/announce"
                    magnet += "&tr=udp://tracker.torrent.eu.org:451/announce"
                    items.append((name, magnet, "", f"TPB: {name}"))
        print(f"  The Pirate Bay: {len(items)} items via apibay.org")
    except Exception as e:
        print(f"  The Pirate Bay: apibay.org -> {type(e).__name__}", file=sys.stderr)
    return "The Pirate Bay", items


def fetch_steamgriddb_cover(title):
    """Try to fetch a game cover from SteamGridDB. Returns image URL or None."""
    try:
        # Search for the game
        search_url = f"{STEAMGRIDDB_API}/search/autocomplete/{quote_plus(title)}"
        r = requests.get(search_url, headers=UA, timeout=10)
        if r.status_code == 200:
            results = r.json()
            if results.get("data"):
                game_id = results["data"][0].get("id")
                if game_id:
                    # Get grids (covers)
                    grids_url = f"{STEAMGRIDDB_API}/grids/game/{game_id}"
                    r2 = requests.get(grids_url, headers=UA, timeout=10)
                    if r2.status_code == 200:
                        grids = r2.json()
                        if grids.get("data"):
                            # Return the first grid URL
                            return grids["data"][0].get("url")
    except Exception:
        pass
    return None


def fetch_source(name, urls):
    """Return list of feed items from the first URL that answers."""
    for url in urls:
        try:
            r = requests.get(url, headers=UA, timeout=TIMEOUT)
            if r.status_code == 200:
                content = r.content
                # Try RSS/Atom first
                if b"<item>" in content or b"<entry>" in content:
                    items = [it for it in parse_items(content)]
                    print(f"  {name}: {len(items)} items via {url}")
                    return name, items
                # Try sitemap (for ElAmigos)
                elif b"<urlset" in content or b"<sitemapindex" in content:
                    items = [it for it in parse_sitemap(content)]
                    print(f"  {name}: {len(items)} items via {url} (sitemap)")
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

    def add_entry(raw_title, link, date_s, desc, source, cover_url=None):
        title = clean_title(raw_title)
        key = norm_title(title)
        if key in seen:
            return
        seen.add(key)
        dt = parse_date(date_s) if date_s else datetime.now(timezone.utc)
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
            "imageUrl": cover_url or "",
            "repack": None,
            "sources": [source],
            "feedUrl": link,
        }
        new_games.append(entry)
        print(f"  + [{source}] {entry['title']}")

    # Browser-based sources first (they carry real cover images).
    for scraper in (scrape_steamrip, scrape_fitgirl, scrape_dodi, scrape_codex, scrape_reloaded, scrape_elamigos, scrape_tokyo, scrape_nintendocave, scrape_1337x_games):
        source, items = scraper()
        if items:
            live_sources.append(source)
        for raw_title, link, date_s, desc, image in items:
            add_entry(raw_title, link, date_s, desc, source, cover_url=image)

    # Newest cracks first: process sources, keep only titles not already held.
    for source, urls in SOURCES.items():
        _, items = fetch_source(source, urls)
        if items:
            live_sources.append(source)
        for raw_title, link, date_s, desc in items:
            add_entry(raw_title, link, date_s, desc, source,
                      cover_url=fetch_steamgriddb_cover(clean_title(raw_title)))

    # Also fetch from The Pirate Bay via apibay
    _, tpb_items = fetch_tpb_games()
    if tpb_items:
        live_sources.append("The Pirate Bay")
    for raw_title, link, date_s, desc in tpb_items:
        title = clean_title(raw_title)
        # Sanitize for console output
        safe_title = title.encode('ascii', 'replace').decode('ascii')
        key = norm_title(title)
        if key in seen:
            continue
        seen.add(key)
        dt = datetime.now(timezone.utc)
        age_days = 0
        genre, label = guess_genre(title)
        size = "Unknown"
        cover_url = fetch_steamgriddb_cover(title)
        entry = {
            "id": slugify(title),
            "title": title,
            "genre": genre,
            "genreLabel": label,
            "description": desc[:160] + "..." if len(desc) > 160 else desc,
            "crackedBy": "TPB",
            "crackedDate": dt.strftime("%Y-%m-%d"),
            "uploadedDate": dt.strftime("%Y-%m-%d"),
            "size": size,
            "sizeBytes": 0,
            "version": "",
            "isUpcoming": False,
            "isJustDropped": True,
            "isLatest": True,
            "rating": 4.0,
            "tags": [genre],
            "imageGradient": GRADIENTS[abs(hash(title)) % len(GRADIENTS)][0],
            "imageUrl": cover_url or "",
            "repack": None,
            "sources": ["The Pirate Bay"],
            "feedUrl": link,
        }
        new_games.append(entry)
        print(f"  + [TPB] {safe_title}")

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
