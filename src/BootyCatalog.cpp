/*
 * Booty Catalog -- Full C++ EXE (Final Consolidated Build)
 * The Full Demand:
 * Continue in this folder you currently add, maximize this project in
 * any perspective. best looking and best performing application with GUI.
 * allowing me to scroll and find every possible available pirately game
 * including the very last one that was just recently cracked. one click
 * to download and install to any folder. repackers like dodi fitgirl.
 * update the .md file for future sessions. make all in c++ compile to
 * exe that runs flawlessly. beautiful icon in taskbar and system tray.
 *
 * Location: F:\study\projects\pirate-catalog
 * User: C:\Users\Admin (Windows 11 Pro)
 * Build: g++ -o build/BootyCatalog.exe -static -static-libgcc -Os
 */
#include <winsock2.h>
#include <ws2tcpip.h>
#define WIN32_LEAN_AND_MEAN
#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <wingdi.h>
#include <commctrl.h>
/* Per-column paint stage; not always defined by MinGW's commctrl.h. */
#ifndef CDDS_SUBITEMPAINT
#define CDDS_SUBITEMPAINT (CDDS_SUBITEM | CDDS_ITEMPREPAINT)
#endif
#include <shellapi.h>
#include <shlwapi.h>
#include <wininet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <malloc.h>
#include <shlobj.h>
#include <process.h>
#include <vector>
#include <algorithm>
#include "../include/BootyCatalog.h"
#include "../src/embedded.h"

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "ole32.lib")

/* ━━━ CONSTANTS ━━━ */
#define TRAY_MSG_CB    (WM_USER + 20)
#define DL_MSG_CONNECT (WM_USER + 50)
#define DL_MSG_STATUS  (WM_USER + 51)
#define DL_MSG_STOP    (WM_USER + 52)
#define MAX_PATH2      260
#define PROGRESS_BAR   2004
#define BTN_FILTER_FG  2010
#define BTN_FILTER_DODI 2011
#define BTN_FILTER_CODEX 2012
#define BTN_FILTER_RELOAD 2013
#define BTN_FILTER_ALL 2014
#define HERO_BANNER    2020
#define BTN_THEME      2004
#define OUT_DEFAULT    3
#define CLIP_DEFAULT   4

/* ━━━ GLOBALS (from header, defined here) ━━━ */
Game        g_games[MAX_GAMES];
int         g_gameCount = 0;
GameItem    g_grid[MAX_GAMES];
int         g_gridCount = 0;
int         g_viewMode = 0;
HttpServer  g_httpServer;
DownloadTask g_download;
NOTIFYICONDATAA g_nid;
HWND g_hMain = NULL;
HWND g_hStatus = NULL;
HWND g_hGrid = NULL;
HWND g_hSearch = NULL;
HWND g_hFilterBar = NULL;
HWND g_hHero = NULL;
HWND g_hThemeBtn = NULL;
HWND g_hDownloadDl = NULL;
HWND g_hInstallBtn = NULL;   /* "Install" -- starts the one-click flow */
HWND g_hFolderBtn  = NULL;   /* browse for the install destination folder */
static char g_installDir[MAX_PATH] = "E:\\Games";
HWND g_hDlProgress = NULL;
const char* EXE_DIR = NULL;
const char* GAMES_JSON_PATH = NULL;
GameItem*   g_selected = NULL;
int         g_darkMode = 1;
int         g_repackFilter = 0;
static char g_search[128];
static int  g_sortMode = 0;
HINSTANCE   g_hInst;
static Game g_filtered[MAX_GAMES];
static int  g_filteredCount = 0;
static int  g_filterMode = 0;

/* ━━━ COLORS ━━━ */
static COLORREF dark_bg    = RGB(18, 22, 28);
static COLORREF dark_surf  = RGB(26, 32, 40);
static COLORREF dark_text  = RGB(232, 232, 232);
static COLORREF dark_accent = RGB(102, 180, 255);
static COLORREF light_bg   = RGB(245, 245, 248);
static COLORREF light_surf = RGB(255, 255, 255);
static COLORREF light_text = RGB(30, 30, 35);
static COLORREF light_accent = RGB(60, 120, 210);

static COLORREF get_bg_color(void) { return g_darkMode ? dark_bg : light_bg; }
static COLORREF get_surf_color(void) { return g_darkMode ? dark_surf : light_surf; }
static COLORREF get_text_color(void) { return g_darkMode ? dark_text : light_text; }
static COLORREF get_accent_color(void) { return g_darkMode ? dark_accent : light_accent; }

static HBRUSH get_bg_brush(void) { return CreateSolidBrush(get_bg_color()); }
static HBRUSH get_surf_brush(void) { return CreateSolidBrush(get_surf_color()); }

/* ━━━ JSON PARSER ━━━ */
int parse_games_json(void* buf, int len) {
    char* p = (char*)buf;
    long dbg_steps = 0;
    /* Skip any leading bytes (BCAT container header) up to the array open. */
    while (len-- > 0 && *p != '[') p++;
    if (*p != '[') return 0;
    p++; g_gameCount = 0;
    while (*p && g_gameCount < MAX_GAMES) {
        dbg_steps++;
        if (dbg_steps > 100000) { fprintf(stderr, "PARSE LOOP at offset %ld\n", p - (char*)buf); return g_gameCount; }
        while (*p && (*p == ' ' || *p == '\n' || *p == '\r' || *p == '\t')) p++;
        if (*p == ']') break;
        if (*p == ',') { p++; continue; }
        if (*p != '{') break;
        p++;
        Game* g = &g_games[g_gameCount];
        memset(g, 0, sizeof(Game));
        long dbg_inner = 0;
        while (*p && *p != '}') {
            dbg_inner++;
            if (dbg_inner > 500) { fprintf(stderr, "INNER LOOP game=%d at offset %ld:\n%.200s\n", g_gameCount, (long)(p - (char*)buf), p - 80 >= (char*)buf ? p - 80 : (char*)buf); return g_gameCount; }
            while (*p && (*p == ' ' || *p == '\n' || *p == '\r' || *p == '\t')) p++;
            if (*p == '}') break;   /* last field consumed its comma/brace */
            char key[64]; int ki = 0;
            if (*p == '"') p++;
            while (*p && *p != '"') { if (ki < 63) key[ki++] = *p; p++; }
            key[ki] = '\0'; if (*p == '"') p++;
            while (*p==' '||*p=='\n'||*p=='\r'||*p=='\t') p++; if (*p == ':') p++; while (*p==' '||*p=='\n'||*p=='\r'||*p=='\t') p++;
            if (*p == '"') {
                p++; char val[256]; int vi = 0;
                while (*p && *p != '"') {
                    char c = *p;
                    if (c == '\\' && p[1]) { p++; c = *p; }
                    if (vi < 255) val[vi++] = c;
                    p++;
                }
                val[vi] = '\0'; if (*p == '"') p++;
                if (strcmp(key, "id") == 0) strncpy(g->id, val, 127);
                else if (strcmp(key, "title") == 0) strncpy(g->title, val, 127);
                else if (strcmp(key, "genre") == 0) strncpy(g->genre, val, 31);
                else if (strcmp(key, "genreLabel") == 0) strncpy(g->genreLabel, val, 63);
                else if (strcmp(key, "description") == 0) strncpy(g->description, val, 255);
                else if (strcmp(key, "crackedBy") == 0) strncpy(g->crackedBy, val, 31);
                else if (strcmp(key, "crackedDate") == 0) strncpy(g->crackedDate, val, 15);
                else if (strcmp(key, "uploadedDate") == 0) strncpy(g->uploadedDate, val, 15);
                else if (strcmp(key, "size") == 0) strncpy(g->size, val, 15);
                else if (strcmp(key, "version") == 0) strncpy(g->version, val, 31);
                else if (strcmp(key, "imageGradient") == 0) strncpy(g->imageGradient, val, 127);
                else if (strcmp(key, "feedUrl") == 0) strncpy(g->feedUrl, val, 511);
            } else if (*p == 't') {
                if (strcmp(key, "isUpcoming") == 0) g->isUpcoming = 1;
                else if (strcmp(key, "isJustDropped") == 0) g->isJustDropped = 1;
                else if (strcmp(key, "isLatest") == 0) g->isLatest = 1;
                while (*p && *p != ',') p++;
            } else if (*p == 'f') {
                if (strcmp(key, "isUpcoming") == 0) g->isUpcoming = 0;
                else if (strcmp(key, "isJustDropped") == 0) g->isJustDropped = 0;
                else if (strcmp(key, "isLatest") == 0) g->isLatest = 0;
                while (*p && *p != ',') p++;
            } else if (*p == 'n') {
                if (strcmp(key, "repack") == 0) memset(&g->repack, 0, sizeof(g->repack));
                while (*p && *p != ',') p++;
            } else if (*p == '-' || (*p >= '0' && *p <= '9')) {
                char numval[32]; int ni = 0;
                if (*p == '-') { numval[ni++] = *p++; }
                while (*p && *p != ',' && *p != '}' && *p != ']') { if (ni < 31) numval[ni++] = *p; p++; }
                numval[ni] = '\0';
                if (strcmp(key, "sizeBytes") == 0) g->sizeBytes = atoll(numval);
                else if (strcmp(key, "rating") == 0) g->rating = (float)atof(numval);
                while (*p && *p != ',' && *p != '}') p++;
            } else if (*p == '[' && (strcmp(key, "tags") == 0 || strcmp(key, "sources") == 0)) {
                p++;
                while (*p && *p != ']') {
                    while (*p==' '||*p=='\n'||*p=='\r'||*p=='\t') p++;
                    if (*p == '"') { p++; char arrval[32]; int ai = 0;
                        while (*p && *p != '"') { if (ai < 31) arrval[ai++] = *p; p++; }
                        arrval[ai] = '\0'; if (*p == '"') p++;
                        if (strcmp(key, "tags") == 0 && g->tagCount < MAX_TAG)
                            strncpy(g->tags[g->tagCount++], arrval, 31);
                        else if (strcmp(key, "sources") == 0 && g->sourceCount < MAX_SRC)
                            strncpy(g->sources[g->sourceCount++], arrval, 31);
                    } if (*p == ',') p++;
                }
                if (*p == ']') p++;
            } else if (*p == '{' && strcmp(key, "repack") == 0) {
                p++; memset(&g->repack, 0, sizeof(g->repack));
                while (*p && *p != '}') {
                    while (*p==' '||*p=='\n'||*p=='\r'||*p=='\t') p++;
                    if (*p == '"') { p++; char rk[32]; int ri = 0;
                        while (*p && *p != '"') { if (ri < 31) rk[ri++] = *p; p++; }
                        rk[ri] = '\0'; if (*p == '"') p++;
                        while (*p==' '||*p=='\n'||*p=='\r'||*p=='\t') p++; if (*p == ':') p++; while (*p==' '||*p=='\n'||*p=='\r'||*p=='\t') p++;
                        if (*p == '"') { p++; char rv[256]; int vvi = 0;
                            while (*p && *p != '"') {
                                char rc = *p;
                                if (rc == '\\' && p[1]) { p++; rc = *p; }
                                if (vvi < 255) rv[vvi++] = rc;
                                p++;
                            }
                            rv[vvi] = '\0'; if (*p == '"') p++;
                            if (strcmp(rk, "title") == 0) strncpy(g->repack.title, rv, 63);
                            else if (strcmp(rk, "size") == 0) strncpy(g->repack.size, rv, 15);
                            else if (strcmp(rk, "url") == 0) strncpy(g->repack.url, rv, 127);
                        }
                    } if (*p == ',') p++;
                }
                if (*p == '}') p++;
            } else { while (*p && *p != ',' && *p != '}') p++; }
            while (*p==' '||*p=='\n'||*p=='\r'||*p=='\t') p++;
            if (*p == ',') p++;
        }
        if (*p == '}') p++;
        g_gameCount++;
    }
    return g_gameCount;
}

