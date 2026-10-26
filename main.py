"""Pirate Catalog — polished GUI for browsing and one-click-installing games."""

import flet as ft
import json
import os
import threading
import time
from pathlib import Path


# ── Load games.json ──
def load_games(path: str = None) -> list[dict]:
    """Load game catalog from JSON file."""
    if path is None:
        path = str(Path(__file__).parent / "data" / "games.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


GAMES = load_games()
CATEGORIES = ["All", "RPG", "Action", "Adventure", "Simulation", "Strategy", "Survival", "Mecha"]
REPACKERS = ["FitGirl", "DODI", "CODEX", "RELOADED", "SKIDROW", "ElAmigos"]


def main(page: ft.Page):
    page.title = "Booty Catalog"
    page.theme = ft.Theme(
        font_gallery=ft.FontGallery(
            primary_font=ft.GoogleFonts.space_grotesk(),
        ),
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_400,
            surface=ft.Colors.BLUE_50,
            on_surface=ft.Colors.BLUE_900,
        ),
    )
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_100
    page.scroll = ft.ScrollMode.ADAPTIVE

    state = {
        "category": "All",
        "search": "",
        "install_path": "C:\\Games",
        "progress": 0,
        "view": "grid",
        "repacker": None,
    }

    # ── Search bar ──
    search_bar = ft.TextField(
        hint_text="Search games, genres, or cracked tools...",
        prefix_icon=ft.icons.SEARCH,
        bgcolor=ft.Colors.WHITE,
        border_radius=25,
        expand=True,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=10),
        on_change=lambda e: refresh(),
    )

    # ── Category chips ──
    def build_chips():
        chips = []
        for cat in CATEGORIES:
            sel = state["category"] == cat
            chips.append(ft.Chip(
                label=ft.Text(cat, size=14, weight=ft.FontWeight.MEDIUM),
                bgcolor=ft.Colors.BLUE_100 if sel else ft.Colors.WHITE,
                color=ft.Colors.BLUE_400 if sel else ft.Colors.GREY_700,
                selected_color=ft.Colors.BLUE_50,
                on_click=lambda e, c=cat: _filter(c),
                selected=sel,
            ))
        return ft.Row(
            controls=chips, scroll=ft.ScrollMode.AUTO, spacing=8,
            padding=ft.padding.only(left=16, right=16, top=8),
        )

    # ── Repacker chips ──
    def build_repacker_chips():
        chips = [ft.Chip(
            label=ft.Text("All", size=12, weight=ft.FontWeight.MEDIUM),
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.GREY_700,
            on_click=lambda e: _repack_filter(None),
            selected=state["repacker"] is None,
        )]
        for rep in REPACKERS:
            sel = state["repacker"] == rep
            chips.append(ft.Chip(
                label=ft.Text(rep, size=12, weight=ft.FontWeight.MEDIUM),
                bgcolor=ft.Colors.GREEN_100 if sel else ft.Colors.WHITE,
                color=ft.Colors.GREEN_700 if sel else ft.Colors.GREY_700,
                on_click=lambda e, c=rep: _repack_filter(c),
                selected=sel,
            ))
        return ft.Row(
            controls=chips, scroll=ft.ScrollMode.AUTO, spacing=6,
            padding=ft.padding.only(left=16, right=16),
        )

    def _filter(cat):
        state["category"] = cat
        refresh()

    def _repack_filter(repacker):
        state["repacker"] = repacker
        refresh()

    # ── Game card ──
    def game_card(g: dict):
        # Build repack indicator
        repack_widget = None
        if g.get("repack"):
            repack_widget = ft.Container(
                content=ft.Row([
                    ft.Text("📦", size=14),
                    ft.Text(f"{g['repack']['title']}: {g['repack']['size']}", size=11, color=ft.Colors.GREEN_700),
                ], spacing=4),
                padding=ft.padding.only(left=8, top=6),
            )

        # Build source tags
        sources = g.get("sources", [])
        source_tags = [
            ft.Container(
                content=ft.Text(s, size=9, color=ft.Colors.GREY_600),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                bgcolor=ft.Colors.GREY_100,
                border_radius=3,
            )
            for s in sources
        ]
        tags_row = ft.Row(
            controls=source_tags, spacing=4,
            overflow=ft.ScrollMode.AUTO,
        ) if source_tags else None

        # Rating stars
        rating_display = None
        if g.get("rating", 0) > 0:
            rating_display = ft.Row([
                ft.Text("⭐", size=12),
                ft.Text(f"{g['rating']:.1f}", size=12, color=ft.Colors.GREY_600),
            ], spacing=2)

        # Badges
        badges = []
        if g.get("isJustDropped"):
            badges.append(ft.Container(
                content=ft.Text("NEW", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                bgcolor=ft.Colors.GOLD_200,
                border_radius=4,
            ))
        if g.get("isUpcoming"):
            badges.append(ft.Container(
                content=ft.Text("UPCOMING", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                bgcolor=ft.Colors.PURPLE_200,
                border_radius=4,
            ))

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(g["image"] if "image" in g else "🎮", size=36),
                                ft.Column([
                                    ft.Text(g["name"] if "name" in g else g["title"],
                                            size=16, weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE_400, width=200, truncate_with="..."),
                                    ft.Text(g["category"] if "category" in g else g["genreLabel"],
                                            size=11, color=ft.Colors.GREY_600),
                                ], spacing=2),
                                ft.Spacer(),
                                *badges,
                            ], spacing=10),
                        ], spacing=0),
                        padding=ft.padding.all(12),
                        bgcolor=ft.Colors.BLUE_50,
                    ),
                    ft.Divider(),
                    ft.Column([
                        ft.Row([
                            ft.Text("Size:", size=12, color=ft.Colors.GREY_600),
                            ft.Text(g.get("size", "—"), size=12, weight=ft.FontWeight.MEDIUM),
                            ft.Spacer(),
                            ft.Text("Cracked:", size=12, color=ft.Colors.GREY_600),
                            ft.Text(g.get("cracked_date", g.get("crackedDate", "—")),
                                    size=12, weight=ft.FontWeight.MEDIUM),
                        ], spacing=4, padding=ft.padding.only(left=12, right=12)),
                        ft.Divider(),
                        ft.Row([
                            ft.ElevatedButton(
                                "Download", icon=ft.icons.DOWNLOAD,
                                bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE,
                                on_click=lambda e, g=g: do_download(e, g), expand=True,
                            ),
                        ], alignment=ft.MainAxisAlignment.END, padding=ft.padding.only(right=12, bottom=12)),
                    ], spacing=0),
                ], spacing=0),
            elevation=3, shadow_color=ft.Colors.GREY_200,
            margin=ft.margin.symmetric(horizontal=8, vertical=6),
            width=320, border=ft.border.all(1, ft.Colors.BLUE_100),
        )

    # ── Refresh ──
    def refresh():
        filtered = [g for g in GAMES
                    if state["category"] == "All"
                    or g.get("category") == state["category"]
                    or g.get("genre") == state["category"].lower()]
        if state["search"]:
            search = state["search"].lower()
            filtered = [g for g in filtered
                        if (g.get("name", "").lower().contains(search)
                            or g.get("title", "").lower().contains(search)
                            or g.get("genre", "").lower().contains(search)
                            or g.get("crackedBy", "").lower().contains(search)
                            or any(search in tag.lower() for tag in g.get("tags", [])))]
        if state["repacker"]:
            filtered = [g for g in filtered
                        if state["repacker"] in (g.get("sources", []) or [])]

        grid = ft.Row(
            controls=[game_card(g) for g in filtered],
            scroll=ft.ScrollMode.AUTO if len(filtered) > 3 else ft.ScrollMode.NONE,
            spacing=8,
            vertical_alignment=ft.CrossAlignment.START,
            padding=ft.padding.only(top=8),
        )

        page.body = ft.Column([
            ft.Row([search_bar], spacing=8),
            build_chips(),
            ft.Divider(),
            ft.Text("Repacker Sources:", size=11, weight=ft.FontWeight.MEDIUM, color=ft.Colors.GREY_600),
            build_repacker_chips(),
            ft.Divider(),
            ft.Text(f"Showing {len(filtered)} of {len(GAMES)} games", size=11, color=ft.Colors.GREY_500),
            grid,
            ft.Spacer(),
        ], spacing=8, expand=True)
        page.update()

    # ── Download ──
    def do_download(e, g: dict):
        state["progress"] = 0
        game_name = g.get("name", g.get("title", "Unknown"))

        def loop():
            phases = [
                ("Connecting...", 0, 25),
                ("Downloading...", 25, 60),
                ("Extracting...", 60, 80),
                ("Bypassing DRM...", 80, 87),
                ("Installing...", 87, 95),
                ("Verifying...", 95, 99),
                ("Done!", 99, 100),
            ]
            for phase_name, start, end in phases:
                while state["progress"] < end:
                    state["progress"] += 1
                    time.sleep(0.03)
                dialog.content.controls[1].controls[0].value = state["progress"] / 100
                dialog.content.controls[1].controls[1].value = f"{state['progress']}% — {phase_name}"
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Downloading: {game_name}"),
            content=ft.Column([
                ft.ProgressRing(value=state["progress"] / 100),
                ft.Text(f"{state['progress']}% Complete", size=14),
                ft.Text(f"Installing to: {state['install_path']}", size=12, color=ft.Colors.GREY_600),
            ], spacing=12, alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Dismiss", on_click=lambda _: setattr(dialog, "open", False)),
            ],
        )

        threading.Thread(target=loop, daemon=True).start()
        page.dialog = dialog
        page.dialog.open = True
        page.update()

    # ── Install folder ──
    def set_install_folder(e):
        state["install_path"] = "C:\\Games"
        page.dialog = ft.AlertDialog(
            title=ft.Text("Install Folder"),
            content=ft.TextField(
                hint_text="Enter folder path",
                value=state["install_path"],
                on_submit=lambda e: setattr(state, "install_path", e.control.value or state["install_path"]),
            ),
            actions=[
                ft.ElevatedButton("Set", on_click=lambda _: setattr(page.dialog, "open", False)),
                ft.TextButton("Cancel", on_click=lambda _: setattr(page.dialog, "open", False)),
            ],
        )
        page.dialog.open = True
        page.update()

    # ── Top bar ──
    page.app_bar = ft.AppBar(
        leading=ft.Icon(ft.icons.SEARCH, size=28, color=ft.Colors.BLUE_400),
        title=ft.Text("Booty Catalog", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
        elevation=4,
        actions=[
            ft.FilledIconButton(
                icon=ft.icons.DARK_MODE,
                tooltip="Dark Mode",
                on_click=lambda _: setattr(page, "theme_mode",
                    ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT),
            ),
            ft.FilledIconButton(
                icon=ft.icons.FOLDER_OPEN,
                tooltip="Install Folder",
                on_click=set_install_folder,
            ),
            ft.FilledIconButton(
                icon=ft.icons.INFO,
                tooltip="About",
                on_click=lambda _: page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Booty Catalog v1.0 — The ultimate pirate game catalog."),
                                behavior=ft.SnackBarBehavior.FIXED, duration=3000),
                ),
            ),
        ],
    )

    refresh()


ft.run(main, assets_dir="assets")
