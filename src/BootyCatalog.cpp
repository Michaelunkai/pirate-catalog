/*
 * Booty Catalog -- Full C++ EXE (Consolidated)
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
 * Build: g++ -O2 -mwindows -std=c++17 -o BootyCatalog.exe BootyCatalog.cpp
 */
#include <winsock2.h>
#include <ws2tcpip.h>
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
#include <algorithm>
#include "../src/embedded.h"
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
#define MAX_PATH          260
/* Use sizeof directly — macro caused issues */

typedef struct RepackInfo {
    char title[64];
    char size[16];
    char url[128];
} RepackInfo;

typedef struct Game {
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
} Game;

typedef struct GameItem {
    Game game;
    RECT rect;
    int  selected;
} GameItem;

typedef struct DownloadTask {
    Game*  game;
    HWND   hwnd;
    char   installDir[MAX_PATH];
    int    progress;
    int    running;
} DownloadTask;

typedef struct HttpServer {
    SOCKET sock;
    sockaddr_in addr;
    char host[64];
    int port;
    int running;
} HttpServer;

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
const char* EXE_DIR = NULL;
const char* GAMES_JSON_PATH = NULL;
GameItem*   g_selected = NULL;
int         g_dark = 1;

/* JSON parser -- hex encoded to avoid corruption */
int parse_games_json(void* buf, int len) {
    char* p = (char*)buf;
    while (*p && *p != '[') p++;
    if (*p) { p++; g_gameCount = 0; }
    else return 0;
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
            if (*p == '"') p++;
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
                else if (strcmp(key, "genre") == 0) strncpy(g->genre, val, 31);
                else if (strcmp(key, "genreLabel") == 0) strncpy(g->genreLabel, val, 63);
                else if (strcmp(key, "description") == 0) strncpy(g->description, val, 255);
                else if (strcmp(key, "crackedBy") == 0) strncpy(g->crackedBy, val, 31);
                else if (strcmp(key, "crackedDate") == 0) strncpy(g->crackedDate, val, 15);
                else if (strcmp(key, "uploadedDate") == 0) strncpy(g->uploadedDate, val, 15);
                else if (strcmp(key, "size") == 0) strncpy(g->size, val, 15);
                else if (strcmp(key, "version") == 0) strncpy(g->version, val, 31);
                else if (strcmp(key, "imageGradient") == 0) strncpy(g->imageGradient, val, 127);
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
                if (strcmp(key, "repack") == 0) memset(&g->repack, 0, sizeof(g->repack));
                while (*p && *p != ',') p++;
            }
            else if (*p == '-' || (*p >= '0' && *p <= '9')) {
                char numval[32]; int ni = 0;
                if (*p == '-') { numval[ni++] = *p++; }
                while (*p && *p != ',' && *p != '}' && *p != ']') { if (ni < 31) numval[ni++] = *p; }
                numval[ni] = '\0';
                if (strcmp(key, "sizeBytes") == 0) g->sizeBytes = atoll(numval);
                else if (strcmp(key, "rating") == 0) g->rating = (float)atof(numval);
                while (*p && *p != ',' && *p != '}') p++;
            }
            else if (*p == '[' && (strcmp(key, "tags") == 0 || strcmp(key, "sources") == 0)) {
                p++;
                while (*p && *p != ']') {
                    while (*p == ' ') p++;
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
            }
            else if (*p == '{' && strcmp(key, "repack") == 0) {
                p++; memset(&g->repack, 0, sizeof(g->repack));
                while (*p && *p != '}') {
                    while (*p == ' ') p++;
                    if (*p == '"') { p++; char rk[32]; int ri = 0;
                        while (*p && *p != '"') { if (ri < 31) rk[ri++] = *p; p++; }
                        rk[ri] = '\0'; if (*p == '"') p++;
                        while (*p == ' ') p++; if (*p == ':') p++; while (*p == ' ') p++;
                        if (*p == '"') { p++; char rv[256]; int vvi = 0;
                            while (*p && *p != '"') {
                                if (*p == '\\' && *(p+1) == '"') { rv[vvi++] = '"'; p++; }
                                else { rv[vvi++] = *p; }
                                if (vvi < 255) p++;
                            }
                            rv[vvi] = '\0'; if (*p == '"') p++;
                            if (strcmp(rk, "title") == 0) strncpy(g->repack.title, rv, 63);
                            else if (strcmp(rk, "size") == 0) strncpy(g->repack.size, rv, 15);
                            else if (strcmp(rk, "url") == 0) strncpy(g->repack.url, rv, 127);
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

/* Resources */
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
    g->isUpcoming = 1;
    g->isJustDropped = 0;
    g->isLatest = 0;
    g->rating = 4.9f;
    g_gameCount++;
}

/* HTTP Server */
int http_server_init(int port) {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2,2), &wsa);
    g_httpServer.sock = socket(AF_INET, SOCK_STREAM, 6);
    g_httpServer.port = port;
    g_httpServer.addr.sin_family = AF_INET;
    g_httpServer.addr.sin_addr.s_addr = INADDR_ANY;
    g_httpServer.addr.sin_port = htons(port);
    g_httpServer.running = 1;
    return 0;
}

void http_server_stop(void) {
    g_httpServer.running = 0;
    closesocket(g_httpServer.sock);
    WSACleanup();
}

/* Forward-declare resource buffers for HTTP server */
extern unsigned char g_games_resource_blob[];
extern int g_games_res_len;
extern unsigned char g_html_resource_blob[];
extern int g_html_res_len;
extern unsigned char g_css_resource_blob[];
extern int g_css_res_len;
extern unsigned char g_js_resource_blob[];
extern int g_js_res_len;
extern unsigned char g_jsdl_resource_blob[];
extern int g_jsdl_res_len;
extern const unsigned char games_bin[];
extern int games_bin_len;
extern const unsigned char html_bin[];
extern int html_bin_len;
extern const unsigned char css_bin[];
extern int css_bin_len;
/* Listener thread -- serves HTML/CSS/JS/JSON */
static void http_accept_loop(void) {
    static char header10[] = "HTTP/1.0 200 OK\r\n";
    static char header200[] = "Content-Type: text/html\r\n";
    static char header201[] = "Content-Type: application/json\r\n";
    static char header202[] = "Connection: close\r\n\r\n";
    static char hdrHtml[512];
    while (g_httpServer.running) {
        sockaddr_in clientAddr;
        int clientLen = sizeof(clientAddr);
        SOCKET clientSock = accept(g_httpServer.sock, (sockaddr*)&clientAddr, &clientLen);
        if (clientSock == INVALID_SOCKET) break;
        char buf[4096];
        recv(clientSock, buf, sizeof(buf) - 1, 0);
        char* req = buf;
        char* crlf = strstr(buf, "\r\n");
        if (crlf) *crlf = '\0';
        char* ext = strrchr(req, '.');
        if (ext) {
            if (strcmp(ext, ".js") == 0) {
                sprintf(hdrHtml, "HTTP/1.0 200 OK\r\nContent-Type: application/x-javascript\r\nConnection: close\r\n\r\n");
                send(clientSock, hdrHtml, strlen(hdrHtml), 0);
                send(clientSock, (char*)js_bin, jsdl_bin_len, 0);
            }
            else if (strcmp(ext, ".css") == 0) {
                sprintf(hdrHtml, "HTTP/1.0 200 OK\r\nContent-Type: text/css\r\nConnection: close\r\n\r\n");
                send(clientSock, hdrHtml, strlen(hdrHtml), 0);
                send(clientSock, (char*)css_bin, css_bin_len, 0);
            }
            else if (strcmp(ext, ".json") == 0) {
                sprintf(hdrHtml, "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n");
                send(clientSock, hdrHtml, strlen(hdrHtml), 0);
                send(clientSock, (char*)g_games_resource_blob, games_bin_len, 0);
            }
            else {
                sprintf(hdrHtml, "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n");
                send(clientSock, hdrHtml, strlen(hdrHtml), 0);
                send(clientSock, (char*)html_bin, html_bin_len, 0);
            }
        }
        else if (strcmp(req, "GET /") == 0) {
            sprintf(hdrHtml, "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n");
            send(clientSock, hdrHtml, strlen(hdrHtml), 0);
            send(clientSock, (char*)html_bin, html_bin_len, 0);
        }
        else {
            sprintf(hdrHtml, "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n");
            send(clientSock, hdrHtml, strlen(hdrHtml), 0);
            send(clientSock, (char*)html_bin, html_bin_len, 0);
        }
        closesocket(clientSock);
    }
}

/* Thread entry point for HTTP accept loop */
static DWORD WINAPI http_thread(LPVOID param) {
    (void)param;
    http_accept_loop();
    return 0;
}

extern void http_server_add_listener(void) {
    g_httpServer.running = 1;
    CreateThread(NULL, 0, http_thread, NULL, 0, NULL);
}

/* Forward declarations */
static int init_grid_browser(HWND h) {
    g_hGrid = h;
    return 0;
}
/* Inline filter_grid */
static char g_search[128];
static void filter_grid(const char* s) {
    strncpy(g_search, s, 127);
    g_search[127] = '\0';
    extern void build_grid_from_filtered(void);
    build_grid_from_filtered();
}
extern int  build_download_dialog(HWND, Game*);
extern void tray_destroy(void);
extern void tray_init(HINSTANCE hInst, HWND hwnd);
extern void tray_bubble(LPCSTR title, LPCSTR msg, DWORD timeout);
HINSTANCE g_hInst;

/* Hex-encoded embedded resources — safe from corruption targets */

unsigned char g_games_resource_blob[MAX_PATH * 1024];
int g_games_res_len;

unsigned char g_html_resource_blob[1024 * 1024];
int g_html_res_len;

unsigned char g_css_resource_blob[512 * 1024];
int g_css_res_len;

unsigned char g_js_resource_blob[512 * 1024];
int g_js_res_len;

unsigned char g_jsdl_resource_blob[256 * 1024];
int g_jsdl_res_len;

unsigned char g_icon_resource_blob[256 * 1024];
int g_icon_res_len;

unsigned char g_tray_resource_blob[64 * 1024];
int g_tray_res_len;

/* Decode hex string to binary in-place */
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

/* MainWndProc — Win32 window procedure */
extern LRESULT CALLBACK MainWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    static char installDir[MAX_PATH] = "C:\\Games";
    static Game* selectedGame = NULL;
    switch (msg) {
        case WM_CREATE: {
            parse_games_json(g_games_resource_blob, games_bin_len);
            g_hMain = hwnd;
            g_hGrid = CreateWindowA(WC_LISTVIEWA, NULL,
                WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_NOSORTHEADER,
                10, 40, 780, 540, hwnd, (HMENU)GRID_LIST_VIEW,
                GetModuleHandleA(NULL), NULL);
            LVCOLUMN lvc;
            memset(&lvc, 0, sizeof(LVCOLUMN));
            lvc.mask = LVCF_TEXT;
            lvc.pszText = (LPSTR)"Game";
            lvc.cx = 200;
            ListView_InsertColumn(g_hGrid, 0, &lvc);
            init_grid_browser(g_hGrid);
            filter_grid("");
            break;
        }
        case WM_SIZE: {
            int w = LOWORD(lParam);
            int h = HIWORD(lParam);
            if (g_hGrid) MoveWindow(g_hGrid, 10, 40, w-20, h-80, TRUE);
            if (g_hSearch) MoveWindow(g_hSearch, 10, 10, w-220, 25, TRUE);
            if (g_hStatus) MoveWindow(g_hStatus, 10, h-30, w-20, 20, TRUE);
            break;
        }
        case WM_COMMAND: {
            switch (LOWORD(wParam)) {
                case BTN_DOWNLOAD:
                    if (selectedGame) build_download_dialog(hwnd, selectedGame);
                    break;
                case BTN_BROWSE: {
                    BROWSEINFOA bi2;
                    memset(&bi2, 0, sizeof(BROWSEINFOA));
                    bi2.hwndOwner = hwnd;
                    bi2.ulFlags = 0x00000040 | 0x00000020;
                    LPITEMIDLIST pidl = SHBrowseForFolderA(&bi2);
                    if (pidl) {
                        SHGetPathFromIDListA(pidl, installDir);
                        CoTaskMemFree(pidl);
                    }
                    break;
                }
                case BTN_CANCEL:
                    g_download.running = 0;
                    SendMessage(g_hGrid, WM_USER+30, 0, 0);
                    break;
                case GRID_LIST_VIEW:
                    if (HIWORD(wParam) == LVN_ITEMCHANGED) {
                        LPNMLISTVIEW n = (LPNMLISTVIEW)lParam;
                        if (n->iItem >= 0 && n->iItem < g_gridCount)
                            selectedGame = &g_grid[n->iItem].game;
                    }
                    break;
            }
            break;
        }
        case WM_NOTIFY:
            break;
        case WM_TIMER:
            if (wParam == (WM_USER+20)) {
                if (LOWORD(lParam) == WM_LBUTTONDBLCLK) {
                    ShowWindow(hwnd, SW_SHOW);
                    BringWindowToTop(hwnd);
                }
            }
            break;
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            EndPaint(hwnd, &ps);
            break;
        }
        case WM_SETCURSOR:
            if ((HWND)(INT_PTR)LOWORD(lParam) == g_hGrid)
                SetCursor(LoadCursorA(NULL, IDC_HAND));
            break;
        default:
            return DefWindowProcA(hwnd, msg, wParam, lParam);
    }
    return 0;
}

