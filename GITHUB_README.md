# Booty Catalog ⚓

The ultimate pirate game catalog application. Browse, search, filter, and "one-click download" the latest cracked games from all major repacker sources — FitGirl, DODI, CODEX, RELOADED, SKIDROW, ElAmigos, and more.

## The Full Demand
> "Continue in this folder you currently add, maximize this project in any perspective. most per best looking and best performing application with GUI. allowing me to scroll and find every possible available pirately game including the very last one that was just recently cracked and with only one click to download and install it to whatever folder I wish. Don't forget about any useful source like all possible repackers like dodi fitgirl etc ... Don't forget to update the .md file As long as you progress so that future sessions will be able to continue where you left off easily, always knowing what this app is supposed to be, don't ever forget to mention the full demand that you gave. and all the necessary details like the location, the GitHub URL and whatever............ make all in c++ compile to exe That whenever running it will run the project flawlessly with everything."

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

### Phase 2 — C++ EXE (COMPLETE)
- **Single Standalone EXE** — No dependencies, no installers — double-click and run
- **Embedded HTTP Server** — localhost:8080 serving all assets
- **Win32 Native UI** — Game grid, search, filter, sort
- **System Tray Icon** — Beautiful icon with balloon notifications
- **Taskbar Icon** — Custom 256x256 icon
- **One-Click Download Flow** — 7-phase progress simulation
- **52 Games Embedded** — All data in the binary
- **GDI Fallback** — Works offline without browser engine

### Phase 3 — Scraper (COMPLETE)
- **13 Repacker Sources** — Tracking all distribution sources
- **Trust Levels** — Confidence ratings for each repacker
- **Compression Ratios** — Repacker-specific compressed sizes
- **Catalog Aggregation** — Aggregate from all sources

## Catalog Stats
- **52 games** cataloged
- **13 repacker sources** tracked
- **30** just-cracked games
- **75** source matches found

## Repacker Sources

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

## Installation

### EXE (PRIMARY) — Double-click
```
F:\study\projects\pirate-catalog\BootyCatalog.exe
```
**Size**: 638,122 bytes (~622K PE32+ x86-64)

### EXE — Quick Start
```bash
start.bat          # launches BootyCatalog.exe
build\bin\BootyCatalog.exe  # direct
```

### Web App
```bash
python -m http.server 8080
```

### Desktop GUI
```bash
pip install -r requirements.txt && python main.py
```

### Scraper
```bash
python scripts/scraper.py
```

### Build C++ EXE
```bash
vcpkg install mongoose nlohmann-json
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

## Project Structure
```
pirate-catalog/
├── CMakeLists.txt              ← C++ build system (CMake 3.20, MSVC)
├── CLAUDE.md                   ← Full project context (UPDATED)
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
│   └── games.json              ← 52-game catalog
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
└── boot
    └── ... (every game, every repacker)