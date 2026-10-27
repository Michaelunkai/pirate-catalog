/**
 * GridBrowser.cpp -- Game grid/list view with filtering, search, sort
 * Location: F:\study\projects\pirate-catalog
 */

#include "../include/BootyCatalog.h"
#include <vector>
#include <string>
#include <algorithm>

static Game g_filtered[MAX_GAMES];
static int g_filteredCount = 0;
static int g_sortMode = 0;
static int g_filterMode = 0;
static char g_search[128] = "";

/* Case-insensitive substring search */
static const char* stristr(const char* haystack, const char* needle) {
    const char* h; const char* n;
    for (h = haystack; *h; h++) {
        for (n = needle; tolower((unsigned char)*h) == tolower((unsigned char)*n) && *n; h++, n++);
        if (!*n) return h;
    }
    return NULL;
}

void build_grid_from_filtered(void) {
    if (!g_hGrid) return;

    ListView_DeleteAllItems(g_hGrid);
    g_filteredCount = 0;

    for (int i = 0; i < g_gameCount; i++) {
        Game* g = &g_games[i];
        if (g_filterMode == 1 && !g->isJustDropped) continue;
        if (g_filterMode == 2 && !g->isUpcoming) continue;
        if (g_search[0]) {
            char* s = g_search; bool found = false;
            if (stristr(g->title, s)) found = true;
            if (!found && stristr(g->genreLabel, s)) found = true;
            if (!found && stristr(g->crackedBy, s)) found = true;
            for (int t = 0; t < g->tagCount && !found; t++) {
                if (stristr(g->tags[t], s)) found = true;
            }
            if (!found && stristr(g->description, s)) found = true;
            if (!found) continue;
        }
        g_filtered[g_filteredCount++] = *g;
    }

    switch (g_sortMode) {
        case 0: /* Newest */
            std::sort(g_filtered, g_filtered + g_filteredCount,
                [](const Game& a, const Game& b) {
                    return strcmp(a.crackedDate, b.crackedDate) > 0;
                });
            break;
        case 1: /* Oldest */
            std::sort(g_filtered, g_filtered + g_filteredCount,
                [](const Game& a, const Game& b) {
                    return strcmp(a.crackedDate, b.crackedDate) < 0;
                });
            break;
        case 2: /* Name */
            std::sort(g_filtered, g_filtered + g_filteredCount,
                [](const Game& a, const Game& b) {
                    return strcmp(a.title, b.title) < 0;
                });
            break;
        case 3: /* Size */
            std::sort(g_filtered, g_filtered + g_filteredCount,
                [](const Game& a, const Game& b) {
                    return a.sizeBytes > b.sizeBytes;
                });
            break;
        case 4: /* Rating */
            std::sort(g_filtered, g_filtered + g_filteredCount,
                [](const Game& a, const Game& b) {
                    return a.rating > b.rating;
                });
            break;
    }

    for (int i = 0; i < g_filteredCount && i < MAX_GAMES; i++) {
        LVITEMA lvi = {0};
        lvi.mask = LVIF_TEXT;
        lvi.iSubItem = 0;
        lvi.pszText = (LPSTR)g_filtered[i].title;
        int idx = ListView_InsertItem(g_hGrid, &lvi);
        ListView_SetItemText(g_hGrid, idx, 1, g_filtered[i].genreLabel);
        ListView_SetItemText(g_hGrid, idx, 2, g_filtered[i].size);
        ListView_SetItemText(g_hGrid, idx, 3, g_filtered[i].crackedBy);
        ListView_SetItemText(g_hGrid, idx, 4, g_filtered[i].crackedDate);
        LVITEMA lvi2;
        memset(&lvi, 0, sizeof(LVITEMA));
        lvi.mask = LVIF_PARAM;
        lvi.iItem = idx;
        lvi.lParam = (LPARAM)&g_filtered[i];
        SendMessageA(g_hGrid, LVM_SETITEM, 0, (LPARAM)&lvi);
    }

    char buf[256];
    sprintf(buf, "Showing %d of %d games", g_filteredCount, g_gameCount);
    if (g_hStatus)
        SendMessageA(g_hStatus, SB_SETTEXT, 0, (LPARAM)buf);
}

void build_grid(void) {
    g_gridCount = g_gameCount;
    memcpy(g_grid, g_games, sizeof(Game) * g_gameCount);
    build_grid_from_filtered();
}

