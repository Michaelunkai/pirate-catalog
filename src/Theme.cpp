/**
 * Theme.cpp — Dark/Light theme management for Win32 UI
 * Location: F:\study\projects\pirate-catalog
 */

#include "../include/BootyCatalog.h"

typedef struct {
    COLORREF bg;
    COLORREF surface;
    COLORREF border;
    COLORREF text;
    COLORREF textSec;
    COLORREF accent;
    COLORREF gold;
    COLORREF green;
    COLORREF red;
} ThemeColors;

static ThemeColors g_dark = {
    RGB(0x0a, 0x0e, 0x17), RGB(0x11, 0x18, 0x27), RGB(0x2a, 0x3a, 0x52),
    RGB(0xe8, 0xed, 0xf5), RGB(0xa8, 0xb8, 0xcc), RGB(0x63, 0xb3, 0xed),
    RGB(0xf6, 0xc8, 0x47), RGB(0x7e, 0xc8, 0x7e), RGB(0xfc, 0x62, 0x5d),
};

static ThemeColors g_light = {
    RGB(0xf0, 0xf4, 0xf8), RGB(0xff, 0xff, 0xff), RGB(0xcb, 0xd5, 0xe0),
    RGB(0x1a, 0x20, 0x2c), RGB(0x4a, 0x55, 0x68), RGB(0x3b, 0x82, 0xf6),
    RGB(0xd6, 0x9e, 0x2e), RGB(0x38, 0x7a, 0x4a), RGB(0xdc, 0x26, 0x26),
};

static ThemeColors* g_current = &g_dark;
static int g_themeState = 0;
static HWND g_mainHwnd;

void set_theme(HWND hwnd, int state) {
    g_mainHwnd = hwnd;
    g_current = (state == 0) ? &g_dark : &g_light;
    g_themeState = state;

    HKEY hKey;
    RegOpenKeyExA(HKEY_CURRENT_USER, "Software\\BootyCatalog", 0, KEY_SET_VALUE, &hKey);
    RegSetValueExA(hKey, "Theme", 0, REG_DWORD, (BYTE*)&state, sizeof(DWORD));
    RegCloseKey(hKey);

    if (g_hGrid) {
        ListView_SetTextColor(g_hGrid, g_current->text);
        ListView_SetBkColor(g_hGrid, g_current->bg);
        ListView_SetTextBkColor(g_hGrid, g_current->surface);
    }

    InvalidateRect(hwnd, NULL, TRUE);
    UpdateWindow(hwnd);
}

const char* get_theme_name(void) {
    return g_themeState == 0 ? "dark" : "light";
}

static void ApplyThemeToControls(HWND hwnd, ThemeColors* tc) {
    InvalidateRect(hwnd, NULL, TRUE);
    UpdateWindow(hwnd);

    if (g_hGrid) {
        ListView_SetTextColor(g_hGrid, tc->text);
        ListView_SetBkColor(g_hGrid, tc->bg);
        ListView_SetTextBkColor(g_hGrid, tc->surface);
    }

    if (g_hStatus) {
        int parts[] = {200, 400, -1};
        SendMessageA(g_hStatus, SB_SETPARTS, 3, (LPARAM)parts);
    }

    InvalidateRect(g_hMain, NULL, TRUE);
    UpdateWindow(g_hMain);
}

COLORREF get_color(int colorIndex) {
    switch (colorIndex) {
        case 0: return g_current->bg;
        case 1: return g_current->surface;
        case 2: return g_current->border;
        case 3: return g_current->text;
        case 4: return g_current->textSec;
        case 5: return g_current->accent;
        case 6: return g_current->gold;
        case 7: return g_current->green;
        case 8: return g_current->red;
        default: return g_current->accent;
    }
}

void toggle_theme(HWND hwnd) {
    int newState = (g_themeState + 1) % 2;
    set_theme(hwnd, newState);
    char msg[128];
    sprintf(msg, "Theme switched to %s mode", get_theme_name());
    tray_bubble(APP_NAME, msg, 2000);
}