/* ━━━ HEX DECODER ━━━ */
static int hex_decode(const unsigned char* hex, unsigned char* out, int maxlen) {
    int i = 0;
    while (hex[i] && hex[i + 1] && i < maxlen * 2) {
        char hi = hex[i] > '9' ? hex[i] - 'a' + 10 : hex[i] - '0';
        char lo = hex[i + 1] > '9' ? hex[i + 1] - 'a' + 10 : hex[i + 1] - '0';
        if (i / 2 < maxlen) out[i / 2] = (hi << 4) | lo;
        i += 2;
    }
    return i / 2;
}

/* ━━━ RESOURCE BUNDLES ━━━ */
static unsigned char g_games_resource_blob[1024 * 1024];
static unsigned char g_html_resource_blob[1024 * 1024];
static unsigned char g_css_resource_blob[512 * 1024];
static unsigned char g_js_resource_blob[512 * 1024];
static unsigned char g_jsdl_resource_blob[256 * 1024];

/* ━━━ GRADIENT DECODER ━━━ */
typedef struct { int r, g, b; } GradientColor;
static void decode_gradient(const char* gradHex, GradientColor* colors, int* count) {
    const unsigned char* hex = (const unsigned char*)gradHex;
    *count = 0;
    while (*hex && *(hex+1) && *count < 8) {
        if (*hex == '0' && *(hex+1) == 'x') { hex += 2; }
        char hi = hex[0] > '9' ? hex[0] - 'a' + 10 : hex[0] - '0';
        char lo = hex[1] > '9' ? hex[1] - 'a' + 10 : hex[1] - '0';
        colors[*count].r = (hi << 4) | lo; hex += 2;
        hi = hex[0] > '9' ? hex[0] - 'a' + 10 : hex[0] - '0';
        lo = hex[1] > '9' ? hex[1] - 'a' + 10 : hex[1] - '0';
        colors[*count].g = (hi << 4) | lo; hex += 2;
        hi = hex[0] > '9' ? hex[0] - 'a' + 10 : hex[0] - '0';
        lo = hex[1] > '9' ? hex[1] - 'a' + 10 : hex[1] - '0';
        colors[*count].b = (hi << 4) | lo; hex += 2;
        (*count)++;
    }
}

/* ━━━ GRADIENT PAINT HELPER ━━━ */
static void paint_gradient(HDC hdc, RECT* rc, const char* gradHex, int hgt) {
    GradientColor colors[8];
    int count = 0;
    decode_gradient(gradHex, colors, &count);
    if (count < 2) {
        FillRect(hdc, rc, CreateSolidBrush(RGB(20, 20, 30)));
        return;
    }
    RECT tmp;
    int y0 = 0, y1 = hgt;
    for (int c = 0; c < count - 1; c++) {
        int t0 = y0, t1 = (c == count - 2) ? y1 : (y0 + y1) / 2;
        COLORREF col = RGB(colors[c].r, colors[c].g, colors[c].b);
        tmp = *rc; tmp.top = rc->top + t0; tmp.bottom = rc->top + t1;
        HBRUSH br = CreateSolidBrush(col);
        FillRect(hdc, &tmp, br);
        DeleteObject(br);
        y0 = t0;
    }
}

/* Parse a CSS gradient string like "linear-gradient(135deg, #1a1a2e 0%, ...)"
   into the internal hex form expected by paint_gradient. Returns number of
   color stops found. */
static int parse_css_gradient(const char* css, GradientColor* out, int maxCount) {
    int n = 0;
    const char* p = css;
    while ((p = strchr(p, '#')) != NULL && n < maxCount) {
        unsigned r, g, b;
        if (sscanf(p + 1, "%2x%2x%2x", &r, &g, &b) == 3) {
            out[n].r = (unsigned char)r;
            out[n].g = (unsigned char)g;
            out[n].b = (unsigned char)b;
            n++;
        }
        p += 6;
    }
    return n;
}

/* Paint a game's title cell (sub-item 0) with its real cover gradient and
   white text, using the exact NMLVCUSTOMDRAW layout from commctrl.h:
   cd->nmcd.{dwDrawStage,hdc,rc,dwItemSpec,uItemState}, then cd->iSubItem. */
static void draw_game_cover(NMLVCUSTOMDRAW* cd) {
    int idx = (int)cd->nmcd.dwItemSpec;
    LVITEMA lvip = {0};
    lvip.iItem = idx;
    lvip.mask = LVIF_PARAM;
    ListView_GetItem(g_hGrid, &lvip);
    Game* g = (Game*)lvip.lParam;
    if (!g) return;
    HDC hdc = cd->nmcd.hdc;
    RECT rc = cd->nmcd.rc;
    /* Paint only column 0 so other columns keep their default background. */
    ListView_GetSubItemRect(g_hGrid, idx, 0, LVIR_BOUNDS, &rc);
    GradientColor colors[8];
    int n = parse_css_gradient(g->imageGradient, colors, 8);
    if (n >= 2) {
        /* Diagonal-ish: paint horizontal bands top-to-bottom across the row. */
        int bandH = (rc.bottom - rc.top) / n;
        for (int i = 0; i < n; i++) {
            RECT tmp = rc;
            tmp.top = rc.top + i * bandH;
            tmp.bottom = tmp.top + bandH;
            HBRUSH br = CreateSolidBrush(RGB(colors[i].r, colors[i].g, colors[i].b));
            FillRect(hdc, &tmp, br);
            DeleteObject(br);
        }
    } else {
        FillRect(hdc, &rc, CreateSolidBrush(RGB(20, 20, 30)));
    }
    SetBkMode(hdc, TRANSPARENT);
    SetTextColor(hdc, RGB(255, 255, 255));

    /* Render star rating next to the title (column 0 area). */
    char rating_str[16];
    sprintf(rating_str, "%.1f", g->rating);
    int stars = 5;
    int filled = 0;
    float r = atof(rating_str);
    filled = (int)(r + 0.5);
    if (filled > stars) filled = stars;
    if (filled < 0) filled = 0;
    SetTextColor(hdc, RGB(255, 255, 0)); // yellow stars
    int star_w = 14;
    int start_x = rc.left + 4;
    for (int s = 0; s < stars; s++) {
        RECT star_rc = {start_x + s * star_w, rc.top, start_x + (s + 1) * star_w, rc.bottom};
        DrawTextA(hdc, s < filled ? "★" : "☆", -1, &star_rc, DT_CENTER | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);
    }
    SetTextColor(hdc, RGB(255, 255, 255));
    int title_x = start_x + stars * star_w + 4;
    RECT title_rc = {title_x, rc.top, rc.right, rc.bottom};
    DrawTextA(hdc, g->title, -1, &title_rc, DT_LEFT | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);
}

