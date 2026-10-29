/**
 * CatalogUpdater.h — Auto-update for game catalog data
 * Location: F:\study\projects\pirate-catalog
 *
 * Fetches a remote manifest, compares versions, downloads updated
 * games.json to %APPDATA%\BootyCatalog\cache\, and signals the main
 * window to reload its game list.
 */
#ifndef CATALOG_UPDATER_H
#define CATALOG_UPDATER_H

#include <windows.h>

/* ━━━ CONSTANTS ━━━ */
#define UPDATE_CHECK_INTERVAL_MS   3600000   /* re-check every hour */
#define HTTP_TIMEOUT_MS            8000      /* max wait per request  */
#define MANIFEST_URL               "https://raw.githubusercontent.com/" \
                                   "your-user/pirate-catalog/main/data/manifest.json"
#define CACHE_DIR_NAME             "BootyCatalog\\cache"
#define STATE_FILE                 "update_state.json"
#define GAMES_CACHE_FILE           "games.json"

/* Custom messages posted to g_hMain after an update completes */
#define WM_CATALOG_UPDATED         (WM_USER + 60)  /* wParam = 1 if new data loaded */
#define WM_UPDATE_STATUS           (WM_USER + 61)  /* lParam = status string ptr   */

/* Status codes for WM_UPDATE_STATUS */
#define UPD_OK          0
#define UPD_NO_NET      1
#define UPD_SAME_VER    2
#define UPD_DL_FAIL     3
#define UPD_PARSE_FAIL  4

/* ━━━ PUBLIC API ━━━ */

/*
 * Start the background update check. Safe to call from WinMain before
 * entering the message loop. Spawns a detached thread that will post
 * WM_CATALOG_UPDATED / WM_UPDATE_STATUS to hwnd when done.
 *
 * Returns 1 on success (thread started), 0 on failure.
 */
int start_update_check(HWND hwnd);

/*
 * Force an immediate check regardless of interval. Useful for a
 * manual "Check for updates" menu item.
 */
void force_update_check(HWND hwnd);

/*
 * Return the path to the cached games.json, or NULL if no cache exists.
 * The caller does NOT own the buffer; it is valid until the next call.
 */
const char* get_cached_games_path(void);

/*
 * Parse a downloaded JSON buffer into g_games[]. Replaces whatever was
 * there before. Returns number of games parsed, -1 on error.
 */
int load_catalog_from_file(const char* filePath);

#endif // CATALOG_UPDATER_H
