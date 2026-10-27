#include <process.h>
/**
 * Main.cpp — WinMain entry point and initialization
 * This is the single EXE's entry point.
 * Location: F:\study\projects\pirate-catalog
 */

#include "../include/BootyCatalog.h"

/* Include all modules via header for clean compilation */
extern int  parse_games_json(void* buf, int len);
extern void seed_games(void);
extern void* find_resource(HINSTANCE hInst, int id, const char* type, int* len);
extern void load_all_resources(HINSTANCE hInst);
extern int  http_server_init(int port);
extern void http_server_start(void);
extern void http_server_stop(void);
extern void tray_init(HINSTANCE hInst, HWND hwnd);
extern void tray_bubble(LPCSTR title, LPCSTR msg, DWORD timeout);
extern void tray_destroy(void);
extern void tray_update_state(int state);
extern void dl_start(Game* game, HWND hwndParent);
extern void stop_download(void);
extern int  browse_install_dir(HWND hwnd, char* buf, int bufSize);
extern void build_grid(void);
extern void build_grid_from_filtered(void);
extern void set_theme(HWND hwnd, int state);
extern void toggle_theme(HWND hwnd);
extern COLORREF get_theme_color(int colorIndex);
extern const char* get_game_emoji(const char* genre);
extern void time_ago(const char* dateStr, char* buf, int bufSize);
extern const char* format_size(long long bytes, char* buf, int bufSize);
extern void generate_game_card_html(char* buf, int bufSize, Game* g);
extern LRESULT CALLBACK MainWndProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp);

/* ━━━ GLOBALS (extern -- defined in BootyCatalog.cpp) ━━━ */
extern HINSTANCE g_hInst;
extern Game        g_games[MAX_GAMES];
extern int         g_gameCount;
extern GameItem    g_grid[MAX_GAMES];
extern int         g_gridCount;
extern int         g_viewMode;
extern HttpServer  g_httpServer;
extern DownloadTask g_download;
extern NOTIFYICONDATAA g_nid;
extern const char* EXE_DIR;
extern const char* GAMES_JSON_PATH;
extern HWND g_hMain;
extern HWND g_hStatus;
extern HWND g_hGrid;
extern HWND g_hSearch;

/* ━━━ EMBEDDED RESOURCES ━━━ */
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

/* ━━━ BOOTY CATALOG — FULL DEMAND ━━━ */
/*
 * The Full Demand:
 * "Continue in this folder you currently add, maximize this project in
 * any perspective. most per best looking and best performing application
 * with GUI. allowing me to scroll and find every possible available
 * pirately game including the very last one that was just recently
 * cracked and with only one click to download and install it to whatever
 * folder I wish. Don't forget about any useful source like all possible
 * repackers like dodi fitgirl etc. Don't forget to update the .md file
 * As long as you progress so that future sessions will be able to continue
 * where you left off easily, always knowing what this app is supposed to
 * be, don't ever forget to mention the full demand that I gave. and all
 * the necessary details like the location, the GitHub URL and whatever.
 * make all in c++ compile to exe That whenever running it will run the
 * project flawlessly with everything."
 */

/* ━━━ WinMain (consolidated in BootyCatalog.cpp) ━━━ */
/* WinMain — wrapped to avoid double-def (BootyCatalog.cpp has it) */
#if 0
int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR szCmdLine, int nCmd) {
    UNREFERENCED_PARAMETER(szCmdLine);
    UNREFERENCED_PARAMETER(hPrev);

    /* Store exe directory */
    static char exePath[MAX_PATH];
    GetModuleFileNameA(hInst, exePath, MAX_PATH);
    char* lastSlash = strrchr(exePath, '\\');
    if (lastSlash) { *lastSlash = '\0'; }
    EXE_DIR = exePath;

    /* Set games.json fallback path */
    static char jsonPath[MAX_PATH];
    sprintf(jsonPath, "%s\\data\\games.json", exePath);
    GAMES_JSON_PATH = jsonPath;

    /* Init common controls */
    INITCOMMONCONTROLSEX icc;
    icc.dwSize = sizeof(icc);
    icc.dwICC  = ICC_LISTVIEW_CLASSES | ICC_PROGRESS_CLASS |
                 ICC_BAR_CLASSES | ICC_TAB_CLASSES | ICC_STANDARD_CLASSES;
    InitCommonControlsEx(&icc);

    /* Load embedded resources */
    int len = 0;
    void* res = find_resource(hInst, 1001, RT_RCDATA, &len);
    if (res && len > 0) {
        parse_games_json(res, len);
    }
    if (g_gameCount == 0) {
        seed_games();
    }

    /* Register window class */
    WNDCLASSEXA wcx = {0};
    wcx.cbSize        = sizeof(wcx);
    wcx.style         = CS_HREDRAW | CS_VREDRAW | CS_DBLCLKS;
    wcx.lpfnWndProc   = MainWndProc;
    wcx.hInstance     = hInst;
    wcx.hCursor       = LoadCursorA(NULL, IDC_ARROW);
    wcx.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wcx.lpszClassName = APP_CLASS;
    wcx.hIcon         = LoadIconA(hInst, MAKEINTRESOURCEA(3001));
    wcx.hIconSm       = LoadIconA(hInst, MAKEINTRESOURCEA(3001));
    RegisterClassExA(&wcx);

    /* Create main window */
    g_hMain = CreateWindowExA(
        WS_EX_OVERLAPPEDWINDOW | WS_EX_APPWINDOW,
        APP_CLASS, APP_NAME,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 1200, 800,
        NULL, NULL, hInst, NULL);

    if (!g_hMain) return 1;

    /* Show main window */
    ShowWindow(g_hMain, SW_SHOWNORMAL);
    UpdateWindow(g_hMain);

    /* Init system tray with beautiful icon */
    tray_init(hInst, g_hMain);
    tray_bubble(APP_NAME, "Booty Catalog loaded. Your pirate catalog is ready.", 3000);

    /* Start embedded HTTP server */
    http_server_init(PORT);

    /* Open browser to localhost:8080 */
    char cmd[512];
    sprintf(cmd, "start \"Booty Catalog\" \"http://localhost:%d\"", PORT);
    WinExec(cmd, SW_SHOWNOACTIVATE);

    /* Message loop */
    MSG msg;
    while (GetMessageA(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }

    /* Cleanup */
    http_server_stop();
    tray_destroy();

    return (int)msg.wParam;
}
#endif
