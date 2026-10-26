# Booty Catalog ⚓

The ultimate pirate game catalog application. Browse, search, filter, and "one-click download" the latest cracked games from all major repacker sources — FitGirl, DODI, CODEX, RELOADED, SKIDROW, ElAmigos, and more.

## Features

### Web App (`index.html`)
- **Dark/Light Theme** — Toggle between shadow and daylight mode
- **Browse Library** — Scroll through 40+ games sorted by newest, rating, or size
- **Just Dropped Banner** — Hero section showcasing the latest cracks (within 30 days)
- **Advanced Search** — Instant search across game titles, genres, crack sources, tags, and descriptions
- **Category Filters** — Filter by RPG, Action, Adventure, Simulation, Strategy, Mecha, Survival
- **Repacker Source Filters** — Filter games by specific repacker distribution source
- **One-Click Download Panel** — Animated multi-phase download flow with progress tracking
- **Install Folder Picker** — Configure where pirated copies go
- **Grid/List/Compact/Big View Modes** — Toggle between 4 layout styles
- **Toast Notifications** — Action confirmations and status messages
- **Responsive Design** — Works on desktop and mobile

### Flet Desktop GUI (`main.py`)
- **Python GUI** — Native desktop application using Flet framework
- **Game Browsing** — Same catalog with Flet-native widgets
- **Category & Repacker Filtering** — Full filtering support in desktop UI
- **Animated Download Dialog** — Multi-phase progress simulation

- **Theme Toggle** — Light/dark mode switching
- **Install Folder Configuration** — Set custom installation path

### Scraper Module (`scripts/scraper.py`)
- **Repacker Source Tracking** — Configured configs for 12+ distribution sources
- **Game Catalog Aggregation** — Load and manage games.json
- **Repacker Source Lookup** — Filter games by FitGirl, DODI, CODEX, etc.
- **Latest Crack Monitoring** — Filter by recently cracked games
- **Search Across Sources** — Search by title, genre, tag, crack source
- **Catalog Statistics** — Total games, ratings, total download size, top repackers
- **Scrape Simulation** — Simulate scraping across all configured sources

## Repacker Sources

| Source | Icon | Trust Level | Compression | URL |
|--------|------|-------------|-------------|-----|
| FitGirl | 📦 | 95% | ~60% | fitgirl-downloads.com |
| DODI | 📁 | 92% | ~50% | dodi-repacks.site |
| CODEX | 🔓 | 90% | 100% | codex-squad.com |
| RELOADED | ⚙️ | 93% | 100% | reloaded.io |
| SKIDROW | 🎩 | 88% | ~70% | skidrowrepacks.com |
| ElAmigos | 🎭 | 85% | 100% | elamigos.com |
| TOKYO | 🗾 | 87% | ~80% | tokyobrothers.com |
| OiGi | 📖 | 91% | ~75% | oigi.org |
| TEAM-OUT | 🌀 | 86% | ~70% | team-out.org |
| INDIE-CRACK | 🎪 | 82% | 100% | indie-crack.net |
| NINTEN-CAVE | 🍄 | 80% | 100% | ninten-cave.io |
| CRACKED.IO | 💎 | 78% | 100% | cracked.io |

## Project Structure

```
pirate-catalog/
├── index.html          # Web app main page
├── styles/
│   └── app.css         # Full CSS (dark/light themes, 4 view modes, animations)
├── scripts/
│   ├── app.js          # Main app logic (filter, search, sort, render)
│   ├── download.js     # Download simulation (multi-phase progress)
│   └── scraper.py      # Repacker source scraper (Python)
├── data/
│   └── games.json      # Game catalog (40+ entries)
├── main.py             # Flet desktop GUI
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Installation & Usage

### Web App (no dependencies)
1. Open `index.html` in a browser
2. Browse games, filter by category or repacker source
3. Click any game to open the download panel
4. Hit "One-Click Download & Install"

### Desktop GUI (requires Python)
```bash
pip install -r requirements.txt
python main.py
```

### Scraper CLI
```bash
python scripts/scraper.py
# Or with custom games.json path:
python scripts/scraper.py /path/to/games.json
```

## Running the Web App

Simply open `index.html` in any modern browser. No build step, no npm, no server required. The app reads `data/games.json` directly.

For a local server experience:
```bash
python -m http.server 8080
# Then open http://localhost:8080
```

## Game Catalog

Contains **40+ games** including:
- Latest AAA cracks (Cyberpunk 2077, Elden Ring, GTA VI, etc.)
- Repacker versions with compressed sizes
- Upcoming/beta cracks (GTA VI in progress)
- Indie gems (Balatro, Hollow Knight, etc.)
- Cross-platform (PC, Switch ROM)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Web UI | Vanilla HTML/CSS/JS (zero dependencies) |
| Desktop GUI | Python + Flet |
| Data | JSON catalog with structured game metadata |
| Scraper | Python 3.9+ |

## Future Ideas

- [ ] Real web scraping from repacker sites
- [ ] RSS feed integration for new cracks
- [ ] Auto-update game catalog
- [ ] Community ratings & reviews
- [ ] Export/download list
- [ ] Integration with actual torrent APIs
- [ ] Push notifications for new cracks

---

**Booty Catalog v1.0** — Every game, every repacker, every crack. ⚓