Game* get_game_by_index(int idx) {
    if (!g_hGrid || idx < 0) return NULL;
    LVITEMA lviGet;
    memset(&lviGet, 0, sizeof(LVITEMA));
    lviGet.mask = LVIF_PARAM;
    lviGet.iItem = idx;
    SendMessageA(g_hGrid, LVM_GETITEM, idx, (LPARAM)&lviGet);
    DWORD_PTR data = lviGet.lParam;
    return (Game*)data;
}

int count_by_repacker(const char* repacker) {
    int count = 0;
    for (int i = 0; i < g_gameCount; i++) {
        for (int s = 0; s < g_games[i].sourceCount; s++) {
            if (strcmp(g_games[i].sources[s], repacker) == 0) {
                count++;
                break;
            }
        }
    }
    return count;
}

Game* find_latest_crack(void) {
    if (g_gameCount == 0) return NULL;
    Game* latest = &g_games[0];
    for (int i = 1; i < g_gameCount; i++) {
        if (strcmp(g_games[i].crackedDate, latest->crackedDate) > 0)
            latest = &g_games[i];
    }
    return latest;
}

const char* get_game_emoji(const char* genre) {
    static const char* genres[] = {"rpg", "action", "strategy", "simulation", "survival", "mecha", "adventure", "racing"};
    static const char* emojis[] = {"\xf0\x9f\xab\x99", "\xf0\x9f\x8f\xa2", "\xf0\x9f\x9a\x9f", "\xf0\x9f\x9f\x93",
                                   "\xf0\x9f\xa6\x9f", "\xf0\x9f\xa4\x96", "\xf0\x9f\x8f\xba", "\xf0\x9f\x8f\x8e"};
    for (int i = 0; i < 8; i++) {
        if (strcmp(genre, genres[i]) == 0) return emojis[i];
    }
    return "\xf0\x9f\x8e\xae";
}

long long get_total_size(Game* g) {
    long long total = g->sizeBytes;
    if (g->repack.title[0]) {
        for (int i = 0; i < 12; i++) {
            static struct { const char* name; float compression; } REPACK[12] = {
                {"FitGirl", 0.6f}, {"DODI", 0.5f}, {"CODEX", 1.0f},
                {"RELOADED", 1.0f}, {"SKIDROW", 0.7f}, {"ElAmigos", 1.0f},
                {"Tokyo", 0.8f}, {"OiGi", 0.75f}, {"TEAM-OUT", 0.7f},
                {"INDIE", 1.0f}, {"NINTEN", 1.0f}, {"CRACKED.IO", 1.0f}
            };
            if (strcmp(REPACK[i].name, g->repack.title) == 0) {
                total = (long long)(total * REPACK[i].compression);
                break;
            }
        }
    }
    return total;
}

const char* format_size(long long bytes, char* buf, int bufSize) {
    if (bytes < 1024)
        sprintf(buf, "%lld B", bytes);
    else if (bytes < 1024 * 1024)
        sprintf(buf, "%.1f KB", bytes / 1024.0);
    else if (bytes < 1024LL * 1024 * 1024 * 1024)
        sprintf(buf, "%.1f MB", bytes / (1024.0 * 1024.0));
    else
        sprintf(buf, "%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0));
    return buf;
}

void time_ago(const char* dateStr, char* buf, int bufSize) {
    struct tm tm;
    memset(&tm, 0, sizeof(tm));
    sscanf(dateStr, "%d-%d-%d", &tm.tm_year, &tm.tm_mon, &tm.tm_mday);
    tm.tm_year -= 1900;
    tm.tm_mon -= 1;
    time_t t = mktime(&tm);
    time_t now = time(NULL);
    double diff = difftime(now, t);
    int days = (int)(diff / 86400.0);
    if (days == 0) strcpy(buf, "Today");
    else if (days == 1) strcpy(buf, "Yesterday");
    else if (days < 7) sprintf(buf, "%d days ago", days);
    else if (days < 30) sprintf(buf, "%d weeks ago", days / 7);
    else if (days < 365) sprintf(buf, "%d months ago", days / 30);
    else sprintf(buf, "%d years ago", days / 365);
}

int is_repack_available(Game* g) {
    return g->repack.title[0] ? 1 : 0;
}
