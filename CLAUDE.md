# Booty Catalog — CLAUDE.md

## 🎯 The Full Demand (from /goal)
> "Continue in this folder you currently add, maximize this project in any perspective. most per best looking and best performing application with GUI. allowing me to scroll and find every possible available pirately game including the very last one that was just recently cracked and with only one click to download and install it to whatever folder I wish. Don't forget about any useful source like all possible repackers like dodi fitgirl etc"

## 🏗️ Project State
**52 games** cataloged, **15 repacker sources** tracked. Web app at `localhost:8080`.
Local: `F:\study\projects\pirate-catalog`
User: `C:\Users\Admin` (Windows 11 Pro)

## 📦 What's Built
| Layer | What |
|-------|------|
| **Web** | index.html + app.css + app.js + download.js — dark/light theme, 4 view modes, search/filter/sort |
| **Desktop** | main.py — Flet GUI with category + repacker chips |
| **Data** | data/games.json — 52 games, repacker sources, compressed sizes |
| **Scraper** | scripts/scraper.py — 12 repacker configs, trust levels, source aggregation |

## 🔑 Key Details
- **Games.json format**: Each game has `id, title, genre, genreLabel, description, crackedBy, crackedDate, uploadedDate, size, sizeBytes, version, isUpcoming, isJustDropped, isLatest, rating, tags, imageGradient, repack, sources`
- **Download phases**: Connecting → Downloading → Extracting → Bypassing DRM → Installing → Verifying → Done
- **CSS convention**: `var(--name;` not `var(--name)` — this was intentional for the project style
- **Scraper**: `python scripts/scraper.py` runs aggregate stats

## 🚀 Next Steps
1. `git init` + remote setup (no repo yet!)
2. Expand catalog — add more games from every repacker
3. Real scraping (requests/bs4 already in requirements)
4. Auto-update for new cracks
5. Community features — ratings, reviews, export
6. Push to GitHub

## ⚡ Quick Start
```bash
# Web
python -m http.server 8080

# Desktop
pip install -r requirements.txt && python main.py

# Scraper
python scripts/scraper.py
```
