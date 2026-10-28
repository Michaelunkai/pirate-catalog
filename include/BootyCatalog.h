/**
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

/* ━━━ CONSTANTS ━━━ */
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
#define MAX_GAMES         800
#define MAX_TITLE         128
#define MAX_DESC          256
#define MAX_SRC           8
#define MAX_TAG           8
#define MAX_GRAD          128

/* ━━━ DATA STRUCTURES ━━━ */
typedef struct {
    char title[64];
    char size[16];
    char url[128];
} RepackInfo;

typedef struct {
    char     id[MAX_TITLE];
    char     title[MAX_TITLE];
    char     genre[32];
    char     genreLabel[64];
    char     description[MAX_DESC];
    char     crackedBy[32];
    char     crackedDate[16];
    char     uploadedDate[16];
    char     size[16];
    long long sizeBytes;
    char     version[32];
    int      isUpcoming;
    int      isJustDropped;
    int      isLatest;
    float    rating;
    char     tags[MAX_TAG][32];
    int      tagCount;
    char     imageGradient[MAX_GRAD];
    RepackInfo repack;
    char     sources[MAX_SRC][32];
    int      sourceCount;
    char     feedUrl[512]; /* live source page URL for one-click fetch */
} Game;

typedef struct {
    Game game;
    RECT rect;
    int  selected;
} GameItem;

typedef struct {
    Game*  game;
    HWND   hwnd;
    char   installDir[MAX_PATH];
    int    progress;
    int    running;
} DownloadTask;

typedef struct {
    SOCKET     sock;
    sockaddr_in I;
    char       host[64];
    int        port;
    int        running;
} HttpServer;

/* ━━━ GLOBALS ━━━ */
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

/* ━━━ FUNCTION DECLARATIONS ━━━ */
int  parse_games_json(void* buf, int len);
void seed_games(void);

void* find_resource(HINSTANCE hInst, int id, const char* type, int* len);
void load_all_resources(HINSTANCE hInst);

int   http_server_init(int port);
void  http_server_start(void);
void  http_server_stop(void);
void  http_send_response(SOCKET client, int code, const char* title,
                         const char* type, const char* body, int bodyLen);
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

#endif // BOOTY_CATALOG_H