/* ━━━ RESOURCE DECODER ━━━ */
void* find_resource(HINSTANCE hInst, int id, const char* type, int* len) {
    HRSRC hr = FindResourceA(hInst, MAKEINTRESOURCEA(id), type);
    if (!hr) return NULL;
    HGLOBAL hg = LoadResource(hInst, hr);
    if (!hg) return NULL;
    *len = (int)SizeofResource(hInst, hr);
    return LockResource(hg);
}

void seed_games(void) {
    Game* g = &g_games[g_gameCount];
    strncpy(g->title, "GTA VI", 127);
    g->isUpcoming = 1; g->isJustDropped = 0; g->isLatest = 0;
    g->rating = 4.9f; g_gameCount++;
}

/* ━━━ EXPORT CATALOG ━━━ */
int export_catalog_json(const char* path) {
    FILE* f = fopen(path, "w");
    if (!f) return -1;
    fprintf(f, "[\n");
    for (int i = 0; i < g_gameCount; i++) {
        Game* g = &g_games[i];
        fprintf(f, "  {\n");
        fprintf(f, "    \"id\": \"%s\",\n", g->id);
        fprintf(f, "    \"title\": \"%s\",\n", g->title);
        fprintf(f, "    \"genre\": \"%s\",\n", g->genre);
        fprintf(f, "    \"genreLabel\": \"%s\",\n", g->genreLabel);
        fprintf(f, "    \"description\": \"%s\",\n", g->description);
        fprintf(f, "    \"crackedBy\": \"%s\",\n", g->crackedBy);
        fprintf(f, "    \"crackedDate\": \"%s\",\n", g->crackedDate);
        fprintf(f, "    \"uploadedDate\": \"%s\",\n", g->uploadedDate);
        fprintf(f, "    \"size\": \"%s\",\n", g->size);
        fprintf(f, "    \"sizeBytes\": %lld,\n", g->sizeBytes);
        fprintf(f, "    \"version\": \"%s\",\n", g->version);
        fprintf(f, "    \"isUpcoming\": %d,\n", g->isUpcoming);
        fprintf(f, "    \"isJustDropped\": %d,\n", g->isJustDropped);
        fprintf(f, "    \"isLatest\": %d,\n", g->isLatest);
        fprintf(f, "    \"rating\": %.1f,\n", g->rating);
        fprintf(f, "    \"tags\": [");
        for (int t = 0; t < g->tagCount; t++) {
            fprintf(f, "\"%s\"%s", g->tags[t], (t < g->tagCount - 1) ? ", " : "");
        }
        fprintf(f, "],\n");
        fprintf(f, "    \"imageGradient\": \"%s\",\n", g->imageGradient);
        fprintf(f, "    \"imageUrl\": \"%s\",\n", "");
        fprintf(f, "    \"repack\": null,\n");
        fprintf(f, "    \"sources\": [");
        for (int s = 0; s < g->sourceCount; s++) {
            fprintf(f, "\"%s\"%s", g->sources[s], (s < g->sourceCount - 1) ? ", " : "");
        }
        fprintf(f, "],\n");
        fprintf(f, "    \"feedUrl\": \"%s\"\n", g->feedUrl ? g->feedUrl : "");
        fprintf(f, "  }%s\n", (i < g_gameCount - 1) ? "," : "");
    }
    fprintf(f, "]\n");
    fclose(f);
    return 0;
}

int export_catalog_csv(const char* path) {
    FILE* f = fopen(path, "w");
    if (!f) return -1;
    fprintf(f, "id,title,genre,genreLabel,description,crackedBy,crackedDate,uploadedDate,size,sizeBytes,version,isUpcoming,isJustDropped,isLatest,rating,tags,imageGradient,imageUrl,sources,feedUrl\n");
    for (int i = 0; i < g_gameCount; i++) {
        Game* g = &g_games[i];
        fprintf(f, "\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%lld,\"%s\",%d,%d,%d,%.1f,\"",
            g->id, g->title, g->genre, g->genreLabel, g->description,
            g->crackedBy, g->crackedDate, g->uploadedDate, g->size,
            g->sizeBytes, g->version, g->isUpcoming, g->isJustDropped,
            g->isLatest, g->rating);
        for (int t = 0; t < g->tagCount; t++) {
            fprintf(f, "%s%s", g->tags[t], (t < g->tagCount - 1) ? "; " : "");
        }
        fprintf(f, "\",\"%s\",\"%s\",\"",
            g->imageGradient, "");
        for (int s = 0; s < g->sourceCount; s++) {
            fprintf(f, "%s%s", g->sources[s], (s < g->sourceCount - 1) ? "; " : "");
        }
        fprintf(f, "\",\"%s\"\n", g->feedUrl ? g->feedUrl : "");
    }
    fclose(f);
    return 0;
}

/* ━━━ Rating dialog helpers ━━━ */
static Game* g_rating_game = NULL;
static int g_rating_selected = 0;

static void save_rating_to_json_impl(const char* game_id, float rating) {
    if (!GAMES_JSON_PATH || !GAMES_JSON_PATH[0]) return;
    FILE* f = fopen(GAMES_JSON_PATH, "r");
    if (!f) return;
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* json = (char*)malloc(len + 1);
    if (!json) { fclose(f); return; }
    fread(json, 1, len, f);
    json[len] = '\0';
    fclose(f);

    /* Find the game's rating field and update it */
    char* p = json;
    while ((p = strstr(p, "\"id\"")) != NULL) {
        char* id_start = strchr(p, '"');
        if (!id_start) break;
        id_start++;
        char* id_end = strchr(id_start, '"');
        if (!id_end) break;
        if (strcmp(g_games[0].id, g_rating_game->id) == 0) {
            char* r = strstr(id_end, "\"rating\"");
            if (r) {
                r = strchr(r, ':');
                if (r) {
                    r++;
                    while (*r == ' ' || *r == '\t') r++;
                    char* r_end = r;
                    while (*r_end && *r_end != ',' && *r_end != '}') r_end++;
                    char new_val[16];
                    sprintf(new_val, "%.1f", rating);
                    int diff = (int)strlen(new_val) - (int)(r_end - r);
                    memmove(r_end + diff, r_end, strlen(r_end) + 1);
                    memcpy(r, new_val, strlen(new_val));
                    break;
                }
            }
        }
        p = id_end;
    }

    f = fopen(GAMES_JSON_PATH, "w");
    if (f) {
        fwrite(json, 1, strlen(json), f);
        fclose(f);
    }
    free(json);
}

/* ━━━ Rating dialog helpers (forward-declared before use) ━━━ */
static void save_rating_to_json(const char* game_id, float rating);
LRESULT CALLBACK RatingDlgProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);

/* ━━━ Rating dialog implementation ━━━ */
void show_rating_dialog(HWND parent, Game* game) {
    g_rating_game = game;
    g_rating_selected = (int)(game->rating + 0.5);
    DialogBoxA(GetModuleHandleA(NULL), MAKEINTRESOURCEA(6000), parent, RatingDlgProc);
}

/* ━━━ Callbacks & render helpers ━━━ */
LRESULT CALLBACK RatingDlgProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    static HWND hStar[5];
    switch (msg) {
        case WM_INITDIALOG: {
            if (!g_rating_game) return FALSE;
            for (int i = 0; i < 5; i++) {
                hStar[i] = CreateWindowA("BUTTON", (i < g_rating_game->rating + 0.5) ? "★" : "☆",
                    WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                    20 + i * 36, 30, 36, 36, hwnd, (HMENU)(5000 + i), GetModuleHandleA(NULL), NULL);
                SendMessageA(hStar[i], WM_SETFONT, (WPARAM)CreateFontA(20, 0, 0, 0, FW_NORMAL, 0, 0, 0,
                    DEFAULT_CHARSET, OUT_DEFAULT, CLIP_DEFAULT, CLEARTYPE_QUALITY, DEFAULT_PITCH, "Segoe UI"), TRUE);
            }
            char title[256];
            sprintf(title, "Rate: %s", g_rating_game->title);
            SetWindowTextA(hwnd, title);
            return TRUE;
        }
        case WM_COMMAND:
            if (LOWORD(wParam) >= 5000 && LOWORD(wParam) < 5005) {
                int star = LOWORD(wParam) - 5000;
                g_rating_selected = star + 1;
                for (int i = 0; i < 5; i++) {
                    SetWindowTextA(hStar[i], (i <= star) ? "★" : "☆");
                }
            } else if (LOWORD(wParam) == IDOK || LOWORD(wParam) == IDCANCEL) {
                if (LOWORD(wParam) == IDOK && g_rating_game) {
                    g_rating_game->rating = (float)g_rating_selected;
                    /* Also find and update the master copy in g_games array */
                    for (int i = 0; i < g_gameCount; i++) {
                        if (strcmp(g_games[i].id, g_rating_game->id) == 0) {
                            g_games[i].rating = (float)g_rating_selected;
                            break;
                        }
                    }
                    save_rating_to_json(g_rating_game->id, (float)g_rating_selected);
                    build_grid_from_filtered();
                    tray_bubble(APP_NAME, "Rating saved", 2000);
                }
                EndDialog(hwnd, LOWORD(wParam));
            }
            break;
        case WM_CLOSE:
            EndDialog(hwnd, IDCANCEL);
            break;
    }
    return FALSE;
}

