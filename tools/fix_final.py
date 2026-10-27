#!/usr/bin/env python3
"""Final comprehensive fix for ALL BootyCatalog C++ files."""
import os, re, sys, glob

def fix(path):
    with open(path, 'rb') as f:
        content = f.read().decode('latin-1')
    orig = content
    src = os.path.basename(path)

    # 1. Missing closing parens: strcpy/strncpy strncpy(szInfo) - 1; -> strncpy(szInfo) - 1)
    content = re.sub(
        r'(strncpy\([^)]+,\s*[^\s;]+;)\s*$',
        r'\1)',
        content, flags=re.MULTILINE
    )

    # 2. Missing closing parens: tray_bubble(APP_NAME, buf, 5000; -> tray_bubble(APP_NAME, buf, 5000))
    content = re.sub(
        r'(tray_bubble\([^)]+,\s*[0-9]+;)',
        r'\1)',
        content
    )

    # 3. Missing closing parens: send(client, header, hLen, 0; -> send(client, header, hLen, 0))
    content = re.sub(
        r'(send\([^)]+,\s*[a-zA-Z_]+\d*,\s*[0-9]+;)',
        r'\1)',
        content
    )

    # 4. Missing closing parens: send(client, hdr, strlen(, 0; -> send(client, hdr, strlen(hdr), 0))
    content = re.sub(
        r'(send\([^)]+,\s*strlen\([^)]+\s*[^)]*,\s*[0-9]+;)',
        r'\1)',
        content
    )

    # 5. Missing closing parens: send(client, out, oi, 0; -> send(client, out, oi, 0))
    content = re.sub(
        r'(send\([^)]+,\s*oui,\s*[0-9]+;)',
        r'\1)',
        content
    )

    # 6. Missing closing parens: sizeof(lvc); -> sizeof(lvc)
    content = re.sub(
        r'(sizeof\(\w+\);)',
        r'\1)',
        content
    )

    # 7. Missing closing parens: memcpy(..., sizeof(Game) * g_gameCount; -> memcpy(..., sizeof(Game) * g_gameCount)
    content = re.sub(
        r'(memcpy\([^)]+,\s*sizeof\([^)]+\)\s*[^)]*;)',
        r'\1)',
        content
    )

    # 8. Missing closing parens: ListView_SetItemData(..., (DWORD_PTR)&g_filtered[i; -> ListView_SetItemData(..., (DWORD_PTR)&g_filtered[i])
    content = re.sub(
        r'(ListView_SetItemData\([^)]+,\s*\(DWORD_PTR\)&[^\)]+;)',
        r'\1)',
        content
    )

    # 9. szInfoTip -> szInfo
    content = content.replace('g_nid.szInfoTip', 'g_nid.szInfo')

    # 10. BIF_RETURNFSANCEONLY -> BIF_RETURNFSANCESTORS (the correct Windows constant)
    content = content.replace('BIF_RETURNFSANCEONLY', 'BIF_RETURNFSANCESTORS')

    # 11. ListView_InsertItemA -> ListView_InsertItem (the function exists)
    content = content.replace('ListView_InsertItemA', 'ListView_InsertItem')
    content = content.replace('ListView_SetItemTextA', 'ListView_SetItemText')
    content = content.replace('ListView_GetItemDataA', 'ListView_GetItemData')
    content = content.replace('ListView_InsertColumnA', 'ListView_InsertColumn')

    # 12. [ci; -> [ci]
    content = content.replace('[ci;', '[ci]')

    # 13. Missing ] before ;
    content = re.sub(r'\[([a-zA-Z_][a-zA-Z_0-9]*)\;([,\s\)]?)', r'[\1]\2', content)

    # 14. Missing closing paren on sprintf calls ending with ;
    content = re.sub(
        r'(sprintf\([^)]+,\s*"[^"]*",\s*[^\)]+\s*;)\s*$',
        r'\1)',
        content, flags=re.MULTILINE
    )

    # 15. Missing closing paren on sprintf with %d/%lld/%s ending with ;
    content = re.sub(
        r'(sprintf\([^)]+\d[^)]+,\s*[^\)]+)\s*;)',
        r'\1)',
        content
    )

    # 16. Missing closing paren on sprintf ending with ;
    content = re.sub(
        r'(sprintf\([^)]+,\s*"[^"]*[^)]+;\s*$',
        r'\1)',
        content, flags=re.MULTILINE
    )

    # 17. memset(&lvc, 0, sizeof(lvc); -> memset(&lvc, 0, sizeof(lvc))
    content = re.sub(
        r'(memset\([^)]+,\s*0,\s*sizeof\(\w+\);)',
        r'\1)',
        content
    )

    # 18. MainWndProc - fix truncated line: lvc.pszText = (LPSTR)
    content = content.replace(
        'lvc.cx = 100; lvc.pszText = (LPSTR)',
        'lvc.cx = 100; lvc.pszText = (LPSTR)"Genre";'
    )

    # 19. Add missing text after pszText
    if 'lvc.pszText = (LPSTR)' in content:
        content = content.replace(
            'lvc.pszText = (LPSTR)',
            'lvc.pszText = (LPSTR)"Genre";'
        )

    # 20. Missing closing paren in strcpy
    content = re.sub(
        r'(strcpy\([^)]+;\s*$)',
        r'\1)',
        content, flags=re.MULTILINE
    )

    # 21. Missing closing paren in strncpy
    content = re.sub(
        r'(strncpy\([^)]+;\s*$)',
        r'\1)',
        content, flags=re.MULTILINE
    )

    # 22. Missing closing paren in sprintf (generic)
    content = re.sub(
        r'(sprintf\([^)]+;\s*$)',
        r'\1)',
        content, flags=re.MULTILINE
    )

    # 23. Missing closing paren in sprintf with string literal
    content = re.sub(
        r'(sprintf\([^)]+,\s*"[^"]*"[^)]*;\s*$)',
        r'\1)',
        content, flags=re.MULTILINE | re.DOTALL
    )

    # 24. MainWndProc - fix truncated text at end of file:
    # Add closing braces for MainWndProc
    if content.rstrip().endswith('}'):
        # Check if MainWndProc is truncated
        mwp_start = content.find('static LRESULT CALLBACK MainWndProc')
        if mwp_start > 0:
            mwp_body = content[mwp_start:]
            # Count braces
            open_b = mwp_body.count('{')
            close_b = mwp_body.count('}')
            if open_b > close_b + 3:  # need more closing braces
                suffix = r'''
        case WM_SIZE:
            MoveWindow(g_hGrid, 20, 50, LOWORD(lp) - 40, HIWORD(lp) - 130, TRUE);
            SendMessageA(g_hStatus, WM_SIZE, 0, 0);
            return 0;
        case WM_COMMAND:
            switch (LOWORD(wp)) {
                case BTN_DOWNLOAD:
                    if (HIWORD(wp) == BN_CLICKED) {
                        int sel = ListView_GetNextItem(g_hGrid, -1, LVNI_SELECTED);
                        if (sel >= 0 && sel < g_filteredCount) {
                            dl_start(&g_filtered[sel], hwnd);
                        } else if (g_gameCount > 0) {
                            dl_start(&g_games[0], hwnd);
                        }
                    }
                    break;
                case BTN_BROWSE:
                    if (HIWORD(wp) == BN_CLICKED) {
                        char buf[MAX_PATH] = "C:\\Games";
                        if (browse_install_dir(hwnd, buf, MAX_PATH)) {
                            strcpy(g_download.installDir, buf);
                            char msg[256];
                            sprintf(msg, "Install folder: %s", buf);
                            if (g_hStatus)
                                SendMessageA(g_hStatus, SB_SETTEXT, 0, (LPARAM)msg);
                        }
                    }
                    break;
            }
            return 0;
        case WM_NOTIFY: {
            NMHDR* nh = (NMHDR*)lp;
            if (nh->code == LVN_ITEMCHANGED) {
                NMLISTVIEW* nlv = (NMLISTVIEW*)lp;
                if (nlv->uNewState & LVIS_SELECTED) {
                    int idx = nlv->iItem;
                    Game* g = (Game*)ListView_GetItemData(g_hGrid, idx);
                    if (g) {
                        char buf[256];
                        sprintf(buf, "Selected: %s (%s) — cracked by %s",
                                g->title, g->genreLabel, g->crackedBy);
                        if (g_hStatus)
                            SendMessageA(g_hStatus, SB_SETTEXT, 0, (LPARAM)buf);
                    }
                }
            }
            return 0;
        }
        case TRAY_MSG:
            if ((WORD)wp == WM_LBUTTONDBLCLK) {
                ShowWindow(hwnd, SW_SHOWNORMAL);
                BringWindowToTop(hwnd);
            } else if ((WORD)wp == WM_RBUTTONDOWN) {
                POINT pt;
                GetCursorPos(&pt);
                HMENU hMenu = CreatePopupMenu();
                AppendMenuA(hMenu, MF_STRING, 3001, "Open Booty Catalog");
                AppendMenuA(hMenu, MF_STRING, 3002, "Latest Cracks");
                AppendMenuA(hMenu, MF_STRING, 3003, "Add Game");
                AppendMenuA(hMenu, MF_STRING, 3004, "Exit");
                TrackPopupMenu(hMenu, TPM_BOTTOMALIGN | TPM_LEFTBUTTON,
                    pt.x, pt.y, 0, hwnd, NULL);
                DestroyMenu(hMenu);
            }
            return 0;
        case WM_DESTROY:
            http_server_stop();
            tray_destroy();
            PostQuitMessage(0);
            return 0;
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            SetBkMode(hdc, TRANSPARENT);
            SetTextColor(hdc, RGB(0x63, 0xb3, 0xed));
            TextOutA(hdc, 20, 5, APP_NAME, strlen(APP_NAME));
            SetTextColor(hdc, RGB(0xa8, 0xb8, 0xcc));
            char buf[128];
            sprintf(buf, "Showing %d games from all repacker sources", g_gameCount);
            TextOutA(hdc, 20, 25, buf, strlen(buf));
            SetTextColor(hdc, RGB(0x7e, 0xc8, 0x7e));
            TextOutA(hdc, LOWORD(lp) - 200, HIWORD(lp) - 30, "All systems operational", 22);
            EndPaint(hwnd, &ps);
            return 0;
        }
    }
    return DefWindowProcA(hwnd, msg, wp, lp);
'''
        else:
            suffix = r'''
        case WM_SIZE:
            MoveWindow(g_hGrid, 20, 50, LOWORD(lp) - 40, HIWORD(lp) - 130, TRUE);
            SendMessageA(g_hStatus, WM_SIZE, 0, 0);
            return 0;
        case WM_COMMAND:
            switch (LOWORD(wp)) {
                case BTN_DOWNLOAD:
                    if (HIWORD(wp) == BN_CLICKED) {
                        int sel = ListView_GetNextItem(g_hGrid, -1, LVNI_SELECTED);
                        if (sel >= 0 && sel < g_filteredCount) {
                            dl_start(&g_filtered[sel], hwnd);
                        } else if (g_gameCount > 0) {
                            dl_start(&g_games[0], hwnd);
                        }
                    }
                    break;
                case BTN_BROWSE:
                    if (HIWORD(wp) == BN_CLICKED) {
                        char buf[MAX_PATH] = "C:\\Games";
                        if (browse_install_dir(hwnd, buf, MAX_PATH)) {
                            strcpy(g_download.installDir, buf);
                            char msg[256];
                            sprintf(msg, "Install folder: %s", buf);
                            if (g_hStatus)
                                SendMessageA(g_hStatus, SB_SETTEXT, 0, (LPARAM)msg);
                        }
                    }
                    break;
            }
            return 0;
        case WM_NOTIFY: {
            NMHDR* nh = (NMHDR*)lp;
            if (nh->code == LVN_ITEMCHANGED) {
                NMLISTVIEW* nlv = (NMLISTVIEW*)lp;
                if (nlv->uNewState & LVIS_SELECTED) {
                    int idx = nlv->iItem;
                    Game* g = (Game*)ListView_GetItemData(g_hGrid, idx);
                    if (g) {
                        char buf[256];
                        sprintf(buf, "Selected: %s (%s) — cracked by %s",
                                g->title, g->genreLabel, g->crackedBy);
                        if (g_hStatus)
                            SendMessageA(g_hStatus, SB_SETTEXT, 0, (LPARAM)buf);
                    }
                }
            }
            return 0;
        }
        case TRAY_MSG:
            if ((WORD)wp == WM_LBUTTONDBLCLK) {
                ShowWindow(hwnd, SW_SHOWNORMAL);
                BringWindowToTop(hwnd);
            } else if ((WORD)wp == WM_RBUTTONDOWN) {
                POINT pt;
                GetCursorPos(&pt);
                HMENU hMenu = CreatePopupMenu();
                AppendMenuA(hMenu, MF_STRING, 3001, "Open Booty Catalog");
                AppendMenuA(hMenu, MF_STRING, 3002, "Latest Cracks");
                AppendMenuA(hMenu, MF_STRING, 3003, "Add Game");
                AppendMenuA(hMenu, MF_STRING, 3004, "Exit");
                TrackPopupMenu(hMenu, TPM_BOTTOMALIGN | TPM_LEFTBUTTON,
                    pt.x, pt.y, 0, hwnd, NULL);
                DestroyMenu(hMenu);
            }
            return 0;
        case WM_DESTROY:
            http_server_stop();
            tray_destroy();
            PostQuitMessage(0);
            return 0;
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            SetBkMode(hdc, TRANSPARENT);
            SetTextColor(hdc, RGB(0x63, 0xb3, 0xed));
            TextOutA(hdc, 20, 5, APP_NAME, strlen(APP_NAME));
            SetTextColor(hdc, RGB(0xa8, 0xb8, 0xcc));
            char buf[128];
            sprintf(buf, "Showing %d games from all repacker sources", g_gameCount);
            TextOutA(hdc, 20, 25, buf, strlen(buf));
            SetTextColor(hdc, RGB(0x7e, 0xc8, 0x7e));
            TextOutA(hdc, LOWORD(lp) - 200, HIWORD(lp) - 30, "All systems operational", 22);
            EndPaint(hwnd, &ps);
            return 0;
        }
    }
    return DefWindowProcA(hwnd, msg, wp, lp);
'''

    if content != orig:
        with open(path, 'wb') as f:
            f.write(content.encode('latin-1'))
        print(f'Fixed: {src}')
    else:
        print(f'No changes: {src}')

# Fix all source files
for f in sorted(glob.glob('src/*.cpp') + glob.glob('include/*.h')):
    fix(f)
print('All done')
