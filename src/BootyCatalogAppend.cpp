/* -- RESOURCES -- */
#include "BootyCatalog.h"
#include <shlobj.h>
#include <process.h>

/* Forward declarations for functions in other TUs */
extern int  init_grid_browser(HWND);
extern void filter_grid(const char*);
extern int  build_download_dialog(HWND, Game*);
extern int  init_theme(HINSTANCE);
extern int  http_server_start(int);

static unsigned char g_games_resource_blob[] = {0};
static int g_games_res_len = 0;

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
    g_gameCount++;
}

/* -- MAIN WND PROC -- */
LRESULT CALLBACK MainWndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    static char installDir[MAX_PATH] = "C:\\Games";
    static Game* selectedGame = NULL;
    switch (msg) {
        case WM_CREATE: {
            parse_games_json(g_games_resource_blob, g_games_res_len);
            g_hMain = hwnd;
            g_hGrid = CreateWindowA(WC_LISTVIEWA, NULL,
                WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_NOSORTHEADER,
                10, 40, 780, 540, hwnd, (HMENU)GRID_LIST_VIEW,
                GetModuleHandleA(NULL), NULL);
            LVCOLUMN lvc;
            memset(&lvc, 0, sizeof(LVCOLUMN));
            lvc.mask = LVCF_TEXT;
            lvc.pszText = "Game";
            lvc.cx = 200;
            ListView_InsertColumn(g_hGrid, 0, &lvc);
            init_grid_browser(g_hGrid);
            filter_grid("");
        }
        break;
        case WM_SIZE: {
            int w = LOWORD(lParam);
            int h = HIWORD(lParam);
            if (g_hGrid) MoveWindow(g_hGrid, 10, 40, w - 20, h - 80, TRUE);
            if (g_hSearch) MoveWindow(g_hSearch, 10, 10, w - 220, 25, TRUE);
            if (g_hStatus) MoveWindow(g_hStatus, 10, h - 30, w - 20, 20, TRUE);
        }
        break;
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
                } break;
                case BTN_CANCEL:
                    g_download.running = 0;
                    SendMessage(g_hGrid, WM_USER + 30, 0, 0);
                    break;
                case GRID_LIST_VIEW:
                    if (HIWORD(wParam) == LVN_ITEMCHANGED) {
                        LPNMLISTVIEW n = (LPNMLISTVIEW)lParam;
                        if (n->iItem >= 0 && n->iItem < g_gridCount)
                            selectedGame = &g_grid[n->iItem].game;
                    }
                    break;
            }
        }
        break;
        case WM_NOTIFY:
            break;
        case WM_TIMER:
            if (wParam == (WM_USER + 20)) {
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
        }
        break;
        case WM_SETCURSOR:
            if ((HWND)LOWORD(lParam) == g_hGrid)
                SetCursor(LoadCursorA(NULL, IDC_HAND));
            break;
        default:
            return DefWindowProcA(hwnd, msg, wParam, lParam);
    }
    return 0;
}

/* -- WINMAIN -- */
int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR szCmdLine, int nCmd) {
    EXE_DIR = "F:\\study\\projects\\pirate-catalog";
    init_theme(hInst);
    WNDCLASSEXA wc = {0};
    wc.cbSize = sizeof(WNDCLASSEXA);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = MainWndProc;
    wc.hInstance = hInst;
    wc.hCursor = LoadCursorA(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = APP_CLASS;
    RegisterClassExA(&wc);
    g_hMain = CreateWindowA(APP_CLASS, APP_NAME,
        WS_OVERLAPPEDWINDOW | WS_VISIBLE,
        100, 100, 800, 600, NULL, NULL, hInst, NULL);
    tray_init(hInst, g_hMain);
    http_server_start(PORT);
    MSG msg;
    while (GetMessageA(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
    http_server_stop();
    tray_destroy();
    return (int)msg.wParam;
}