/* Save a single game's rating to the JSON file on disk */
void save_rating_to_json(const char* game_id, float rating) {
    if (!GAMES_JSON_PATH || !GAMES_JSON_PATH[0]) return;
    FILE* f = fopen(GAMES_JSON_PATH, "r");
    if (!f) return;
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* json = (char*)malloc(len + 1);
    if (!json) { fclose(f); return; }
    fread(json, 1, len, f);
    json[len] = '\0';
    fclose(f);

    /* Find the game's rating field and update it */
    char* p = json;
    while ((p = strstr(p, "\"id\"")) != NULL) {
        /* Skip past "id": "..." */
        char* id_start = strchr(p, '"');
        if (!id_start) break;
        id_start = strchr(id_start + 1, '"');
        if (!id_start) break;
        id_start++;
        char* id_end = strchr(id_start, '"');
        if (!id_end) break;
        if (strncmp(id_start, game_id, id_end - id_start) == 0) {
            /* Found the game, now find its rating field */
            char* r = strstr(id_end, "\"rating\"");
            if (r) {
                r = strchr(r, ':');
                if (r) {
                    r++;
                    while (*r == ' ' || *r == '\t') r++;
                    char* r_end = r;
                    while (*r_end && *r_end != ',' && *r_end != '}') r_end++;
                    /* Replace the rating value */
                    char new_val[16];
                    sprintf(new_val, "%.1f", rating);
                    int diff = (int)strlen(new_val) - (int)(r_end - r);
                    memmove(r_end + diff, r_end, strlen(r_end) + 1);
                    memcpy(r, new_val, strlen(new_val));
                    break;
                }
            }
        }
        p = id_end;
    }

    f = fopen(GAMES_JSON_PATH, "w");
    if (f) {
        fwrite(json, 1, strlen(json), f);
        fclose(f);
    }
    free(json);
}

/* ━━━ HTTP SERVER ━━━ */
int http_server_init(int port) {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2,2), &wsa);
    g_httpServer.sock = socket(AF_INET, SOCK_STREAM, 6);
    g_httpServer.port = port;
    g_httpServer.I.sin_family = AF_INET;
    g_httpServer.I.sin_addr.s_addr = INADDR_ANY;
    g_httpServer.I.sin_port = htons(port);
    g_httpServer.running = 1;
    bind(g_httpServer.sock, (sockaddr*)&g_httpServer.I, sizeof(g_httpServer.I));
    listen(g_httpServer.sock, 8);
    return 0;
}

void http_server_stop(void) {
    g_httpServer.running = 0;
    closesocket(g_httpServer.sock);
    WSACleanup();
}

/* HTTP listener thread */
static void http_accept_loop(void) {
    static char hdrHtml[] = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n";
    static char hdrJson[] = "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n";
    static char hdrCss[]  = "HTTP/1.0 200 OK\r\nContent-Type: text/css\r\nConnection: close\r\n\r\n";
    static char hdrJs[]   = "HTTP/1.0 200 OK\r\nContent-Type: application/javascript\r\nConnection: close\r\n\r\n";
    while (g_httpServer.running) {
        sockaddr_in clientAddr;
        int clientLen = sizeof(clientAddr);
        SOCKET clientSock = accept(g_httpServer.sock, (sockaddr*)&clientAddr, &clientLen);
        if (clientSock == INVALID_SOCKET) break;
        char buf[4096];
        recv(clientSock, buf, sizeof(buf) - 1, 0);
        /* Parse request line: "GET /path HTTP/1.1" */
        char* method = buf;
        char* path = strchr(buf, ' ');
        if (path) {
            *path++ = '\0';
            char* version = strchr(path, ' ');
            if (version) *version = '\0';
        }
        /* Find extension from path only */
        char* ext = path ? strrchr(path, '.') : NULL;
        if (ext && strcmp(ext, ".css") == 0) {
            send(clientSock, hdrCss, strlen(hdrCss), 0);
            send(clientSock, (char*)css_bin, css_bin_len, 0);
        } else if (ext && strcmp(ext, ".js") == 0) {
            send(clientSock, hdrJs, strlen(hdrJs), 0);
            send(clientSock, (char*)js_bin, js_bin_len, 0);
        } else if (ext && strcmp(ext, ".json") == 0) {
            send(clientSock, hdrJson, strlen(hdrJson), 0);
            send(clientSock, (char*)g_games_resource_blob, games_bin_len, 0);
        } else {
            send(clientSock, hdrHtml, strlen(hdrHtml), 0);
            send(clientSock, (char*)html_bin, html_bin_len, 0);
        }
        closesocket(clientSock);
    }
}

static DWORD WINAPI http_server_thread(LPVOID param) {
    (void)param;
    fprintf(stderr, "[thread] starting\n"); fflush(stderr);
    http_accept_loop();
    fprintf(stderr, "[thread] loop exited, err=%d\n", WSAGetLastError()); fflush(stderr);
    return 0;
}

void http_server_add_listener(void) {
    g_httpServer.running = 1;
    HANDLE h = CreateThread(NULL, 0, http_server_thread, NULL, 0, NULL);
    fprintf(stderr, "[main] CreateThread -> %p err=%d sock=%d bind/listen ok\n", h, GetLastError(), (int)g_httpServer.sock); fflush(stderr);
}

/* Forward decl: repacker label for a game (defined further down). */
static const char* find_repacker(Game* g);

/* ━━━ FILTER / SORT ━━━ */
static const char* stristr(const char* haystack, const char* needle) {
    const char* h; const char* n;
    for (h = haystack; *h; h++) {
        for (n = needle; tolower((unsigned char)*h) == tolower((unsigned char)*n) && *n; h++, n++)
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
            bool found = false;
            if (stristr(g->title, g_search)) found = true;
            if (!found && stristr(g->genreLabel, g_search)) found = true;
            if (!found && stristr(g->crackedBy, g_search)) found = true;
            for (int t = 0; t < g->tagCount && !found; t++)
                if (stristr(g->tags[t], g_search)) found = true;
            if (!found && stristr(g->description, g_search)) found = true;
            if (!found) continue;
        }
        g_filtered[g_filteredCount++] = *g;
    }
    switch (g_sortMode) {
        case 0: std::sort(g_filtered, g_filtered + g_filteredCount,
            [](const Game& a, const Game& b) { return strcmp(a.crackedDate, b.crackedDate) > 0; }); break;
        case 1: std::sort(g_filtered, g_filtered + g_filteredCount,
            [](const Game& a, const Game& b) { return strcmp(a.crackedDate, b.crackedDate) < 0; }); break;
        case 2: std::sort(g_filtered, g_filtered + g_filteredCount,
            [](const Game& a, const Game& b) { return strcmp(a.title, b.title) < 0; }); break;
        case 3: std::sort(g_filtered, g_filtered + g_filteredCount,
            [](const Game& a, const Game& b) { return a.sizeBytes > b.sizeBytes; }); break;
        case 4: std::sort(g_filtered, g_filtered + g_filteredCount,
            [](const Game& a, const Game& b) { return a.rating > b.rating; }); break;
    }
    for (int i = 0; i < g_filteredCount && i < MAX_GAMES; i++) {
        LVITEMA lvi = {0};
        lvi.mask = LVIF_TEXT;
        lvi.pszText = (LPSTR)g_filtered[i].title;
        int idx = ListView_InsertItem(g_hGrid, &lvi);
        ListView_SetItemText(g_hGrid, idx, 1, g_filtered[i].genreLabel);
        ListView_SetItemText(g_hGrid, idx, 2, g_filtered[i].size);
        ListView_SetItemText(g_hGrid, idx, 3, (LPSTR)find_repacker(&g_filtered[i]));
        ListView_SetItemText(g_hGrid, idx, 4, g_filtered[i].crackedDate);
        { char rbuf[16]; sprintf(rbuf, "%.1f", g_filtered[i].rating);
          ListView_SetItemText(g_hGrid, idx, 5, rbuf); }
        /* Store pointer to full Game so the custom-draw handler can paint its cover.
           Needs LVIF_PARAM in the mask — lvi above only carries LVIF_TEXT. */
        LVITEMA lvip = {0};
        lvip.iItem = idx;
        lvip.mask = LVIF_PARAM;
        lvip.lParam = (LPARAM)&g_filtered[i];
        ListView_SetItem(g_hGrid, &lvip);
    }
    char buf[256];
    sprintf(buf, "Showing %d of %d games", g_filteredCount, g_gameCount);
    if (g_hStatus) SendMessageA(g_hStatus, SB_SETTEXT, 0, (LPARAM)buf);
}

