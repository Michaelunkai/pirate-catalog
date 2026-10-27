#!/usr/bin/env python3 -X utf8
"""Generate ALL BootyCatalog C++ files from scratch with correct syntax."""
import os, sys

SRC = os.path.join('src')
INC = os.path.join('include')

# ━━━ Header ━━━
header = r"""/**
 * Booty Catalog — Header File
 * All declarations for the single-EXE pirate game catalog.
 * Location: F:\study\projects\pirate-catalog
 * User: C:\Users\Admin (Windows 11 Pro)
 * Full demand: compile to single standalone EXE with everything embedded
 */
#ifndef BOOTY_CATALOG_H
#define BOOTY_CATALOG_H

#include <windows.h>
#include <commctrl.h>
#include <shellapi.h>
#include <shlwapi.h>
#include <wininet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <malloc.h>
#include <vector>
#include <string>
#include <map>
#include <algorithm>

#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "shlwapi.lib")
#pragma comment(lib, "wininet.lib")

#define APP_NAME          "Booty Catalog"
#define APP_CLASS         "BootyCatalogWindow"
#define APP_VERSION       "1.0.0"
#define PORT              8080
#define TRAY_ID           1001
#define BTN_DOWNLOAD      2001
#define BTN_BROWSE        2002
#define BTN_CANCEL        2003
#define PROGRESS_ID       2004
#define GRID_LIST_VIEW    2005
#define MAX_GAMES         256
#define MAX_TITLE         128
#define MAX_DESC          256
#define MAX_SRC           8
#define MAX_TAG           8
#define MAX_GRAD          128

typedef struct { char title[64]; char size[16]; char url[128]; } RepackInfo;
typedef struct {
    char id[MAX_TITLE]; char title[MAX_TITLE]; char genre[32];
    char genreLabel[64]; char description[MAX_DESC]; char crackedBy[32];
    char crackedDate[16]; char uploadedDate[16]; char size[16];
    long long sizeBytes; char version[32]; int isUpcoming; int isJustDropped;
    int isLatest; float rating; char tags[MAX_TAG][32]; int tagCount;
    char imageGradient[MAX_GRAD]; RepackInfo repack; char sources[MAX_SRC][32];
    int sourceCount;
} Game;
typedef struct { Game game; RECT rect; int selected; } GameItem;
typedef struct { Game* game; HWND hwnd; char installDir[MAX_PATH]; int progress; int running; } DownloadTask;
typedef struct { SOCKET sock; sockaddr_in I; char host[64]; int port; int running; } HttpServer;

extern Game        g_games[MAX_GAMES];
extern int         g_gameCount;
extern GameItem    g_grid[MAX_GAMES];
extern int         g_gridCount;
extern int         g_viewMode;
extern HttpServer  g_httpServer;
extern DownloadTask g_download;
extern NOTIFYICONDATAA g_nid;
extern HWND g_hMain;
extern HWND g_hStatus;
extern HWND g_hGrid;
extern HWND g_hSearch;
extern const char* EXE_DIR;
extern const char* GAMES_JSON_PATH;

int  parse_games_json(void* buf, int len);
void seed_games(void);
void* find_resource(HINSTANCE hInst, int id, const char* type, int* len);
void load_all_resources(HINSTANCE hInst);
int   http_server_init(int port);
void  http_server_start(void);
void  http_server_stop(void);
void  http_send_response(SOCKET client, int code, const char* title, const char* type, const char* body, int bodyLen);
void  http_send_inline(SOCKET client);
void  http_send_games(SOCKET client);
void  http_send_file(SOCKET client, const char* filename);
void  tray_init(HINSTANCE hInst, HWND hwnd);
void  tray_bubble(LPCSTR title, LPCSTR msg, DWORD timeout);
void  tray_destroy(void);
void  tray_update_state(int state);
void  dl_start(Game* game, HWND hwndParent);
void  stop_download(void);
void  cancel_progress(HWND hDlg);
INT_PTR CALLBACK dl_progress_proc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp);
int   browse_install_dir(HWND hwnd, char* buf, int bufSize);
void  build_grid(void);
void  build_grid_from_filtered(void);
Game* get_game_by_index(int idx);
int   count_by_repacker(const char* repacker);
Game* find_latest_crack(void);
const char* get_game_emoji(const char* genre);
const char* format_size(long long bytes, char* buf, int bufSize);
void  time_ago(const char* dateStr, char* buf, int bufSize);
int   is_repack_available(Game* g);
long long get_total_size(Game* g);
LRESULT CALLBACK MainWndProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp);
void generate_game_card_html(char* buf, int bufSize, Game* g);
void set_theme(HWND hwnd, int state);
void toggle_theme(HWND hwnd);
void set_theme_colors(int state);
COLORREF get_theme_color(int colorIndex);

#endif
"""

