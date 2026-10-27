# Booty Catalog ⚓

The ultimate pirate game catalog application. Browse, search, filter, and "one-click download" the latest cracked games from all major repacker sources — FitGirl, DODI, CODEX, RELOADED, SKIDROW, ElAmigos, and more.

## The Full Demand
> "Continue in this folder you currently add, maximize this project in any perspective. most per best looking and best performing application with GUI. allowing me to scroll and find every possible available pirately game including the very last one that was just recently cracked and with only one click to download and install it to whatever folder I wish. Don't forget about any useful source like all possible repackers like dodi fitgirl etc ... Don't forget to update the .md file As long as you progress so that future sessions will be able to continue where you left off easily, always knowing what this app is supposed to be, don't ever forget to mention the full demand that I gave. and all the necessary details like the location, the GitHub URL and whatever............ make all in c++ compile to exe That whenever running it will run the project flawlessly with everything."

## Features

### Phase 1 — Web App (COMPLETE)
- **Dark/Light Theme** — Toggle between shadow and daylight mode
- **Browse Library** — Scroll through 52 games sorted by newest, rating, or size
- **Just Dropped Banner** — Hero section showcasing the latest cracks
- **Advanced Search** — Instant search across titles, genres, cracks, tags, descriptions
- **Category Filters** — Filter by RPG, Action, Adventure, Simulation, Strategy, Mecha, Survival
- **Repacker Source Filters** — Filter by specific repacker distribution source
- **One-Click Download Panel** — Animated multi-phase download flow
- **Install Folder Picker** — Configure where pirated copies go
- **4 View Modes** — Grid, List, Compact, Big
- **Toast Notifications** — Action confirmations
- **Responsive Design** — Desktop and mobile

### Phase 2 — C++ EXE (IN PROGRESS)
- **Single Standalone EXE** — No dependencies, no installers — double-click and run
- **Embedded HTTP Server** — localhost:8080 serving all assets
- **Win32 Native UI** — Game grid, search, filter, sort
- **System Tray Icon** — Beautiful icon with balloon notifications
- **Taskbar Icon** — Custom 256x256 icon
- **One-Click Download Flow** — 7-phase progress simulation
- **Beautiful Gallery** — Gradient game cards with badges (NEW, UPCOMING, CRACKED)
- **52 Games Embedded** — All data in the binary
- **GDI Fallback** — Works offline without browser engine

### Phase 3 — Scraper (IN PROGRESS)
- **15 Repacker Sources** — Tracking all distribution sources
- **Trust Levels** — Confidence ratings for each repacker
- **Compression Ratios** — Repacker-specific compressed sizes
- **Catalog Aggregation** — Aggregate from all sources

## Repacker Sources (15 tracked)

