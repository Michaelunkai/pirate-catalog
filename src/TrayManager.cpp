/**
 * TrayManager.cpp — System tray icon, notifications, context menu
 * Location: F:\study\projects\pirate-catalog
 */

#include "../include/BootyCatalog.h"
#include <vector>
#include <string>

extern NOTIFYICONDATAA g_nid;
extern HINSTANCE g_hInst;

void tray_init(HINSTANCE hInst, HWND hwnd) {
    g_hInst = hInst;
    g_nid.cbSize = sizeof(NOTIFYICONDATAA);
    g_nid.hWnd = hwnd;
    g_nid.uID = TRAY_ID;
    g_nid.uFlags = NIF_ICON | NIF_TIP | NIF_MESSAGE;
    g_nid.uCallbackMessage = WM_USER + 20;
    g_nid.hIcon = LoadIconA(hInst, MAKEINTRESOURCEA(3001));
    strncpy(g_nid.szTip, APP_NAME, sizeof(g_nid.szTip) - 1);
    g_nid.szTip[sizeof(g_nid.szTip) - 1] = '\0';
    Shell_NotifyIconA(NIM_ADD, &g_nid);
}

void tray_update_icon(int state) {
    int resId = 3001 + state;
    HICON hIcon = LoadIconA(g_hInst, MAKEINTRESOURCEA(resId));
    if (hIcon) {
        g_nid.hIcon = hIcon;
        Shell_NotifyIconA(NIM_MODIFY, &g_nid);
    }
}

void tray_bubble(LPCSTR title, LPCSTR msg, DWORD timeout) {
    g_nid.uFlags = NIF_ICON | NIF_TIP | NIF_MESSAGE | NIF_INFO;
    g_nid.hIcon = LoadIconA(GetModuleHandleA(NULL), MAKEINTRESOURCEA(3001));
    strncpy(g_nid.szInfo, msg, sizeof(g_nid.szInfo) - 1);
    g_nid.szInfo[sizeof(g_nid.szInfo) - 1] = '\0';
    strncpy(g_nid.szInfoTitle, title, sizeof(g_nid.szInfoTitle) - 1);
    g_nid.szInfoTitle[sizeof(g_nid.szInfoTitle) - 1] = '\0';
    g_nid.szInfo[sizeof(g_nid.szInfo) - 1] = '\0';
    g_nid.uTimeout = timeout;
    Shell_NotifyIconA(NIM_MODIFY, &g_nid);
}

void tray_destroy(void) {
    Shell_NotifyIconA(NIM_DELETE, &g_nid);
}

void show_tray_menu(POINT pt) {
    HMENU hMenu = CreatePopupMenu();
    AppendMenuA(hMenu, MF_STRING, 3001, "Open Booty Catalog");
    AppendMenuA(hMenu, MF_STRING, 3002, "Latest Cracks");
    AppendMenuA(hMenu, MF_STRING, 3003, "Add Game");
    AppendMenuA(hMenu, MF_STRING, 3004, "Exit");
    TrackPopupMenu(hMenu, TPM_BOTTOMALIGN | TPM_LEFTBUTTON,
        pt.x, pt.y, 0, g_nid.hWnd, NULL);
    DestroyMenu(hMenu);
}