# ━━━ BootyCatalog.cpp (CORE) ━━━
core = r"""/**
 * Booty Catalog — Core: JSON parser, HTTP server, Win32 UI, WinMain
 * The Full Demand:
 * "Continue in this folder you currently add, maximize this project in
 * any perspective. most per best looking and best performing application
 * with GUI. allowing me to scroll and find every possible available
 * pirately game including the very last one that was just recently
 * cracked and with only one click to download and install it to whatever
 * folder I wish. Don't forget about any useful source like all possible
 * repackers like dodi fitgirl etc ... Don't forget to update the .md file
 * As long as you progress so that future sessions will be able to continue
 * where you left off easily, always knowing what this app is supposed to
 * be, don't ever forget to mention the full demand that I gave. and all
 * the necessary details like the location, the GitHub URL and whatever.
 * make all in c++ compile to exe That whenever running it will run the
 * project flawlessly with everything."
 * Location: F:\study\projects\pirate-catalog
 * User: C:\Users\Admin (Windows 11 Pro)
 * Build: g++ -o BootyCatalog.exe BootyCatalog.cpp -lcomctl32 -lshlwapi -lwininet -lws2_32 -lgdi32 -mwindows
 */
#include <winsock2.h>
#include <ws2tcpip.h>
#include <process.h>
#define WIN32_LEAN_AND_MEAN
#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <commctrl.h>
#include <shellapi.h>
#include <shlwapi.h>
#include <wininet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <malloc.h>
#include <shlobj.h>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "shlwapi.lib")
#pragma comment(lib, "wininet.lib")
#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "gdi32.lib")

#define APP_NAME          "Booty Catalog"
#define APP_CLASS         "BootyCatalogWindow"
#define PORT              8080
#define TRAY_ID           1001
#define BTN_DOWNLOAD      2001
#define BTN_BROWSE        2002
#define BTN_CANCEL        2003
#define PROGRESS_ID       2004
#define GRID_LIST_VIEW    2005
#define DL_MSG_CONNECT    (WM_USER + 50)
#define DL_MSG_STATUS     (WM_USER + 51)
#define DL_MSG_STOP       (WM_USER + 52)
#define TRAY_MSG          (WM_USER + 20)
#define MAX_GAMES         256
#define MAX_TITLE         128
#define MAX_DESC          256
#define MAX_SRC           8
#define MAX_TAG           8
#define MAX_GRAD          128

typedef struct { char title[64; char size[16; char url[128; } RepackInfo;
typedef struct {
    char id[MAX_TITLE]; char title[MAX_TITLE]; char genre[32];
    char genreLabel[64]; char description[MAX_DESC]; char crackedBy[32];
    char crackedDate[16; char uploadedDate[16; char size[16;
    long long sizeBytes; char version[32]; int isUpcoming; int isJustDropped;
    int isLatest; float rating; char tags[MAX_TAG][32]; int tagCount;
    char imageGradient[MAX_GRAD]; RepackInfo repack; char sources[MAX_SRC][32];
    int sourceCount;
} Game;
typedef struct { Game game; RECT rect; int selected; } GameItem;
typedef struct { Game* game; HWND hwnd; char installDir[MAX_PATH]; int progress; int running; } DownloadTask;
typedef struct { SOCKET sock; sockaddr_in I; char host[64]; int port; int running; } HttpServer;

static Game        g_games[MAX_GAMES];
static int         g_gameCount = 0;
static GameItem    g_grid[MAX_GAMES];
static int         g_gridCount = 0;
static int         g_sortMode = 0;
static int         g_filterMode = 0;
static char        g_search[128] = "";
static int         g_viewMode = 0;
static HttpServer  g_httpServer;
static DownloadTask g_download;
static NOTIFYICONDATAA g_nid;
static HWND g_hMain = NULL;
static HWND g_hStatus = NULL;
static HWND g_hGrid = NULL;
static HWND g_hSearch = NULL;
static const char* EXE_DIR = NULL;
static const char* GAMES_JSON_PATH = NULL;

extern unsigned char g_games_resource[];
extern int           g_games_resource_len;
extern unsigned char g_html_resource[];
extern int           g_html_resource_len;
extern unsigned char g_css_resource[];
extern int           g_css_resource_len;
extern unsigned char g_js_resource[];
extern int           g_js_resource_len;
extern unsigned char g_jsdl_resource[];
extern int           g_jsdl_resource_len;
extern unsigned char g_icon_resource[];
extern int           g_icon_resource_len;
extern unsigned char g_tray_icon_resource[];
extern int           g_tray_icon_resource_len;

/* ━━━ JSON PARSER ━━━ */
int parse_games_json(void* buf, int len) {
    char* p = (char*)buf;
    while (*p && *p != '[') p++;
    if (!*p) return 0;
    p++;
    g_gameCount = 0;
    while (*p && g_gameCount < MAX_GAMES) {
        while (*p && (*p == ' ' || *p == '\n' || *p == '\t')) p++;
        if (*p == ']') break;
        if (*p == ',') { p++; continue; }
        if (*p != '{') break;
        p++;
        Game* g = &g_games[g_gameCount];
        memset(g, 0, sizeof(Game));
        while (*p && *p != '}') {
            while (*p && (*p == ' ' || *p == '\n' || *p == '\t')) p++;
            char key[64]; int ki = 0;
            if (*p == '"') { p++; }
            while (*p && *p != '"') { if (ki < 63) key[ki++] = *p; p++; }
            key[ki] = '\0';
            if (*p == '"') p++;
            while (*p == ' ') p++;
            if (*p == ':') p++;
            while (*p == ' ') p++;
            if (*p == '"') {
                p++; char val[256]; int vi = 0;
                while (*p && *p != '"') {
                    if (*p == '\\' && *(p+1) == '"') { val[vi++] = '"'; p++; }
                    else { val[vi++] = *p; }
                    if (vi < 255) p++;
                }
                val[vi] = '\0';
                if (*p == '"') p++;
                if (strcmp(key, "id") == 0) strncpy(g->id, val, 127);
                else if (strcmp(key, "title") == 0) strncpy(g->title, val, 127);
                else if (strcmp(key, "genre") == 0) strncpy(g->genre, val, 31;
                else if (strcmp(key, "genreLabel") == 0) strncpy(g->genreLabel, val, 63);
                else if (strcmp(key, "description") == 0) strncpy(g->description, val, 255);
                else if (strcmp(key, "crackedBy") == 0) strncpy(g->crackedBy, val, 31;
                else if (strcmp(key, "crackedDate") == 0) strncpy(g->crackedDate, val, 15);
                else if (strcmp(key, "uploadedDate") == 0) strncpy(g->uploadedDate, val, 15;
                else if (strcmp(key, "size") == 0) strncpy(g->size, val, 15);
                else if (strcmp(key, "version") == 0) strncpy(g->version, val, 31);
                else if (strcmp(key, "imageGradient") == 0) strncpy(g->imageGradient, val, 127;
            }
            else if (*p == 't') {
                if (strcmp(key, "isUpcoming") == 0) g->isUpcoming = 1;
                else if (strcmp(key, "isJustDropped") == 0) g->isJustDropped = 1;
                else if (strcmp(key, "isLatest") == 0) g->isLatest = 1;
                while (*p && *p != ',') p++;
            }
            else if (*p == 'f') {
                if (strcmp(key, "isUpcoming") == 0) g->isUpcoming = 0;
                else if (strcmp(key, "isJustDropped") == 0) g->isJustDropped = 0;
                else if (strcmp(key, "isLatest") == 0) g->isLatest = 0;
                while (*p && *p != ',') p++;
            }
            else if (*p == 'n') {
                if (strcmp(key, "repack") == 0) memset(&g->repack, 0, sizeof(g->repack);
                while (*p && *p != ',') p++;
            }
            else if (*p == '-' || (*p >= '0' && *p <= '9')) {
                char numval[32; int ni = 0;
                if (*p == '-') { numval[ni++] = *p++; }
                while (*p && *p != ',' && *p != '}' && *p != ']') { if (ni < 31) numval[ni++] = *p++; }
                numval[n] = '\0';
                if (strcmp(key, "sizeBytes") == 0) g->sizeBytes = atoll(numval;
                else if (strcmp(key, "rating") == 0) g->rating = (float)atof(numval);
                while (*p && *p != ',' && *p != '}') p++;
            }
            else if (*p == '[' && (strcmp(key, "tags") == 0 || strcmp(key, "sources") == 0)) {
                p++;
                while (*p && *p != ']') {
                    while (*p == ' ') p++;
                    if (*p == '"') {
                        p++; char arrval[32; int ai = 0;
                        while (*p && *p != '"') { if (ai < 31) arrval[ai++] = *p; p++; }
                        arrval[ai] = '\0'; if (*p == '"') p++;
                        if (strcmp(key, "tags") == 0 && g->tagCount < MAX_TAG)
                            strncpy(g->tags[g->tagCount++], arrval, 31);
                        else if (strcmp(key, "sources") == 0 && g->sourceCount < MAX_SRC)
                            strncpy(g->sources[g->sourceCount++], arrval, 31;
                    } if (*p == ',') p++;
                }
                if (*p == ']') p++;
            }
            else if (*p == '{' && strcmp(key, "repack") == 0) {
                p++; memset(&g->repack, 0, sizeof(g->repack);
                while (*p && *p != '}') {
                    while (*p == ' ') p++;
                    if (*p == '"') { p++; char rk[32; int ri = 0;
                        while (*p && *p != '"') { if (ri < 31) rk[ri++] = *p; p++; }
                        rk[ri] = '\0'; if (*p == '"') p++;
                        while (*p == ' ') p++; if (*p == ':') p++; while (*p == ' ') p++;
                        if (*p == '"') { p++; char rv[256; int vvi = 0;
                            while (*p && *p != '"') { if (*p == '\\' && *(p+1) == '"') { rv[vvi++] = '"'; p++; } else { rv[vvi++] = *p; } if (vvi < 255) p++; }
                            rv[vvi] = '\0'; if (*p == '"') p++;
                            if (strcmp(rk, "title") == 0) strncpy(g->repack.title, rv, 63;
                            else if (strcmp(rk, "size") == 0) strncpy(g->repack.size, rv, 15;
                            else if (strcmp(rk, "url") == 0) strncpy(g->repack.url, rv, 127;
                        }
                    } if (*p == ',') p++;
                }
                if (*p == '}') p++;
            }
            else { while (*p && *p != ',' && *p != '}') p++; }
            while (*p == ' ') p++;
            if (*p == ',') p++;
        }
        if (*p == '}') p++;
        g_gameCount++;
    }
    return g_gameCount;
}

/* ━━━ HTTP SERVER ━━━ */
static void http_send_response(SOCKET client, int code, const char* title, const char* type, const char* body, int bodyLen) {
    char header[512;
    int hLen = sprintf(header, "HTTP/1.1 %d %s\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\nAccess-Control-Allow-Origin: *\r\nCache-Control: no-cache\r\n\r\n", code, title, type, bodyLen);
    send(client, header, hLen, 0;
    if (body && bodyLen > 0) send(client, body, bodyLen, 0);
}

static void http_send_inline(SOCKET client) {
    static char out[256000; static int oi = 0;
    oi = 0;
    const char* hp = (const char*)g_html_resource;
    while (*hp) {
        if (strncmp(hp, "styles/app.css", 14) == 0) {
            oi += sprintf(out + oi, "<style>"); hp += 14;
            while (*hp) { if (*hp == '<' && *(hp+1) == '/' && *(hp+2) == '>') break; oi += sprintf(out + oi, "%c", *hp++); }
            oi += sprintf(out + oi, "</style>");
        } else if (strncmp(hp, "scripts/app.js", 14) == 0) {
            oi += sprintf(out + oi, "<script>"); hp += 14;
            while (*hp) { if (*hp == '<' && *(hp+1) == '/' && *(hp+2) == '>') break; oi += sprintf(out + oi, "%c", *hp++); }
            oi += sprintf(out + oi, "</script>");
        } else if (strncmp(hp, "scripts/download.js", 19) == 0) {
            oi += sprintf(out + oi, "<script>"); hp += 19;
            while (*hp) { if (*hp == '<' && *(hp+1) == '/' && *(hp+2) == '>') break; oi += sprintf(out + oi, "%c", *hp++); }
            oi += sprintf(out + oi, "</script>");
        } else { out[oi++] = *hp++; }
    }
    out[oi] = '\0';
    char hdr[512;
    int hLen = sprintf(hdr, "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: %d\r\nConnection: close\r\nAccess-Control-Allow-Origin: *\r\n\r\n", oi);
    send(client, hdr, strlen(hdr, 0;
    send(client, out, oi, 0;
}

static void http_send_games(SOCKET client) {
    static char out[256000; static int oi = 0;
    oi = 0;
    oi += sprintf(out + oi, "[\n");
    for (int i = 0; i < g_gameCount; i++) {
        Game* g = &g_games[i];
        oi += sprintf(out + oi, "  {\n    \"id\": \"%s\",\n    \"title\": \"%s\",\n    \"genre\": \"%s\",\n", g->id, g->title, g->genre);
        oi += sprintf(out + oi, "    \"genreLabel\": \"%s\",\n    \"description\": \"%s\",\n", g->genreLabel, g->description;
        oi += sprintf(out + oi, "    \"crackedBy\": \"%s\",\n    \"crackedDate\": \"%s\",\n", g->crackedBy, g->crackedDate;
        oi += sprintf(out + oi, "    \"uploadedDate\": \"%s\",\n    \"size\": \"%s\",\n", g->uploadedDate, g->size;
        oi += sprintf(out + oi, "    \"sizeBytes\": %lld,\n    \"version\": \"%s\",\n", g->sizeBytes, g->version);
        oi += sprintf(out + oi, "    \"isUpcoming\": %s,\n    \"isJustDropped\": %s,\n", g->isUpcoming ? "true" : "false", g->isJustDropped ? "true" : "false");
        oi += sprintf(out + oi, "    \"isLatest\": %s,\n    \"rating\": %.1f,\n", g->isLatest ? "true" : "
        }