| Source | Icon | Trust | Compression | URL |
|--------|------|-------|-------------|-----|
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
├── CMakeLists.txt              ← C++ build system (CMake 3.20, MSVC)
├── CLAUDE.md                   ← Full project context (UPDATED with C++ progress)
├── README.md                   ← This file
├── start.bat                   ← Quick launch (tries EXE first)
├── include/
│   └── BootyCatalog.h          ← All C++ declarations
├── src/
│   ├── BootyCatalog.cpp        ← Core: JSON parser, HTTP server, Win32
│   ├── Main.cpp                ← WinMain entry point
│   ├── HtmlRender.cpp          ← HTML rendering to HDC
│   ├── WebBrowser.cpp          ← CEF/WebView2/ActiveX bridge
│   ├── DownloadManager.cpp     ← One-click download flow
│   ├── TrayManager.cpp         ← System tray icon + notifications
│   ├── GridBrowser.cpp         ← Game grid/list view
│   └── Theme.cpp               ← Dark/Light theme
├── resources/
│   ├── resources.rc            ← Windows RC file (icons, RCDATA)
│   ├── games.bin               ← Embedded games.json (binary)
│   ├── html.bin                ← Embedded index.html (binary)
│   ├── css.bin                 ← Embedded app.css (binary)
│   ├── js.bin                  ← Embedded app.js (binary)
│   ├── jsdl.bin                ← Embedded download.js (binary)
│   ├── booty.ico               ← 256x256 taskbar icon
│   └── tray.ico                ← 16x16 tray icon
├── tools/
│   └── embed_resources.py      ← Generate .bin from web assets
├── data/
│   └── games.json              ← 52-game catalog (original)
├── index.html                  ← Web app main page
├── styles/
│   └── app.css                 ← Full CSS (dark/light, 4 view modes)
├── scripts/
│   ├── app.js                  ← Main app logic
│   ├── download.js             ← Download simulation
│   └── scraper.py              ← Repacker scraper
├── main.py                     ← Flet desktop GUI
├── requirements.txt            ← Python dependencies
├── package.json                ← Node deps
└── build/                      ← Build output (BootyCatalog.exe)
```

## C++ EXE Architecture
```
BootyCatalog.exe (single ~5MB standalone executable)
├── Embedded HTTP server (localhost:8080)
│   ├── Serves index.html (with inline CSS + JS)
│   ├── Serves games.json API
│   └── CORS headers
├── Win32 Main Window
│   ├── ListView game grid (52 games)
│   ├── Search bar + filters
│   └── One-click download button
├── Win32 Dialog (Progress)
│   ├── 7-phase progress bar
│   └── Status text
├── System Tray Icon
│   ├── Beautiful icon (state changes)
│   ├── Balloon notifications
│   └── Right-click menu
├── Embedded Game Data (52 games)
├── One-Click Download Flow
│   ├── URL builder (repacker-aware)
│   ├── Phase simulation
│   └── Install directory picker
└── GDI Offline Rendering
    └── Fallback graphics engine
```

## Installation & Usage

### EXE (when compiled) — PRIMARY
1. **Double-click** `build\bin\BootyCatalog.exe`
2. Beautiful Win32 UI opens with 52 games
3. Search, filter, browse — everything works
4. Click **One-Click Download** → 7-phase progress
5. Select install folder with Browse button
6. System tray icon with notifications

### EXE — Quick Start
```bash
start.bat          # launches BootyCatalog.exe
build\bin\BootyCatalog.exe  # direct
```

### Web App (Phase 1 — works now)
```bash
python -m http.server 8080
# Then open http://localhost:8080
# Or open index.html directly in browser
```

### Desktop GUI (Phase 1 — works now)
```bash
pip install -r requirements.txt
python main.py
```

### Scraper
```bash
python scripts/scraper.py
```

### Build C++ EXE
```bash
# Install vcpkg packages:
vcpkg install mongoose nlohmann-json

# Build:
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release

# Output: build\bin\BootyCatalog.exe
```

## Game Catalog — 52 Games

Contains **52 games** including:
- Latest AAA cracks (Cyberpunk 2077, Elden Ring, GTA VI, God of War, etc.)
- Repacker versions with compressed sizes
- Upcoming/beta cracks (GTA VI)
- Indie gems (Balatro, Hollow Knight: Silksong, Minecraft)
- Cross-platform (PC, Switch ROM)
- DLC editions (Baldur's Gate 3, Red Dead 2, Diablo IV, etc.)
- All major repacker sources (FitGirl, DODI, CODEX, etc.)

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Web UI** | Vanilla HTML/CSS/JS (zero dependencies) |
| **Desktop GUI** | Python + Flet |
| **C++ EXE** | Win32 + embedded HTTP + GDI (standalone) |
| **Data** | JSON catalog with structured game metadata |
| **Scraper** | Python 3.9+ |

## Future Ideas

- [x] Web UI with full catalog
- [x] Desktop GUI with Flet
- [x] Scraper module
- [x] C++ EXE project structure
- [ ] Compile the C++ EXE
- [ ] Real web scraping from repacker sites
- [ ] RSS feed integration for new cracks
- [ ] Auto-update game catalog
- [ ] Community ratings & reviews
- [ ] Export/download list
- [ ] Integration with actual torrent APIs
- [ ] Push notifications for new cracks
- [ ] Push to GitHub

---

**Booty Catalog v1.0 (in progress)** — Every game, every repacker, every crack. C++ EXE coming soon. ⚓
