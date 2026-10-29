/**
 * Menu.h — Context Menu System (IMPLEMENTATION READY)
 * Location: F:\study\projects\pirate-catalog
 *
 * Structured menu management with right-click grid support.
 * No Windows menu-specific implementation in this .cpp file.
 */
#ifndef MENU_H
#define MENU_H

#include <windows.h>

typedef struct Menu Menu;

/* Menu item callback signature */
typedef void (*MenuCallback)(HWND, int, LPARAM);

struct MenuItem {
    int id;
    const char* text;
    MenuCallback callback;
    LPARAM param;
};

struct Menu {
    HMENU hMenu;
    int itemCount;
    MenuItem items[32];
};

/* Menu API */
void    menu_init(Menu* m);
void    menu_add_item(Menu* m, int id, const char* text, MenuCallback callback, LPARAM param);
void    menu_show(Menu* m, HWND hwnd, int x, int y);
void    menu_destroy(Menu* m);

#endif // MENU_H