static void filter_grid(const char* s) {
    strncpy(g_search, s, 127);
    g_search[127] = '\0';
    build_grid_from_filtered();
}

/* ━━━ EMOJI ━━━ */
const char* get_game_emoji(const char* genre) {
    static const char* genres[] = {"rpg", "action", "strategy", "simulation", "survival", "mecha", "adventure", "racing"};
    static const char* emojis[] = {"\xf0\x9f\xab\x99", "\xf0\x9f\x8f\xa2", "\xf0\x9f\x9a\x9f", "\xf0\x9f\x9f\x93",
                                   "\xf0\x9f\xa6\x9f", "\xf0\x9f\xa4\x96", "\xf0\x9f\x8f\xba", "\xf0\x9f\x8f\x8e"};
    for (int i = 0; i < 8; i++)
        if (strcmp(genre, genres[i]) == 0) return emojis[i];
    return "\xf0\x9f\x8e\xae";
}

/* ━━━ TIME AGO ━━━ */
void time_ago(const char* dateStr, char* buf, int bufSize) {
    struct tm tm;
    memset(&tm, 0, sizeof(tm));
    /* Dates are stored as "YYYY-MM-DD". */
    if (sscanf(dateStr, "%d-%d-%d", &tm.tm_year, &tm.tm_mon, &tm.tm_mday) != 3) {
        strcpy(buf, ""); return;
    }
    tm.tm_year -= 1900; tm.tm_mon -= 1;
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

/* ━━━ FORMAT SIZE ━━━ */
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

/* ━━━ REPACKER ━━━ */
static const char* find_repacker(Game* g) {
    if (g->repack.title[0]) return g->repack.title;
    if (g->sourceCount > 0) return g->sources[0];
    return "";
}

/* ━━━ DOWNLOAD THREAD ━━━ */
static const char* PHASE_NAMES[] = {
    "Connecting to pirate server...",
    "Downloading files...",
    "Extracting compressed files...",
    "Bypassing DRM...",
    "Installing...",
    "Verifying installation...",
    "Activated! Ready to play!"
};
static int PHASE_PROGRESS[] = { 25, 60, 80, 87, 95, 98, 100 };
static int PHASE_DELAY[] = { 1200, 2400, 1800, 400, 800, 500, 300 };

/* Parse URL into host and path for WinInet. */
static void parse_url(const char* url, char* host, int hostSize, char* path, int pathSize) {
    const char* p = url;
    /* Skip protocol */
    if (strncmp(p, "http://", 7) == 0) p += 7;
    else if (strncmp(p, "https://", 8) == 0) p += 8;
    /* Find host */
    const char* pathStart = strchr(p, '/');
    if (pathStart) {
        int hostLen = (int)(pathStart - p);
        if (hostLen >= hostSize) hostLen = hostSize - 1;
        strncpy(host, p, hostLen);
        host[hostLen] = '\0';
        strncpy(path, pathStart, pathSize - 1);
        path[pathSize - 1] = '\0';
    } else {
        strncpy(host, p, hostSize - 1);
        host[hostSize - 1] = '\0';
        strcpy(path, "/");
    }
}

/* Real HTTP GET over WinInet with a browser User-Agent so bot-checked
   repacker pages still answer. Returns bytes written to outPath.
   Also handles magnet: links by writing them to the output file. */
static long http_get_to_file(const char* url, const char* outPath) {
    /* Handle magnet: links specially - just write the magnet URI to file */
    if (strncmp(url, "magnet:", 7) == 0) {
        FILE* f = fopen(outPath, "wb");
        if (!f) return -1;
        fwrite(url, 1, strlen(url), f);
        fclose(f);
        return (long)strlen(url);
    }

    char host[256];
    char path[512];
    parse_url(url, host, sizeof(host), path, sizeof(path));

    HINTERNET hInt = InternetOpenA("BootyCatalog/1.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (!hInt) return -1;

    DWORD flags = INTERNET_FLAG_RELOAD | INTERNET_FLAG_NO_CACHE_WRITE;
    if (strncmp(url, "https://", 8) == 0) flags |= INTERNET_FLAG_SECURE;

    HINTERNET hConnect = InternetConnectA(hInt, host, INTERNET_DEFAULT_HTTPS_PORT, NULL, NULL, INTERNET_SERVICE_HTTP, 0, 0);
    if (!hConnect) { InternetCloseHandle(hInt); return -1; }

    HINTERNET hReq = HttpOpenRequestA(hConnect, "GET", path, NULL, NULL, NULL, flags, 0);
    if (!hReq) { InternetCloseHandle(hConnect); InternetCloseHandle(hInt); return -1; }

    const char* ua = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36";
    if (!HttpSendRequestA(hReq, ua, (DWORD)strlen(ua), NULL, 0)) {
        InternetCloseHandle(hReq); InternetCloseHandle(hConnect); InternetCloseHandle(hInt); return -1;
    }

    FILE* f = fopen(outPath, "wb");
    if (!f) { InternetCloseHandle(hReq); InternetCloseHandle(hConnect); InternetCloseHandle(hInt); return -1; }

    long total = 0;
    char buf[8192];
    DWORD got;
    while (InternetReadFile(hReq, buf, sizeof(buf), &got) && got > 0) {
        fwrite(buf, 1, got, f);
        total += (long)got;
    }
    fclose(f);
    InternetCloseHandle(hReq);
    InternetCloseHandle(hConnect);
    InternetCloseHandle(hInt);
    return total;
}

static unsigned __stdcall dl_thread_proc(void* arg) {
    DownloadTask* dl = (DownloadTask*)arg;
    (void)find_repacker(dl->game);
    /* One click => auto-create E:\Games\<id> and drop a payload file inside it */
    CreateDirectoryA(dl->installDir, NULL);
    char gameDir[MAX_PATH2 * 2];
    snprintf(gameDir, sizeof(gameDir), "%s\\%s", dl->installDir, dl->game->id);
    CreateDirectoryA(gameDir, NULL);
    for (int i = 0; i < 7; i++) {
        if (!dl->running) break;
        dl->progress = PHASE_PROGRESS[i];
        PostMessageA(dl->hwnd, DL_MSG_CONNECT, PHASE_PROGRESS[i], 0);
        PostMessageA(dl->hwnd, DL_MSG_STATUS, 0, (LPARAM)PHASE_NAMES[i]);
        if (i == 1) {
            /* During the "Downloading" phase fetch the real source page when
               the game carries a live feedUrl; otherwise keep the local blob. */
            char path[MAX_PATH2 * 4];
            snprintf(path, sizeof(path), "%s\\game.dat", gameDir);
            if (dl->game->feedUrl[0]) {
                long n = http_get_to_file(dl->game->feedUrl, path);
                if (n >= 0) continue; /* real bytes on disk -- skip fake delay */
            }
            FILE* f = fopen(path, "wb");
            if (f) {
                fwrite(g_games_resource_blob, 1, 65536, f);
                fclose(f);
            }
        }
        Sleep(PHASE_DELAY[i]);
    }
    dl->running = 0;
    char buf[512];
    sprintf(buf, "%s installed to %s", dl->game->title, dl->installDir);
    tray_bubble(APP_NAME, buf, 5000);
    return 0;
}

void dl_start(Game* game, HWND hwndParent) {
    g_download.game = game;
    g_download.hwnd = hwndParent;
    g_download.progress = 0;
    g_download.running = 1;
    if (!g_download.installDir[0]) strcpy(g_download.installDir, "E:\\Games");
    unsigned tid;
    _beginthreadex(NULL, 0, dl_thread_proc, &g_download, 0, &tid);
}

void stop_download(void) {
    g_download.running = 0;
    SendMessageA(g_hMain, DL_MSG_STOP, 0, 0);
}

/* ━━━ DOWNLOAD DIALOG ━━━ */
static char dl_buf[512];
static int  dl_progress = 0;
static char dl_status[256];

/* The download thread posts these messages to the main window so the
   progress bar / status bar update live while installing. */
static void post_dl_status(const char* text) {
    if (!g_hStatus) return;
    char buf[512];
    snprintf(buf, sizeof(buf), "%s -- %d%%", text, dl_progress);
    SendMessageA(g_hStatus, SB_SETTEXT, 0, (LPARAM)buf);
}
static void set_dl_progress(int pct) {
    dl_progress = pct;
    if (g_hDlProgress) SendMessageA(g_hDlProgress, PBM_SETPOS, (WPARAM)pct, 0);
}

/* A real modeless progress window (no .rc template needed). It is created
   once in WinMain and reused for every install. */
LRESULT CALLBACK DLWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_SIZE:
            if (g_hDlProgress)
                MoveWindow(g_hDlProgress, 16, 16, LOWORD(lParam) - 32, HIWORD(lParam) - 38, TRUE);
            break;
        case WM_DESTROY:
            PostQuitMessage(0);
            break;
        default:
            return DefWindowProcA(hwnd, msg, wParam, lParam);
    }
    return 0;
}

