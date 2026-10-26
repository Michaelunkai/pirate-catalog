"""Booty Scraper — Aggregate cracked games from repacker sources.

Scans and tracks game catalogs across the major pirate and repacker distribution
networks. Keeps the catalog up-to-date with the latest cracks.
"""

import json
import os
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from pathlib import Path


# ── Repacker Sources ──
class RepackerSource(Enum):
    FITGIRL = "FitGirl"
    DODI = "DODI"
    CODEX = "CODEX"
    RELOADED = "RELOADED"
    SKIDROW = "SKIDROW"
    ELAMIGOS = "ElAmigos"
    TOKYO = "TOKYO"
    OIGI = "OiGi"
    TEAM_OUT = "TEAM-OUT"
    INDIE_CRACK = "INDIE-CRACK"
    NINTEN_CAVE = "NINTEN-CAVE"
    TOAD_64 = "TOAD-64"
    GOG = "GOG"
    CRACKED_IO = "CRACKED.IO"


@dataclass
class RepackerConfig:
    """Configuration for a repacker distribution source."""
    name: RepackerSource
    url: str
    icon: str
    trust_level: float  # 0.0 - 1.0
    size_ratio: float  # Original size / Repack size (lower = more compression)
    games_count: int = 0
    last_update: Optional[datetime] = None


# ── Repacker source configurations ──
REPACKER_SOURCES = {
    RepackerSource.FITGIRL: RepackerConfig(
        name=RepackerSource.FITGIRL,
        url="fitgirl-downloads.com",
        icon="📦",
        trust_level=0.95,
        size_ratio=0.6,
    ),
    RepackerSource.DODI: RepackerConfig(
        name=RepackerSource.DODI,
        url="dodi-repacks.site",
        icon="📁",
        trust_level=0.92,
        size_ratio=0.5,
    ),
    RepackerSource.CODEX: RepackerConfig(
        name=RepackerSource.CODEX,
        url="codex-squad.com",
        icon="🔓",
        trust_level=0.90,
        size_ratio=1.0,
    ),
    RepackerSource.RELOADED: RepackerConfig(
        name=RepackerSource.RELOADED,
        url="reloaded.io",
        icon="⚙️",
        trust_level=0.93,
        size_ratio=1.0,
    ),
    RepackerSource.SKIDROW: RepackerConfig(
        name=RepackerSource.SKIDROW,
        url="skidrowrepacks.com",
        icon="🎩",
        trust_level=0.88,
        size_ratio=0.7,
    ),
    RepackerSource.ELAMIGOS: RepackerConfig(
        name=RepackerSource.ELAMIGOS,
        url="elamigos.com",
        icon="🎭",
        trust_level=0.85,
        size_ratio=1.0,
    ),
    RepackerSource.TOKYO: RepackerConfig(
        name=RepackerSource.TOKYO,
        url="tokyobrothers.com",
        icon="🗾",
        trust_level=0.87,
        size_ratio=0.8,
    ),
    RepackerSource.OIGI: RepackerConfig(
        name=RepackerSource.OIGI,
        url="oigi.org",
        icon="📖",
        trust_level=0.91,
        size_ratio=0.75,
    ),
}


@dataclass
class CatalogEntry:
    """A single game entry in the pirate catalog."""
    id: str
    title: str
    genre: str
    genreLabel: str
    description: str
    crackedBy: str
    crackedDate: str
    uploadedDate: str
    size: str
    version: str
    isUpcoming: bool = False
    isJustDropped: bool = False
    rating: float = 0
    tags: list = field(default_factory=list)
    imageGradient: str = ""
    repack: Optional[dict] = None
    sources: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CatalogEntry":
        return cls(**data)


@dataclass
class ScraperResult:
    """Result of a scraper run."""
    timestamp: datetime
    games_found: int
    new_games: int
    updated_games: int
    sources_scraped: int
    errors: list = field(default_factory=list)
    summary: str = ""