/* WinMain — startup entry point */
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
    INITCOMMONCONTROLSEX icc;
    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_LISTVIEW_CLASSES | ICC_PROGRESS_CLASS |
        ICC_BAR_CLASSES | ICC_TAB_CLASSES | ICC_STANDARD_CLASSES;
    InitCommonControlsEx(&icc);
    memcpy(g_games_resource_blob, games_bin, games_bin_len);
    parse_games_json(g_games_resource_blob, games_bin_len);
    memcpy(g_html_resource_blob, html_bin, html_bin_len);
    memcpy(g_css_resource_blob, css_bin, css_bin_len);
    memcpy(g_js_resource_blob, js_bin, js_bin_len);
    memcpy(g_jsdl_resource_blob, jsdl_bin, jsdl_bin_len);
    if (g_gameCount == 0) {
        seed_games();
    }
    http_server_add_listener();
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
    g_hMain = CreateWindowExA(
        WS_EX_OVERLAPPEDWINDOW | WS_EX_APPWINDOW,
        APP_CLASS, APP_NAME,
        WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 1200, 800,
        NULL, NULL, hInst, NULL);
    if (!g_hMain) return 1;
    ShowWindow(g_hMain, SW_SHOWNORMAL);
    UpdateWindow(g_hMain);
    tray_init(hInst, g_hMain);
    tray_bubble(APP_NAME, "Booty Catalog loaded. Your pirate catalog is ready.", 3000);
    http_server_init(PORT);
    char cmd[512];
    sprintf(cmd, "start \"Booty Catalog\" \"http://localhost:%d\"", PORT);
    WinExec(cmd, SW_SHOWNOACTIVATE);
    MSG msg;
    while (GetMessageA(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
    http_server_stop();
    tray_destroy();
    return (int)msg.wParam;
}
