#!/usr/bin/env python3
"""Simple line-by-line fix for all C++ files."""
import os, sys

def fix_file(path):
    with open(path, 'rb') as f:
        content = f.read().decode('latin-1')
    lines = content.split('\n')
    new_lines = []
    changed = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()
        # Skip empty lines
        if not stripped:
            new_lines.append(line)
            i += 1
            continue
        orig = stripped

        # Fix: missing closing paren at end of line
        # Rule: line ends with ';' but has unbalanced ( )
        if stripped.endswith(';'):
            oplen = stripped.count('(') - stripped.count(')')
            if oplen > 0:
                # Count in pairs of ()
                depth = 0
                max_depth = 0
                for c in stripped:
                    if c == '(':
                        depth += 1
                        max_depth = max(max_depth, depth)
                    elif c == ')':
                        depth -= 1
                # Check: is the last ( a function call or sizeof?
                # Find last unmatched (
                depth = 0
                last_paren_pos = -1
                for c in stripped:
                    if c == '(': depth += 1
                    elif c == ')': depth -= 1
                if depth > 0:
                    depth = 0
                    for j, c in enumerate(stripped):
                        if c == '(':
                            depth += 1
                        elif c == ')':
                            depth -= 1
                        if depth == oplen:
                            last_paren_pos = j
                            break
                    if last_paren_pos > 0:
                        stripped = stripped[:last_paren_pos+1] + ')' + stripped[last_paren_pos+1:]
                        changed = True
                else:
                    # Maybe missing ] before ;
                    if stripped.endswith('];'):
                        pass
                    else:
                        # Check if we have [xxx; ending
                        if re.search(r'\[([a-zA-Z_]*)\;(\s|\)|$)', stripped):
                            stripped = re.sub(r'\[([a-zA-Z_]*)\;(\s|\))', r'[\1]\2', stripped)
                            changed = True
        else:
            # Not ending with ; but still check unbalanced parens
            oplen = stripped.count('(') - stripped.count(')')
            if oplen > 0:
                # Find last (
                depth = 0
                for j, c in enumerate(stripped):
                    if c == '(': depth += 1
                    elif c == ')': depth -= 1
                    if depth == oplen:
                        stripped = stripped[:j+1] + ')' + stripped[j+1:]
                        changed = True

        # Replace szInfoTip -> szInfo
        stripped = stripped.replace('g_nid.szInfoTip', 'g_nid.szInfo')

        # Replace BIF_RETURNFSANCEONLY -> BIF_RETURNFSANCESTORS
        stripped = stripped.replace('BIF_RETURNFSANCEONLY', 'BIF_RETURNFSANCESTORS')

        # Replace ListView_InsertItemA -> ListView_InsertItem
        stripped = stripped.replace('ListView_InsertItemA', 'ListView_InsertItem')
        stripped = stripped.replace('ListView_SetItemTextA', 'ListView_SetItemText')
        stripped = stripped.replace('ListView_GetItemDataA', 'ListView_GetItemData')
        stripped = stripped.replace('ListView_InsertColumnA', 'ListView_InsertColumn')

        # Fix truncated line: lvc.pszText = (LPSTR)
        if 'lvc.pszText = (LPSTR)' in stripped and not stripped.endswith('"Genre";'):
            stripped = stripped.replace('lvc.pszText = (LPSTR)', 'lvc.pszText = (LPSTR)"Genre";')
            changed = True

        new_lines.append(stripped)
        i += 1

    # If MainWndProc truncated, append the rest
    content = '\n'.join(new_lines)
    if content.rstrip().endswith('}'):
        mwp_start = content.find('static LRESULT CALLBACK MainWndProc')
        if mwp_start > 0:
            mwp_body = content[mwp_start:]
            open_b = mwp_body.count('{')
            close_b = mwp_body.count('}')
            needed = open_b - close_b
            if needed > 2:
                suffix_lines = [
                    '        case WM_SIZE:',
                    '            MoveWindow(g_hGrid, 20, 50, LOWORD(lp) - 40, HIWORD(lp) - 130, TRUE);',
                    '            SendMessageA(g_hStatus, WM_SIZE, 0, 0);',
                    '            return 0;',
                    '        case WM_COMMAND:',
                    '            switch (LOWORD(wp)) {',
                    '                case BTN_DOWNLOAD:',
                    '                    if (HIWORD(wp) == BN_CLICKED) {',
                    '                        int sel = ListView_GetNextItem(g_hGrid, -1, LVNI_SELECTED);',
                    '                        if (sel >= 0 && sel < g_filteredCount) {',
                    '                            dl_start(&g_filtered[sel], hwnd);',
                    '                        } else if (g_gameCount > 0) {',
                    '                            dl_start(&g_games[0], hwnd);',
                    '                        }',
                    '                    }',
                    '                    break;',
                    '                case BTN_BROWSE:',
                    '                    if (HIWORD(wp) == BN_CLICKED) {',
                    '                        char buf[MAX_PATH] = "C:\\\\\\\\Games";',
                    '                        if (browse_install_dir(hwnd, buf, MAX_PATH)) {',
                    '                            strcpy(g_download.installDir, buf);',
                    '                            char msg[256];',
                    '                            sprintf(msg, "Install folder: %s", buf);',
                    '                            if (g_hStatus)',
                    '                                SendMessageA(g_hStatus, SB_SETTEXT, 0, (LPARAM)msg);',
                    '                        }',
                    '                    }',
                    '                    break;',
                    '            }',
                    '            return 0;',
                    '        case WM_NOTIFY: {',
                    '            NMHDR* nh = (NMHDR*)lp;',
                    '            if (nh->code == LVN_ITEMCHANGED) {',
                    '                NMLISTVIEW* nlv = (NMLISTVIEW*)lp;',
                    '                if (nlv->uNewState & LVIS_SELECTED) {',
                    '                    int idx = nlv->iItem;',
                    '                    Game* g = (Game*)ListView_GetItemData(g_hGrid, idx);',
                    '                    if (g) {',
                    '                        char buf[256];',
                    '                        sprintf(buf, "Selected: %s (%s) — cracked by %s",',
                    '                                g->title, g->genreLabel, g->crackedBy);',
                    '                        if (g_hStatus)',
                    '                            SendMessageA(g_hStatus, SB_SETTEXT, 0, (LPARAM)buf);',
                    '                    }',
                    '                }',
                    '            }',
                    '            return 0;',
                    '        }',
                    '        case TRAY_MSG:',
                    '            if ((WORD)wp == WM_LBUTTONDBLCLK) {',
                    '                ShowWindow(hwnd, SW_SHOWNORMAL);',
                    '                BringWindowToTop(hwnd);',
                    '            } else if ((WORD)wp == WM_RBUTTONDOWN) {',
                    '                POINT pt;',
                    '                GetCursorPos(&pt);',
                    '                HMENU hMenu = CreatePopupMenu();',
                    '                AppendMenuA(hMenu, MF_STRING, 3001, "Open Booty Catalog");',
                    '                AppendMenuA(hMenu, MF_STRING, 3002, "Latest Cracks");',
                    '                AppendMenuA(hMenu, MF_STRING, 3003, "Add Game");',
                    '                AppendMenuA(hMenu, MF_STRING, 3004, "Exit");',
                    '                TrackPopupMenu(hMenu, TPM_BOTTOMALIGN | TPM_LEFTBUTTON,',
                    '                    pt.x, pt.y, 0, hwnd, NULL);',
                    '                DestroyMenu(hMenu);',
                    '            }',
                    '            return 0;',
                    '        case WM_DESTROY:',
                    '            http_server_stop();',
                    '            tray_destroy();',
                    '            PostQuitMessage(0);',
                    '            return 0;',
                    '        case WM_PAINT: {',
                    '            PAINTSTRUCT ps;',
                    '            HDC hdc = BeginPaint(hwnd, &ps);',
                    '            SetBkMode(hdc, TRANSPARENT);',
                    '            SetTextColor(hdc, RGB(0x63, 0xb3, 0xed));',
                    '            TextOutA(hdc, 20, 5, APP_NAME, strlen(APP_NAME));',
                    '            SetTextColor(hdc, RGB(0xa8, 0xb8, 0xcc));',
                    '            char buf[128];',
                    '            sprintf(buf, "Showing %d games from all repacker sources", g_gameCount);',
                    '            TextOutA(hdc, 20, 25, buf, strlen(buf));',
                    '            SetTextColor(hdc, RGB(0x7e, 0xc8, 0x7e));',
                    '            TextOutA(hdc, LOWORD(lp) - 200, HIWORD(lp) - 30, "All systems operational", 22);',
                    '            EndPaint(hwnd, &ps);',
                    '            return 0;',
                    '        }',
                    '    }',
                    '    return DefWindowProcA(hwnd, msg, wp, lp);',
                    '}',
                ]
                suffix = '\n' + '\n'.join(suffix_lines) + '\n'
                content = content + suffix
                changed = True

    if content != orig:
        with open(path, 'wb') as f:
            f.write(content.encode('latin-1'))
        print(f'Fixed: {os.path.basename(path)}')
    else:
        print(f'No change: {os.path.basename(path)}')

import re, glob
for f in sorted(glob.glob('src/*.cpp') + glob.glob('include/*.h')):
    fix_file(f)
print('All done')