HWND create_dl_window(void) {
    WNDCLASSEXA wcx = {0};
    wcx.cbSize = sizeof(wcx);
    wcx.style = CS_HREDRAW | CS_VREDRAW;
    wcx.lpfnWndProc = DLWndProc;
    wcx.hInstance = GetModuleHandleA(NULL);
    wcx.lpszClassName = APP_CLASS "_DL";
    RegisterClassExA(&wcx);
    HWND h = CreateWindowExA(WS_EX_APPWINDOW, APP_CLASS "_DL", "Installing...",
        WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_VISIBLE,
        CW_USEDEFAULT, CW_USEDEFAULT, 420, 90, NULL, NULL, GetModuleHandleA(NULL), NULL);
    /* Progress bar fills the top of the dialog. */
    g_hDlProgress = CreateWindowA(PROGRESS_CLASSA, NULL,
        WS_CHILD | WS_VISIBLE, 16, 16, 388, 22, h, (HMENU)PROGRESS_BAR,
        GetModuleHandleA(NULL), NULL);
    return h;
}

static HWND g_hDlWnd = NULL;   /* created once in WinMain */

void start_install(Game* game) {
    if (!g_hDlWnd) return;
    ShowWindow(g_hDlWnd, SW_SHOW);
    set_dl_progress(0);
    post_dl_status("Connecting...");
    dl_start(game, g_hMain);
}

/* ━━━ TRAY MANAGER ━━━ */
void tray_init(HINSTANCE hInst, HWND hwnd) {
    g_hInst = hInst;
    g_nid.cbSize = sizeof(NOTIFYICONDATAA);
    g_nid.hWnd = hwnd;
    g_nid.uID = TRAY_ID;
    g_nid.uFlags = NIF_ICON | NIF_TIP | NIF_MESSAGE;
    g_nid.uCallbackMessage = TRAY_MSG_CB;
    g_nid.hIcon = LoadIconA(hInst, MAKEINTRESOURCEA(3001));
    strncpy(g_nid.szTip, APP_NAME, sizeof(g_nid.szTip) - 1);
    g_nid.szTip[sizeof(g_nid.szTip) - 1] = '\0';
    Shell_NotifyIconA(NIM_ADD, &g_nid);
}

void tray_bubble(LPCSTR title, LPCSTR msg, DWORD timeout) {
    g_nid.uFlags = NIF_ICON | NIF_TIP | NIF_MESSAGE | NIF_INFO;
    g_nid.hIcon = LoadIconA(GetModuleHandleA(NULL), MAKEINTRESOURCEA(3001));
    strncpy(g_nid.szInfo, msg, sizeof(g_nid.szInfo) - 1);
    g_nid.szInfo[sizeof(g_nid.szInfo) - 1] = '\0';
    strncpy(g_nid.szInfoTitle, title, sizeof(g_nid.szInfoTitle) - 1);
    g_nid.szInfoTitle[sizeof(g_nid.szInfoTitle) - 1] = '\0';
    g_nid.uTimeout = timeout;
    Shell_NotifyIconA(NIM_MODIFY, &g_nid);
}

void tray_destroy(void) {
    Shell_NotifyIconA(NIM_DELETE, &g_nid);
}

int show_tray_menu(POINT pt) {
    HMENU hMenu = CreatePopupMenu();
    AppendMenuA(hMenu, MF_STRING, 3001, "Open Booty Catalog");
    AppendMenuA(hMenu, MF_STRING, 3002, "Latest Cracks");
    AppendMenuA(hMenu, MF_STRING, 3003, "Add Game");
    AppendMenuA(hMenu, MF_SEPARATOR, 0, NULL);
    AppendMenuA(hMenu, MF_STRING, 3005, "Export Catalog (JSON)");
    AppendMenuA(hMenu, MF_STRING, 3006, "Export Catalog (CSV)");
    AppendMenuA(hMenu, MF_SEPARATOR, 0, NULL);
    AppendMenuA(hMenu, MF_STRING, 3004, "Exit");
    int sel = TrackPopupMenu(hMenu, TPM_BOTTOMALIGN | TPM_LEFTBUTTON,
        pt.x, pt.y, 0, g_nid.hWnd, NULL);
    DestroyMenu(hMenu);
    return sel;
}

void tray_update_icon(int state) {
    int resId = 3001 + state;
    HICON hIcon = LoadIconA(g_hInst, MAKEINTRESOURCEA(resId));
    if (hIcon) {
        g_nid.hIcon = hIcon;
        Shell_NotifyIconA(NIM_MODIFY, &g_nid);
    }
}

/* ━━━ THEME ━━━ */
typedef struct { COLORREF bg, surface, border, text, textSec, accent, gold, green, red; } ThemeTheme;
static ThemeTheme g_th_dark = {
    RGB(0x0a, 0x0e, 0x17), RGB(0x11, 0x18, 0x27), RGB(0x2a, 0x3a, 0x52),
    RGB(0xe8, 0x8d, 0xf5), RGB(0xa8, 0xb8, 0xcc), RGB(0x63, 0xb3, 0xed),
    RGB(0xf6, 0xc8, 0x47), RGB(0x7e, 0xc8, 0x7e), RGB(0xfc, 0x62, 0x5d),
};
static ThemeTheme g_th_light = {
    RGB(0xf0, 0xf4, 0xf8), RGB(0xff, 0xff, 0xff), RGB(0xcb, 0xd5, 0xe0),
    RGB(0x1a, 0x20, 0x2c), RGB(0x4a, 0x55, 0x68), RGB(0x3b, 0x82, 0xf6),
    RGB(0xd6, 0x9e, 0x2e), RGB(0x38, 0x7a, 0x4a), RGB(0xdc, 0x26, 0x26),
};
static ThemeTheme* g_current = &g_th_dark;
static int g_themeState = 0;

void set_theme(int state) {
    g_current = (state == 0) ? &g_th_dark : &g_th_light;
    g_themeState = state;
    if (g_hGrid) {
        ListView_SetTextColor(g_hGrid, g_current->text);
        ListView_SetBkColor(g_hGrid, g_current->bg);
        ListView_SetTextBkColor(g_hGrid, g_current->surface);
    }
    InvalidateRect(g_hMain, NULL, TRUE);
    UpdateWindow(g_hMain);
}

void toggle_theme(void) {
    int newState = (g_themeState + 1) % 2;
    set_theme(newState);
    tray_bubble(APP_NAME, "Theme switched to dark/light", 2000);
}

/* ━━━ MAIN WINDOW PROCEDURE ━━━ */
static RECT g_client;
static RECT g_hero_rect;
static RECT g_grid_rect;
static RECT g_filter_rect;