class BootyScraper:
    """Aggregates game catalog data from repacker sources."""

    def __init__(self, games_path: Optional[str] = None):
        self.games_path = Path(games_path) if games_path else Path(__file__).parent.parent / "data" / "games.json"
        self.sources = REPACKER_SOURCES
        self._cache: dict = {}

    def load_games(self) -> list[dict]:
        """Load games from the JSON catalog file."""
        if self.games_path.exists():
            with open(self.games_path, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
        return self._cache

    def save_games(self, games: list[dict]) -> None:
        """Save games back to the JSON catalog file."""
        with open(self.games_path, "w", encoding="utf-8") as f:
            json.dump(games, f, indent=2, ensure_ascii=False)

    def get_repackers(self) -> list[RepackerConfig]:
        """Return all configured repacker sources."""
        return list(self.sources.values())

    def get_source_by_name(self, name: str) -> Optional[RepackerConfig]:
        """Look up a repacker config by display name."""
        for source in self.sources.values():
            if source.name.value.lower() == name.lower():
                return source
        return None

    def filter_by_repacker(self, games: list[dict], source_name: str) -> list[dict]:
        """Filter games by a specific repacker source."""
        source = self.get_source_by_name(source_name)
        if not source:
            return games
        return [
            g for g in games
            if source.name.value in (g.get("sources") or [])
        ]

    def get_latest_cracked(self, days: int = 30) -> list[dict]:
        """Get games cracked within the last N days."""
        games = self.load_games()
        cutoff = datetime.now() - timedelta(days=days)
        return [
            g for g in games
            if g.get("isJustDropped") and datetime.strptime(g["crackedDate"], "%Y-%m-%d") >= cutoff
        ]

    def get_upcoming(self) -> list[dict]:
        """Get upcoming games (beta cracks)."""
        games = self.load_games()
        return [g for g in games if g.get("isUpcoming")]

    def search_games(self, query: str, games: Optional[list[dict]] = None) -> list[dict]:
        """Search games by title, genre, crack source, or tags."""
        if games is None:
            games = self.load_games()
        query = query.lower()
        return [
            g for g in games
            if query in g["title"].lower()
            or query in g["genreLabel"].lower()
            or query in g["crackedBy"].lower()
            or any(query in tag.lower() for tag in g.get("tags", []))
            or query in g["description"].lower()
        ]

    def categorize_games(self, games: Optional[list[dict]] = None) -> dict[str, list[dict]]:
        """Group games by genre category."""
        if games is None:
            games = self.load_games()
        categories: dict[str, list[dict]] = {}
        for g in games:
            cat = g["genre"].capitalize()
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(g)
        return categories

    def get_stats(self, games: Optional[list[dict]] = None) -> dict:
        """Get catalog statistics."""
        if games is None:
            games = self.load_games()
        return {
            "total_games": len(games),
            "just_dropped": len([g for g in games if g.get("isJustDropped")]),
            "upcoming": len([g for g in games if g.get("isUpcoming")]),
            "avg_rating": sum(g.get("rating", 0) for g in games) / len(games) if games else 0,
            "total_size_gb": sum(
                float(g["size"].replace(" GB", "")) for g in games
            ) / 1024 if games else 0,
            "top_repackers": self._top_repackers(games),
        }

    def _top_repackers(self, games: list[dict]) -> dict[str, int]:
        """Count games by repacker source."""
        counts: dict[str, int] = {}
        for g in games:
            for source in g.get("sources", []):
                counts[source] = counts.get(source, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))

    def run_scrape(self) -> ScraperResult:
        """Run a scrape across all configured sources."""
        timestamp = datetime.now()
        games_found = 0
        new_games = 0
        updated_games = 0
        errors: list[str] = []
        sources_scraped = len(self.sources)

        for source in self.sources.values():
            try:
                # Simulate scraping from the source
                games_found += self._simulate_source(source)
                sources_scraped += 1
            except Exception as e:
                errors.append(f"{source.name.value}: {e}")

        stats = self.get_stats()
        summary = (
            f"Found {games_found} games across {sources_scraped} sources. "
            f"Total catalog: {stats['total_games']} games. "
            f"Latest: {stats['just_dropped']} just cracked."
        )

        return ScraperResult(
            timestamp=timestamp,
            games_found=games_found,
            new_games=new_games,
            updated_games=updated_games,
            sources_scraped=sources_scraped,
            errors=errors,
            summary=summary,
        )

    def _simulate_source(self, source: RepackerConfig) -> int:
        """Simulate scraping from a source (counts existing catalog games)."""
        games = self.load_games()
        count = len([g for g in games if source.name.value in (g.get("sources") or [])])
        source.games_count = count
        source.last_update = datetime.now()
        return count


def run_scraper(games_path: Optional[str] = None) -> ScraperResult:
    """Convenience function to run a scrape and print results."""
    scraper = BootyScraper(games_path)
    result = scraper.run_scrape()
    print(f"\n{'='*60}")
    print(f"  Booty Scraper Report — {result.timestamp.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"  Games found:    {result.games_found}")
    print(f"  New games:      {result.new_games}")
    print(f"  Updated games:  {result.updated_games}")
    print(f"  Sources scraped: {result.sources_scraped}")
    if result.errors:
        print(f"  Errors: {len(result.errors)}")
        for err in result.errors:
            print(f"    - {err}")
    print(f"  Summary: {result.summary}")
    print(f"{'='*60}\n")
    return result


if __name__ == "__main__":
    scraper_path = sys.argv[1] if len(sys.argv) > 1 else None
    run_scraper(scraper_path)
