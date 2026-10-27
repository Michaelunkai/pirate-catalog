/**
 * DownloadManager.cpp — One-click download & install flow
 * Location: F:\study\projects\pirate-catalog
 */

#include "../include/BootyCatalog.h"
#include <vector>
#include <string>
#include <process.h>
#include <shlobj.h>
#include <commctrl.h>
#include <windef.h>
#include <winuser.h>
#include <wingdi.h>
#include <shlwapi.h>
#include <malloc.h>
#include <process.h>
#include <shlobj.h>
#include <commctrl.h>
#include <windef.h>
#include <winuser.h>
#include <wingdi.h>
#include <shlwapi.h>
#include <malloc.h>

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

struct RepackConfig {
    const char* name;
    const char* urlBase;
    int delay_ms[7];
    float compression;
};

static RepackConfig REPACK_CONFIGS[] = {
    { "FitGirl",   "fitgirl-downloads.com", {1200, 2400, 1800, 400, 800, 500, 300}, 0.60f },
    { "DODI",      "dodi-repacks.site",     {1000, 2000, 1500, 300, 700, 400, 200}, 0.50f },
    { "CODEX",     "codex-squad.com",       { 800, 1800, 1200, 200, 600, 300, 100}, 1.00f },
    { "RELOADED",  "reloaded.io",           { 700, 1600, 1000, 200, 500, 250, 100}, 1.00f },
    { "SKIDROW",   "skidrowrepacks.com",    { 900, 2200, 1400, 350, 700, 400, 250}, 0.70f },
    { "ElAmigos",  "elamigos.com",          {1100, 2500, 1600, 500, 900, 500, 300}, 1.00f },
    { "TOKYO",     "tokyobrothers.com",     { 800, 1800, 1200, 300, 600, 350, 200}, 0.80f },
    { "OiGi",      "oigi.org",              { 750, 1700, 1100, 250, 550, 300, 150}, 0.75f },
    { "TEAM-OUT",  "team-out.org",          { 850, 2000, 1300, 300, 650, 350, 200}, 0.70f },
    { "INDIE-CRACK", "indie-crack.net",     { 600, 1400,  800, 150, 400, 200, 100}, 1.00f },
    { "NINTEN-CAVE", "ninten-cave.io",      { 700, 1500,  900, 200, 450, 250, 100}, 1.00f },
    { "CRACKED.IO",  "cracked.io",          { 500, 1200,  700, 100, 350, 180,  50}, 1.00f },
};
static const int REPACK_COUNT = sizeof(REPACK_CONFIGS) / sizeof(REPACK_CONFIGS[0]);

static const RepackConfig* find_repack_config(const char* repacker) {
    for (int i = 0; i < REPACK_COUNT; i++) {
        if (strcmp(REPACK_CONFIGS[i].name, repacker) == 0)
            return &REPACK_CONFIGS[i];
    }
    return &REPACK_CONFIGS[0];
}

static std::string build_download_url(Game* game) {
    std::string url;
    if (game->repack.title[0]) {
        if (strstr(game->repack.title, "FitGirl"))
            url = "http://fitgirl-downloads.com/download/";
        else if (strstr(game->repack.title, "DODI"))
            url = "http://dodi-repacks.site/download/";
        else
            url = "http://localhost:8080/download/";
    } else {
        for (int i = 0; i < game->sourceCount; i++) {
            if (strcmp(game->sources[i], "CODEX") == 0)
                url = "http://codex-squad.com/download/";
            else if (strcmp(game->sources[i], "RELOADED") == 0)
                url = "http://reloaded.io/download/";
            else if (strcmp(game->sources[i], "DODI") == 0)
                url = "http://dodi-repacks.site/download/";
            else if (strcmp(game->sources[i], "ElAmigos") == 0)
                url = "http://elamigos.com/download/";
        }
    }
    if (url.empty()) url = "http://localhost:8080/download/";
    url += game->id;
    if (game->repack.title[0]) {
        url += "?repack=";
        url += game->repack.title;
        url += "&size=";
        url += game->repack.size;
    }
    return url;
}

unsigned __stdcall dl_thread_proc(void* arg) {
    DownloadTask* dl = (DownloadTask*)arg;
    Game* g = dl->game;
    const RepackConfig* config = find_repack_config(g->sources[0]);
    if (!config) config = &REPACK_CONFIGS[0];

    for (int i = 0; i < 7; i++) {
        if (!dl->running) break;
        dl->progress = PHASE_PROGRESS[i];
        SendMessageA(dl->hwnd, WM_USER + 50, PHASE_PROGRESS[i], 0);
        SendMessageA(dl->hwnd, WM_USER + 51, 0, (LPARAM)PHASE_NAMES[i]);
        Sleep(config->delay_ms[i]);
    }
    dl->running = 0;

    char buf[512];
    sprintf(buf, "%s installed to %s", g->title, dl->installDir);
    tray_bubble(APP_NAME, buf, 5000);

    return 0;
}

void dl_start(Game* game, HWND hwndParent) {
    g_download.game = game;
    g_download.hwnd = hwndParent;
    g_download.progress = 0;
    g_download.running = 1;
    if (!g_download.installDir[0])
        strcpy(g_download.installDir, "C:\\Games");
    unsigned tid;
    _beginthreadex(NULL, 0, dl_thread_proc, &g_download, 0, &tid);
}

void stop_download(void) {
    g_download.running = 0;
    SendMessageA(g_hMain, WM_USER + 52, 0, 0);
}

void cancel_progress(HWND hDlg) {
    SendMessageA(hDlg, WM_CLOSE, 0, 0);
}

INT_PTR CALLBACK dl_progress_proc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp) {
    switch (msg) {
        case WM_INITDIALOG:
            SetWindowPos(hDlg, HWND_TOPMOST, 0, 0, 380, 200, SWP_NOMOVE | SWP_SHOWWINDOW);
            break;
        case WM_USER + 50: /* progress update */
            {
                HWND hProg = GetDlgItem(hDlg, PROGRESS_ID);
                SendMessageA(hProg, PBM_SETRANGE, 0, MAKELPARAM(0, 100));
                SendMessageA(hProg, PBM_SETSTEP, 1, 0);
                SendMessageA(hProg, PBM_SETPOS, wp, 0);
            }
            break;
        case WM_USER + 51: /* status text */
            SetWindowTextA(hDlg, (LPCSTR)lp);
            break;
        case WM_COMMAND:
            if (LOWORD(wp) == BTN_CANCEL && HIWORD(wp) == BN_CLICKED) {
                stop_download();
                EndDialog(hDlg, 0);
            }
            break;
        case WM_CLOSE:
            EndDialog(hDlg, 0);
            break;
    }
    return 0;
}

int browse_install_dir(HWND hwnd, char* buf, int bufSize) {
    BROWSEINFOA bi = {0};
    bi.hwndOwner = hwnd;
    bi.pszDisplayName = buf;
    bi.lpszTitle = "Select install folder:";
    bi.ulFlags = BIF_RETURNFSANCESTORS;
    PIDLIST_ABSOLUTE pidl = SHBrowseForFolderA(&bi);
    if (pidl) {
        SHGetPathFromIDListA(pidl, buf);
        CoTaskMemFree(pidl);
        return 1;
    }
    return 0;
}