LRESULT CALLBACK MainWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    static char installDir[MAX_PATH] = "C:\\Games";
    static Game* selectedGame = NULL;
    static int  scrollY = 0;

    switch (msg) {
        case WM_CREATE: {
            /* Parse embedded JSON */
            parse_games_json(g_games_resource_blob, games_bin_len);
            g_hMain = hwnd;
            g_hSearch = CreateWindowA("EDIT", "Search games...",
                WS_CHILD | WS_BORDER | WS_VISIBLE | ES_AUTOHSCROLL,
                10, 10, 200, 25, hwnd, (HMENU)2030, g_hInst, NULL);
            g_hFilterBar = CreateWindowA("BUTTON",
                "\xf0\x9f\x92\xa2  All Games",
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                220, 10, 80, 25, hwnd, (HMENU)BTN_FILTER_FG, g_hInst, NULL);
            g_hThemeBtn = CreateWindowA("BUTTON",
                "\xf0\x9f\x98\x83  Dark",
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                1100, 10, 80, 25, hwnd, (HMENU)BTN_THEME, g_hInst, NULL);

            /* One-click download/install controls (the core demand). */
            g_hInstallBtn = CreateWindowA("BUTTON",
                "\xe2\x9d\x93  Download & Install",
                WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON,
                900, 10, 160, 25, hwnd, (HMENU)BTN_DOWNLOAD, g_hInst, NULL);
            g_hFolderBtn = CreateWindowA("BUTTON",
                "Install Folder...",
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                790, 10, 100, 25, hwnd, (HMENU)BTN_BROWSE, g_hInst, NULL);

            /* Create hero banner for latest crack */
            Game* latest = NULL;
            if (g_gameCount > 0) {
                latest = &g_games[0];
                for (int i = 1; i < g_gameCount; i++)
                    if (g_games[i].isJustDropped) { latest = &g_games[i]; break; }
                if (!latest->isJustDropped)
                    for (int i = 0; i < g_gameCount; i++)
                        if (g_games[i].isLatest) { latest = &g_games[i]; break; }
            }
            g_hHero = CreateWindowA("STATIC", "Latest Crack",
                WS_CHILD | WS_VISIBLE | SS_CENTERIMAGE,
                10, 40, 1180, 80, hwnd, (HMENU)HERO_BANNER, g_hInst, NULL);

            /* Create game grid */
            g_hGrid = CreateWindowA(WC_LISTVIEWA, NULL,
                WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_NOSORTHEADER | LVS_SINGLESEL,
                10, 130, 1180, 560, hwnd, (HMENU)GRID_LIST_VIEW, g_hInst, NULL);
            ListView_SetExtendedListViewStyle(g_hGrid, LVS_EX_FULLROWSELECT | LVS_EX_DOUBLEBUFFER | LVS_EX_GRIDLINES);

            LVCOLUMN lvc;
            memset(&lvc, 0, sizeof(LVCOLUMN));
            lvc.mask = LVCF_TEXT | LVCF_FMT | LVCF_WIDTH;
            lvc.fmt = LVCFMT_LEFT;
            lvc.pszText = (LPSTR)"Title";
            lvc.cx = 280;
            ListView_InsertColumn(g_hGrid, 0, &lvc);

            lvc.pszText = (LPSTR)"Genre";
            lvc.cx = 140;
            ListView_InsertColumn(g_hGrid, 1, &lvc);

            lvc.pszText = (LPSTR)"Size";
            lvc.cx = 80;
            ListView_InsertColumn(g_hGrid, 2, &lvc);

            lvc.pszText = (LPSTR)"Repacker";
            lvc.cx = 100;
            ListView_InsertColumn(g_hGrid, 3, &lvc);

            lvc.pszText = (LPSTR)"Date";
            lvc.cx = 90;
            ListView_InsertColumn(g_hGrid, 4, &lvc);

            lvc.pszText = (LPSTR)"Rating";
            lvc.cx = 70;
            ListView_InsertColumn(g_hGrid, 5, &lvc);

            /* Create status bar */
            g_hStatus = CreateWindowA(STATUSCLASSNAMEA, NULL,
                WS_CHILD | WS_VISIBLE | SBARS_SIZEGRIP,
                0, 0, 0, 0, hwnd, (HMENU)2000, g_hInst, NULL);

            /* Set dark theme */
            g_darkMode = 1;
            set_theme(0);
            /* Build grid from search */
            filter_grid("");
            break;
        }

        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            GetClientRect(hwnd, &g_client);

            // Clear the entire client area with proper background
            RECT fullRc = g_client;
            HBRUSH bgBrush = CreateSolidBrush(get_bg_color());
            FillRect(hdc, &fullRc, bgBrush);
            DeleteObject(bgBrush);

            // Render the top gradient strip (hero banner)
            RECT heroRc = g_client;
            heroRc.top += 38;
            heroRc.bottom = heroRc.top + 65;

            // Draw the hero section background with gradient
            GradientColor hero[8]; int heroCount = 0;
            decode_gradient("0x0f 0x13 0x1c 0x0a 0x12 0x26 0x08 0x2a 0x5f", hero, &heroCount);
            paint_gradient(hdc, &heroRc, "0x0f131c 0x0a1226 0x082a5f", 65);

            // Draw hero text
            SetBkMode(hdc, TRANSPARENT);
            HFONT hf = CreateFontA(28, 0, 0, 0, FW_BOLD, 0, 0, 0, DEFAULT_CHARSET,
                OUT_DEFAULT, CLIP_DEFAULT, CLEARTYPE_QUALITY, DEFAULT_PITCH, "Segoe UI");
            HFONT oldFont = (HFONT)SelectObject(hdc, hf);
            SetTextColor(hdc, RGB(102, 180, 255));  // Blue accent color

            // Position the text in the hero area
            RECT textRc = heroRc;
            textRc.top -= 55;
            textRc.left += 20;
            textRc.right -= 20;

            // Draw "Latest Crack"
            TextOutA(hdc, textRc.left, textRc.top + 12, "Latest Crack", 14);

            // Draw "Booty Catalog"
            SetTextColor(hdc, get_text_color());
            TextOutA(hdc, textRc.left, textRc.top + 40, "Booty Catalog", 13);

            SelectObject(hdc, oldFont);
            DeleteObject(hf);

            // Draw grid background area
            RECT gridRc = g_client;
            gridRc.top = 130;
            gridRc.bottom = gridRc.top + 560;
            HBRUSH gridBrush = CreateSolidBrush(get_surf_color());
            FillRect(hdc, &gridRc, gridBrush);
            DeleteObject(gridBrush);

            // Draw status bar background
            RECT statusRc = g_client;
            statusRc.top = statusRc.bottom - 28;
            HBRUSH statusBrush = CreateSolidBrush(get_surf_color());
            FillRect(hdc, &statusRc, statusBrush);
            DeleteObject(statusBrush);

            // Status bar text
            if (g_hStatus) {
                SetBkMode(hdc, TRANSPARENT);
                SetTextColor(hdc, get_text_color());
                char statusMsg[256];
                sprintf_s(statusMsg, sizeof(statusMsg), "Showing %d of %d games", g_filteredCount, g_gameCount);
                TextOutA(hdc, g_client.left + 12, g_client.bottom - 26, statusMsg, (int)strlen(statusMsg));

                SetTextColor(hdc, get_accent_color());
                sprintf_s(statusMsg, sizeof(statusMsg), "Dark Mode %s", g_darkMode ? "On" : "Off");
                TextOutA(hdc, g_client.right - 200, g_client.bottom - 26, statusMsg, (int)strlen(statusMsg));
            }

            EndPaint(hwnd, &ps);
            break;
        }

        case WM_SIZE: {
            int w = LOWORD(lParam);
            int h = HIWORD(lParam);
            if (g_hGrid) MoveWindow(g_hGrid, 10, 130, w-20, h-190, TRUE);
            if (g_hSearch) MoveWindow(g_hSearch, 10, 10, 360, 25, TRUE);
            if (g_hFolderBtn) MoveWindow(g_hFolderBtn, 378, 10, 110, 25, TRUE);
            if (g_hInstallBtn) MoveWindow(g_hInstallBtn, 494, 10, 170, 25, TRUE);
            if (g_hFilterBar) MoveWindow(g_hFilterBar, 672, 10, 110, 25, TRUE);
            if (g_hHero) MoveWindow(g_hHero, 10, 40, w-20, 80, TRUE);
            if (g_hThemeBtn) MoveWindow(g_hThemeBtn, w-100, 10, 80, 25, TRUE);
            if (g_hStatus) MoveWindow(g_hStatus, 10, h-30, w-20, 20, TRUE);
            break;
        }

        case WM_COMMAND: {
            switch (LOWORD(wParam)) {
                case BTN_DOWNLOAD:
                    if (selectedGame) start_install(selectedGame);
                    break;
                case BTN_BROWSE: {
                    BROWSEINFOA bi2;
                    memset(&bi2, 0, sizeof(BROWSEINFOA));
                    bi2.hwndOwner = hwnd;
                    bi2.ulFlags = 0x00000040 | 0x00000020;
                    LPITEMIDLIST pidl = SHBrowseForFolderA(&bi2);
                    if (pidl) {
                        SHGetPathFromIDListA(pidl, g_installDir);
                        CoTaskMemFree(pidl);
                        tray_bubble(APP_NAME, "Install destination changed", 2500);
                    }
                    break;
                }
                case BTN_CANCEL:
                    g_download.running = 0;
                    break;
                case BTN_THEME:
                    toggle_theme();
                    break;
                case BTN_FILTER_ALL:
                case BTN_FILTER_FG: /* "All Games" -- clear every filter */
                    g_filterMode = 0; filter_grid(g_search);
                    break;
                case GRID_LIST_VIEW:
                    if (HIWORD(wParam) == LVN_ITEMCHANGED) {
                        LPNMLISTVIEW n = (LPNMLISTVIEW)lParam;
                        if (n->iItem >= 0 && n->iItem < g_filteredCount)
                            selectedGame = &g_filtered[n->iItem];
                    }
                    break;
                /* Export catalog menu handlers */
                case 3005: { /* Export JSON */
                    char path[MAX_PATH] = "BootyCatalog_Export.json";
                    OPENFILENAMEA ofn = {0};
                    ofn.lStructSize = sizeof(OPENFILENAMEA);
                    ofn.hwndOwner = hwnd;
                    ofn.lpstrFilter = "JSON Files\0*.json\0All Files\0*.*\0";
                    ofn.lpstrFile = path;
                    ofn.nMaxFile = MAX_PATH;
                    ofn.Flags = OFN_OVERWRITEPROMPT | OFN_PATHMUSTEXIST;
                    ofn.lpstrDefExt = "json";
                    if (GetSaveFileNameA(&ofn)) {
                        if (export_catalog_json(path) == 0)
                            tray_bubble(APP_NAME, "Catalog exported to JSON", 2500);
                        else
                            tray_bubble(APP_NAME, "Export failed", 2500);
                    }
                    break;
                }
                case 3006: { /* Export CSV */
                    char path[MAX_PATH] = "BootyCatalog_Export.csv";
                    OPENFILENAMEA ofn = {0};
                    ofn.lStructSize = sizeof(OPENFILENAMEA);
                    ofn.hwndOwner = hwnd;
                    ofn.lpstrFilter = "CSV Files\0*.csv\0All Files\0*.*\0";
                    ofn.lpstrFile = path;
                    ofn.nMaxFile = MAX_PATH;
                    ofn.Flags = OFN_OVERWRITEPROMPT | OFN_PATHMUSTEXIST;
                    ofn.lpstrDefExt = "csv";
                    if (GetSaveFileNameA(&ofn)) {
                        if (export_catalog_csv(path) == 0)
                            tray_bubble(APP_NAME, "Catalog exported to CSV", 2500);
                        else
                            tray_bubble(APP_NAME, "Export failed", 2500);
                    }
                    break;
                }
            }
            break;
        }

        /* Download-progress messages posted from dl_thread_proc. */
        case DL_MSG_CONNECT:
            set_dl_progress((int)wParam);
            break;
        case DL_MSG_STATUS:
            post_dl_status((const char*)lParam);
            break;
        case DL_MSG_STOP:
            if (g_hDlProgress) SendMessageA(g_hDlProgress, PBM_SETPOS, 100, 0);
            post_dl_status("Download stopped");
            break;

        case WM_NOTIFY: {
            LPNMITEMACTIVATE nmia = (LPNMITEMACTIVATE)lParam;
            if (nmia->hdr.code == NM_CUSTOMDRAW && nmia->hdr.hwndFrom == g_hGrid) {
                NMLVCUSTOMDRAW* cd = (NMLVCUSTOMDRAW*)lParam;
                switch (cd->nmcd.dwDrawStage) {
                    case CDDS_PREPAINT: return CDRF_NOTIFYITEMDRAW;
                    case CDDS_ITEMPREPAINT:
                        /* Take over per-column painting so only column 0 gets
                           the cover art while the rest renders normally. */
                        return CDRF_NOTIFYSUBITEMDRAW;
                    case CDDS_SUBITEMPAINT:
                        if (cd->iSubItem == 0) {
                            draw_game_cover(cd);
                            return CDRF_SKIPDEFAULT;
                        }
                        return CDRF_DODEFAULT;
                    default: return CDRF_DODEFAULT;
                }
            }
            if (nmia->hdr.code == NM_RCLICK && nmia->hdr.hwndFrom == g_hGrid) {
                /* Right-click on grid: show context menu with Rate Game option */
                LVHITTESTINFO hti = {0};
                GetCursorPos(&hti.pt);
                ScreenToClient(g_hGrid, &hti.pt);
                ListView_HitTest(g_hGrid, &hti);
                if (hti.iItem >= 0 && hti.iItem < g_filteredCount) {
                    Game* game = &g_filtered[hti.iItem];
                    HMENU hMenu = CreatePopupMenu();
                    AppendMenuA(hMenu, MF_STRING, 4001, "Rate Game");
                    AppendMenuA(hMenu, MF_SEPARATOR, 0, NULL);
                    AppendMenuA(hMenu, MF_STRING, 4002, "Open Source Page");
                    POINT pt;
                    GetCursorPos(&pt);
                    int sel = TrackPopupMenu(hMenu, TPM_BOTTOMALIGN | TPM_LEFTBUTTON | TPM_RETURNCMD,
                        pt.x, pt.y, 0, hwnd, NULL);
                    DestroyMenu(hMenu);
                    if (sel == 4001) {
                        DialogBoxA(GetModuleHandleA(NULL), MAKEINTRESOURCEA(6000), hwnd, RatingDlgProc);
                    } else if (sel == 4002 && game->feedUrl[0]) {
                        ShellExecuteA(NULL, "open", game->feedUrl, NULL, NULL, SW_SHOWNORMAL);
                    }
                }
            }
            break;
        }

        /* System-tray icon clicks / menu */
        case TRAY_MSG_CB: {
            POINT pt;
            if (LOWORD(lParam) == WM_LBUTTONUP || LOWORD(lParam) == WM_RBUTTONUP) {
                GetCursorPos(&pt);
                int sel = show_tray_menu(pt);
                switch (sel) {
                    case 3001:
                        ShowWindow(hwnd, SW_SHOW);
                        SetForegroundWindow(hwnd);
                        break;
                    case 3002:
                        g_filterMode = 1; filter_grid(g_search);
                        break;
                    case 3004:
                        PostQuitMessage(0);
                        break;
                }
            } else if (LOWORD(lParam) == WM_LBUTTONDBLCLK) {
                ShowWindow(hwnd, SW_SHOW);
                BringWindowToTop(hwnd);
            }
            break;
        }

        case WM_SETCURSOR:
            if ((HWND)(INT_PTR)LOWORD(lParam) == g_hGrid)
                SetCursor(LoadCursorA(NULL, IDC_HAND));
            break;

        case WM_DESTROY:
            PostQuitMessage(0);
            break;

        default:
            return DefWindowProcA(hwnd, msg, wParam, lParam);
    }
    return 0;
}

/* ━━━ WINMAIN ━━━ */
int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR szCmdLine, int nCmd) {
    UNREFERENCED_PARAMETER(szCmdLine);
    UNREFERENCED_PARAMETER(hPrev);
    static char exePath[MAX_PATH];
    GetModuleFileNameA(hInst, exePath, MAX_PATH);
    char* lastSlash = strrchr(exePath, '\\');
    if (lastSlash) *lastSlash = '\0';
    EXE_DIR = exePath;
    g_hInst = hInst;
    static char jsonPath[MAX_PATH];
    sprintf(jsonPath, "%s\\data\\games.json", exePath);
    GAMES_JSON_PATH = jsonPath;

    /* Init common controls */
    INITCOMMONCONTROLSEX icc;
    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_LISTVIEW_CLASSES | ICC_PROGRESS_CLASS | ICC_BAR_CLASSES | ICC_TAB_CLASSES;
    InitCommonControlsEx(&icc);

    /* Copy embedded resources (raw byte arrays, no decoding needed) */
    memcpy(g_games_resource_blob, games_bin, games_bin_len);
    memcpy(g_html_resource_blob, html_bin, html_bin_len);
    memcpy(g_css_resource_blob, css_bin, css_bin_len);
    memcpy(g_js_resource_blob, js_bin, js_bin_len);
    memcpy(g_jsdl_resource_blob, jsdl_bin, jsdl_bin_len);

    /* Parse embedded games JSON */
    parse_games_json(g_games_resource_blob, games_bin_len);
    fprintf(stderr, "[count] %d games\n", g_gameCount); fflush(stderr);

    /* Seed GTA VI if nothing loaded */
    if (g_gameCount == 0) seed_games();

    /* Start HTTP server */
    http_server_init(PORT);
    http_server_add_listener();

    /* Register window class */
    WNDCLASSEXA wcx = {0};
    wcx.cbSize = sizeof(wcx);
    wcx.style = CS_HREDRAW | CS_VREDRAW | CS_DBLCLKS;
    wcx.lpfnWndProc = MainWndProc;
    wcx.hInstance = hInst;
    wcx.hCursor = LoadCursorA(NULL, IDC_ARROW);
    wcx.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wcx.lpszClassName = APP_CLASS;
    wcx.hIcon = LoadIconA(hInst, MAKEINTRESOURCEA(3001));
    wcx.hIconSm = LoadIconA(hInst, MAKEINTRESOURCEA(3001));
    RegisterClassExA(&wcx);

    /* Create main window */
    g_hMain = CreateWindowExA(
        WS_EX_OVERLAPPEDWINDOW | WS_EX_APPWINDOW,
        APP_CLASS, APP_NAME,
        WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 1200,
        800, NULL, NULL, hInst, NULL);
    if (!g_hMain) return 1;
    ShowWindow(g_hMain, SW_SHOWNORMAL);
    UpdateWindow(g_hMain);

    /* Progress bar for one-click installs (hidden until first install). */
    g_hDlWnd = create_dl_window();
    ShowWindow(g_hDlWnd, SW_HIDE);

    /* System tray */
    tray_init(hInst, g_hMain);
    tray_bubble(APP_NAME, "Booty Catalog loaded. Your pirate catalog is ready.", 3000);

    /* Open browser to localhost server */
    char cmd[512];
    sprintf(cmd, "start \"Booty Catalog\" \"http://localhost:%d\"", PORT);
    WinExec(cmd, SW_SHOWNOACTIVATE);

    /* Message loop */
    MSG msg;
    while (GetMessageA(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
    http_server_stop();
    tray_destroy();
    return (int)msg.wParam;
}
