#!/usr/bin/env python3 -X utf8
"""Fix ALL C++ corruption patterns in src/*.cpp"""
import os, re, sys

SRC = r'F:\study\projects\pirate-catalog\src'

def fix(path):
    with open(path, 'rb') as f:
        content = f.read().decode('latin-1')
    orig = content
    src = os.path.basename(path)

    # === PASS 1: Fix ]->; swap in array brackets ===
    # Pattern: identifier;  where it should be identifier]  (before closing paren or comma or bracket)
    # We need to be careful: only fix cases where ';' is clearly wrong (missing ']' before ')')

    # Fix: MAX_GAMES; -> MAX_GAMES]
    content = re.sub(r'\bMAX_GAMES\;', 'MAX_GAMES]', content)
    content = re.sub(r'\bMAX_TITLE\;', 'MAX_TITLE]', content)
    content = re.sub(r'\bMAX_DESC\;', 'MAX_DESC]', content)
    content = re.sub(r'\bMAX_TAG\;', 'MAX_TAG]', content)
    content = re.sub(r'\bMAX_GRAD\;', 'MAX_GRAD]', content)
    content = re.sub(r'\bMAX_SRC\;', 'MAX_SRC]', content)
    content = re.sub(r'\bMAX_PATH\;', 'MAX_PATH]', content)

    # Fix: char arrval[32; -> char arrval[32]
    content = re.sub(r'\[([a-zA-Z_]\w*)\s*(\d+)\s*;\s*([,\)\]])', r'[\1 \2];\3', content)

    # Fix: char key[64; -> char key[64]
    content = re.sub(r'char\s+(\w+)\[(\d+)\s*;', r'char \1[\2];', content)

    # Fix: char val[256; -> char val[256]
    content = re.sub(r'char\s+(\w+)\[(\d+)\s*;', r'char \1[\2];', content)

    # Fix: char rk[32; -> char rk[32]
    content = re.sub(r'char\s+(\w+)\[(\d+)\s*;', r'char \1[\2];', content)

    # Fix: char rv[256; -> char rv[256]
    content = re.sub(r'char\s+(\w+)\[(\d+)\s*;', r'char \1[\2];', content)

    # Fix: char numval[32; -> char numval[32]
    content = re.sub(r'char\s+(\w+)\[(\d+)\s*;', r'char \1[\2];', content)

    # Fix: char hdr[512; -> char hdr[512]
    content = re.sub(r'char\s+(\w+)\[(\d+)\s*;', r'char \1[\2];', content)

    # Fix: char req[2048; -> char req[2048]
    content = re.sub(r'char\s+(\w+)\[(\d+)\s*;', r'char \1[\2];', content)

    # Fix: g_search[128; -> g_search[128]
    content = re.sub(r'g_search\[128\;', 'g_search[128]', content)

    # Fix: g_search[128;
    content = re.sub(r'\bg_search\[128\;', 'g_search[128]', content)

    # === PASS 2: Fix strstristr_func -> strstr ===
    content = content.replace('strstristr_func', 'strstr')

    # === PASS 3: Fix sprintf()buf -> sprintf(buf ===
    content = content.replace('sprintf()buf', 'sprintf(buf')

    # === PASS 4: Fix missing ) before ; ===
    # This is the hardest. We need to find patterns where a function call ends with ';
    # but should end with ')'

    # Fix known patterns:
    content = content.replace('sizeof(bi);', 'sizeof(bi));')  # memset(&bi, 0, sizeof(bi);
    content = content.replace('sizeof(g_nid.szInfo) - 1;)', 'sizeof(g_nid.szInfo) - 1);')
    content = content.replace('sizeof(g_nid.szTip) - 1;)', 'sizeof(g_nid.szTip) - 1);')

    # Fix: sizeof(lvi; -> sizeof(lvi));
    content = content.replace('sizeof(lvi;)', 'sizeof(lvi));')
    content = content.replace('sizeof(lvi;', 'sizeof(lvi));')

    # Fix: sizeof(g->repack; -> sizeof(g->repack));
    content = content.replace('sizeof(g->repack;)', 'sizeof(g->repack));')
    content = content.replace('sizeof(g->repack;', 'sizeof(g->repack));')

    # Fix: sizeof(g_httpServer.I; -> sizeof(g_httpServer.I));
    content = content.replace('sizeof(g_httpServer.I;)', 'sizeof(g_httpServer.I));')
    content = content.replace('sizeof(g_httpServer.I;', 'sizeof(g_httpServer.I));')

    # Fix: sizeof(opt; -> sizeof(opt));
    content = content.replace('sizeof(opt;)', 'sizeof(opt));')
    content = content.replace('sizeof(opt;', 'sizeof(opt));')

    # Fix: strlen(hdr), 0; -> strlen(hdr), 0)
    content = content.replace('strlen(hdr), 0;', 'strlen(hdr), 0)')
    content = content.replace('strlen(hdr));', 'strlen(hdr));')

    # Fix: strlen(APP_NAME; -> strlen(APP_NAME)
    content = content.replace('strlen(APP_NAME;)', 'strlen(APP_NAME));')
    content = content.replace('strlen(APP_NAME;', 'strlen(APP_NAME));')

    # Fix: strlen(g->title; -> strlen(g->title)
    content = content.replace('strlen(g->title;)', 'strlen(g->title));')
    content = content.replace('strlen(g->title;', 'strlen(g->title));')

    # Fix: strlen(sizeBuf; -> strlen(sizeBuf)
    content = content.replace('strlen(sizeBuf;)', 'strlen(sizeBuf));')
    content = content.replace('strlen(sizeBuf;', 'strlen(sizeBuf));')

    # Fix: strlen(buf; -> strlen(buf)
    content = content.replace('strlen(buf;)', 'strlen(buf));')
    content = content.replace('strlen(buf;', 'strlen(buf));')

    # Fix: strlen(count; -> strlen(count)
    content = content.replace('strlen(count;)', 'strlen(count));')
    content = content.replace('strlen(count;', 'strlen(count));')

    # Fix: subtitle.length; -> subtitle.length())
    content = content.replace('subtitle.length;)', 'subtitle.length()));')
    content = content.replace('subtitle.length;', 'subtitle.length());')

    # Fix: strlen(hdr); -> strlen(hdr)
    content = content.replace('strlen(hdr));)', 'strlen(hdr));')

    # Fix: sizeof(g_games_resource; -> sizeof(g_games_resource)
    content = content.replace('sizeof(g_games_resource;)', 'sizeof(g_games_resource));')

    # === PASS 5: Fix missing ) at end of line (lines ending with ';') ===
    # Generic: find function calls that end with '; instead of ')'
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.rstrip()
        # Skip comments and strings
        if stripped.startswith('//') or stripped.startswith('/*'):
            new_lines.append(line)
            continue
        if stripped.endswith(';'):
            # Check for common patterns missing )
            fixes = [
                ('sizeof(bi);', 'sizeof(bi));'),
                ('sizeof(g_nid.szInfo) - 1;', 'sizeof(g_nid.szInfo) - 1);'),
                ('sizeof(g_nid.szTip) - 1;', 'sizeof(g_nid.szTip) - 1);'),
                ('sizeof(lvi);', 'sizeof(lvi));'),
                ('sizeof(g->repack);', 'sizeof(g->repack));'),
                ('sizeof(g_httpServer.I);', 'sizeof(g_httpServer.I));'),
                ('sizeof(opt);', 'sizeof(opt));'),
                ('sizeof(ic);', 'sizeof(ic));'),
                ('sizeof(icc);', 'sizeof(ic));'),
            ]
            for old, new in fixes:
                if old in stripped:
                    stripped = stripped.replace(old, new)
            # Generic: if line ends with '; and has unbalanced function parens
            open_p = stripped.count('(') - stripped.count(')')
            if open_p > 1 and ')' not in stripped[-5:]:
                stripped = stripped.rstrip(';') + ');'
            elif open_p == 1 and stripped.endswith(');'):
                # Already has ); but maybe missing )
                pass
            else:
                stripped = stripped.rstrip(';') + ');'
        new_lines.append(line.rstrip())
        if line.endswith(';'):
            pass  # keep trailing space for next step

        content = '\n'.join(new_lines)

    # === PASS 6: Fix BIF_RETURNFSANCESTORS ===
    content = content.replace('BIF_RETURN_FSANCE_ONLY', 'BIF_RETURNFSANCESTORS')

    # === PASS 7: Fix icc.dwICC flags ===
    content = content.replace('ICC_PROGRESS_CLASSES', 'ICC_PROGRESS_CLASS')

    # === PASS 8: Fix strnncpy -> strncpy ===
    content = content.replace('strnncpy', 'strncpy')

    # === PASS 9: Fix str -> stristr_func ===
    content = content.replace('str(', 'stristr_func(')

    # === PASS 10: Fix format_size ===
    content = content.replace('format_size()long long', 'format_size(long long')

    # === PASS 11: Fix create window ex ===
    content = content.replace('CreateWindowExA()', 'CreateWindowExA(')
    content = content.replace('tray_bubble()APP_NAME', 'tray_bubble(APP_NAME')

    # === PASS 12: Fix _beginthreadex ===
    content = content.replace('_beginthreadex()NULL', '_beginthreadex(NULL')

    # === PASS 13: Fix SHBrowseForFolderA ===
    content = content.replace('SHBrowseForFolderA()&bi;', 'SHBrowseForFolderA(&bi);')

    # === PASS 14: Fix strcpy buf quotes ===
    content = content.replace('strcpy(buf, "Today);', 'strcpy(buf, "Today");')
    content = content.replace('strcpy(buf, "Yesterday;', 'strcpy(buf, "Yesterday");')

    # === PASS 15: Fix sprintf with "Today" broken quote ===
    content = content.replace('sprintf(buf, "Today);', 'sprintf(buf, "Today");')
    content = content.replace('sprintf(buf, "Yesterday;', 'sprintf(buf, "Yesterday");')

    # === PASS 16: Fix sprintf(buf, "%d years ago"; -> sprintf(buf, "%d years ago", days / 365); ===
    content = content.replace('sprintf(buf, "%d years ago", days / 365;', 'sprintf(buf, "%d years ago", days / 365)')

    # === PASS 17: Fix sprintf(count, ...; ===
    content = content.replace('sprintf(count, "Showing %d games from all repacker sources", g_gameCount;', 'sprintf(count, "Showing %d games from all repacker sources", g_gameCount)')

    # === PASS 18: Fix GridBrowser format_size sprintf()buf ===
    content = content.replace('sprintf()buf, "%.1f MB"', 'sprintf(buf, "%.1f MB"')
    content = content.replace('sprintf()buf, "%.1f GB"', 'sprintf(buf, "%.1f GB"')

    # === PASS 19: Fix Theme.cpp ===
    content = content.replace('sprintf()msg', 'sprintf(msg')
    content = content.replace('sprintf(buf, "Theme', 'sprintf(buf, "Theme')

    # === PASS 20: Fix g_games_resource[0;) -> g_games_resource[0]; ===
    content = content.replace('g_games_resource[0;)', 'g_games_resource[0];')

    # === PASS 21: Fix RegCloseKey(hKey; -> RegCloseKey(hKey); ===
    content = content.replace('RegCloseKey(hKey;)', 'RegCloseKey(hKey);')
    content = content.replace('RegCloseKey(hKey;', 'RegCloseKey(hKey);')

    # === PASS 22: Fix RegOpenKeyExA ===
    content = content.replace('RegOpenKeyExA(HKEY_CURRENT_USER, "Software\\BootyCatalog', 'RegOpenKeyExA(HKEY_CURRENT_USER, "Software\\BootyCatalog')
    content = content.replace('RegOpenKeyExA(HKEY_CURRENT_USER, "Software\\BootyCatalog", 0, KEY_SET_VALUE, &hKey;', 'RegOpenKeyExA(HKEY_CURRENT_USER, "Software\\BootyCatalog", 0, KEY_SET_VALUE, &hKey);')
    content = content.replace('RegSetValueExA(hKey, "Theme", 0, REG_DWORD, (BYTE*)&state, sizeof(DWORD;', 'RegSetValueExA(hKey, "Theme", 0, REG_DWORD, (BYTE*)&state, sizeof(DWORD));')

    # === PASS 23: Fix ListView_SetTextColor ===
    content = content.replace('ListView_SetTextColor(g_hGrid, g_current->text;', 'ListView_SetTextColor(g_hGrid, g_current->text);')

    # === PASS 24: Fix get_theme_name return ===
    content = content.replace('return g_themeState == 0 ? "dark" : "light;', 'return g_themeState == 0 ? "dark" : "light";')

    # === PASS 25: Fix TrackPopupMenu ===
    content = content.replace('TrackPopupMenu(hMenu, TPM_BOTTOMALIGN | TPM_LEFTBUTTON,\n        pt.x, pt.y, 0, g_nid.hWnd, NULL;', 'TrackPopupMenu(hMenu, TPM_BOTTOMALIGN | TPM_LEFTBUTTON,\n        pt.x, pt.y, 0, g_nid.hWnd, NULL);')

    # === PASS 26: Fix CreatePopupMenu missing () ===
    content = content.replace('CreatePopupMenu;', 'CreatePopupMenu();')

    # === PASS 27: Fix http_server_stop/tray_destroy missing () ===
    content = content.replace('http_server_stop;', 'http_server_stop();')
    content = content.replace('tray_destroy;', 'tray_destroy();')
    content = content.replace('PostQuitMessage(0;', 'PostQuitMessage(0);')

    # === PASS 28: Fix ShowWindow/BinWindowToTop missing () ===
    content = content.replace('ShowWindow(hwnd, SW_SHOWNORMAL;', 'ShowWindow(hwnd, SW_SHOWNORMAL);')
    content = content.replace('BringWindowToTop(hwnd;', 'BringWindowToTop(hwnd);')

    # === Fix: GetCursorPos(&pt; -> GetCursorPos(&pt); ===
    content = content.replace('GetCursorPos(&pt;', 'GetCursorPos(&pt);')

    # === Fix: DestroyMenu(hMenu; -> DestroyMenu(hMenu); ===
    content = content.replace('DestroyMenu(hMenu;', 'DestroyMenu(hMenu);')

    # === Fix: BeginPaint(hwnd, &ps; -> BeginPaint(hwnd, &ps); ===
    content = content.replace('BeginPaint(hwnd, &ps;', 'BeginPaint(hwnd, &ps);')

    # === Fix: EndPaint(hwnd, &ps; -> EndPaint(hwnd, &ps); ===
    content = content.replace('EndPaint(hwnd, &ps;', 'EndPaint(hwnd, &ps);')

    # === Fix: SetCursor(LoadCursorA(NULL, IDC_ARROW; -> SetCursor(LoadCursorA(NULL, IDC_ARROW); ===
    content = content.replace('SetCursor(LoadCursorA(NULL, IDC_ARROW;', 'SetCursor(LoadCursorA(NULL, IDC_ARROW);')

    # === Fix: DefWindowProcA(hwnd, msg, wp, lp; -> DefWindowProcA(hwnd, msg, wp, lp); ===
    content = content.replace('DefWindowProcA(hwnd, msg, wp, lp;', 'DefWindowProcA(hwnd, msg, wp, lp);')

    # === Fix: SetTextColor(hdc, RGB(0xa7, 0x8b, 0xfa; -> SetTextColor(hdc, RGB(0xa7, 0x8b, 0xfa); ===
    content = content.replace('SetTextColor(hdc, RGB(0xa7, 0x8b, 0xfa;', 'SetTextColor(hdc, RGB(0xa7, 0x8b, 0xfa);')

    # === Fix: TextOutA(hdc, rect->left + 20, rect->bottom - 30, "All systems operational", 22; ===
    content = content.replace('TextOutA(hdc, rect->left + 20, rect->bottom - 30, "All systems operational", 22;', 'TextOutA(hdc, rect->left + 20, rect->bottom - 30, "All systems operational", 22);')

    # === Fix: strcpy(g->title; -> strcpy(g->title); or similar broken quote ===
    content = content.replace('strcpy(buf, "Today);', 'strcpy(buf, "Today");')

    # === Fix: format_size missing close paren ===
    content = content.replace('sprintf(buf, "%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0;', 'sprintf(buf, "%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0);')

    # === Fix: RepackConfig struct missing brackets ===
    content = content.replace('int delay_ms[7;', 'int delay_ms[7];')

    # === Fix: sizeof(REPACK_COUNT) ===
    content = content.replace('sizeof(REPACK_CONFIGS[0;', 'sizeof(REPACK_CONFIGS[0]);')

    # === Fix: g_grid[idx; -> g_grid[idx] ===
    content = content.replace('g_grid[idx;', 'g_grid[idx]')

    # === Fix: RECT cardRect = { x, y, x + cardW, y + cardH; -> RECT cardRect = { x, y, x + cardW, y + cardH }; ===
    content = content.replace('RECT cardRect = { x, y, x + cardW, y + cardH; };', 'RECT cardRect = { x, y, x + cardW, y + cardH };')
    content = content.replace('RECT cardRect = { x, y, x + cardW, y + cardH; ', 'RECT cardRect = { x, y, x + cardW, y + cardH};')

    # === Fix: RECT gradRect = { cardRect.left, cardRect.top, cardRect.right, cardRect.top + 60; ===
    content = content.replace('RECT gradRect = { cardRect.left, cardRect.top, cardRect.right, cardRect.top + 60; };', 'RECT gradRect = { cardRect.left, cardRect.top, cardRect.right, cardRect.top + 60 };')
    content = content.replace('RECT gradRect = { cardRect.left, cardRect.top, cardRect.right, cardRect.top + 60; ', 'RECT gradRect = { cardRect.left, cardRect.top, cardRect.right, cardRect.top + 60};')

    # === Fix: bi = {0; -> bi = {0}; ===
    content = content.replace('bi = {0;', 'bi = {0};')

    # === Fix: g_filtered[g_filteredCount++; = g_filtered[g_filteredCount++] = ===
    content = content.replace('g_filtered g_filteredCount++]', 'g_filtered[g_filteredCount++]')

    # === Fix: int delay_ms[7; -> int delay_ms[7]; ===
    content = content.replace('int delay_ms[7;', 'int delay_ms[7];')

    # === Fix: strlen(sizeBuf; -> strlen(sizeBuf) ===
    content = content.replace('strlen(sizeBuf;)', 'strlen(sizeBuf));')

    # === Fix: strlen(g->game.title; -> strlen(g->game.title) ===
    content = content.replace('strlen(g->game.title;)', 'strlen(g->game.title));')
    content = content.replace('strlen(g->game.genreLabel;)', 'strlen(g->game.genreLabel));')
    content = content.replace('strlen(g->game.crackedBy;)', 'strlen(g->game.crackedBy));')

    # === Fix: CreatePen missing close paren ===
    content = content.replace('CreatePen(PS_SOLID, 1, RGB(0x2a, 0x3a, 0x52;', 'CreatePen(PS_SOLID, 1, RGB(0x2a, 0x3a, 0x52));')

    # === Fix: SelectObject(hdc, pen; -> SelectObject(hdc, pen); ===
    content = content.replace('SelectObject(hdc, pen;', 'SelectObject(hdc, pen);')

    # === Fix: DeleteObject(pen; -> DeleteObject(pen); ===
    content = content.replace('DeleteObject(pen;', 'DeleteObject(pen);')

    # === Fix: DeleteObject(cardBrush; -> DeleteObject(cardBrush); ===
    content = content.replace('DeleteObject(cardBrush;', 'DeleteObject(cardBrush);')

    # === Fix: DeleteObject(gradBrush; -> DeleteObject(gradBrush); ===
    content = content.replace('DeleteObject(gradBrush;', 'DeleteObject(gradBrush);')

    # === Fix: FillRect(hdc, &cardRect, cardBrush; -> FillRect(hdc, &cardRect, cardBrush); ===
    content = content.replace('FillRect(hdc, &cardRect, cardBrush;', 'FillRect(hdc, &cardRect, cardBrush);')
    content = content.replace('FillRect(hdc, &gradRect, gradBrush;', 'FillRect(hdc, &gradRect, gradBrush);')

    # === Fix: CreateSolidBrush missing close paren ===
    content = content.replace('CreateSolidBrush(RGB(0x15, 0x1d, 0x2e;', 'CreateSolidBrush(RGB(0x15, 0x1d, 0x2e));')
    content = content.replace('CreateSolidBrush(RGB(r, g_, b;', 'CreateSolidBrush(RGB(r, g_, b));')

    # === Fix: CreateSolidBrush(RGB(0x0a, 0x0e, 0x17; ===
    content = content.replace('CreateSolidBrush(RGB(0x0a, 0x0e, 0x17;', 'CreateSolidBrush(RGB(0x0a, 0x0e, 0x17));')

    # === Fix: FillRect(hdc, rect, bgBrush; ===
    content = content.replace('FillRect(hdc, rect, bgBrush;', 'FillRect(hdc, rect, bgBrush);')

    # === Fix: SetTextColor missing close paren ===
    content = content.replace('SetTextColor(hdc, RGB(0x63, 0xb3, 0xed;', 'SetTextColor(hdc, RGB(0x63, 0xb3, 0-ed);')
    content = content.replace('SetTextColor(hdc, RGB(0xa8, 0-b8, 0xcc;', 'SetTextColor(hdc, RGB(0xa8, 0xb8, 0xcc);')
    content = content.replace('SetTextColor(hdc, RGB(0x7e, 0-c8, 0x7e;', 'SetTextColor(hdc, RGB(0x7e, 0xc8, 0x7e);')
    content = content.replace('SetTextColor(hdc, RGB(0x15, 0x1d, 0x2e;', 'SetTextColor(hdc, RGB(0x15, 0x1d, 0x2e);')

    # === Fix: TextOutA missing close paren ===
    content = content.replace('TextOutA(hdc, cardRect.left + 8, cardRect.top + 70,\n                 gi->game.title, (int)strlen(gi->game.title;', 'TextOutA(hdc, cardRect.left + 8, cardRect.top + 70,\n                 gi->game.title, (int)strlen(gi->game.title);')

    # === Fix: memset(&tm, 0, sizeof(tm; ===
    content = content.replace('memset(&tm, 0, sizeof(tm;', 'memset(&tm, 0, sizeof(tm);')

    # === Fix: sscanf missing close paren ===
    content = content.replace('sscanf dateStr, "%d-%d-%d', 'sscanf(dateStr, "%d-%d-%d')

    # === Fix: mktime(&tm; -> mktime(&tm); ===
    content = content.replace('mktime(&tm;', 'mktime(&tm);')

    # === Fix: time(NULL; -> time(NULL); ===
    content = content.replace('time(NULL;', 'time(NULL);')

    # === Fix: difftime(now, t; -> difftime(now, t); ===
    content = content.replace('difftime(now, t;', 'difftime(now, t);')

    # === Fix: (int)(diff / 86400.0; -> (int)(diff / 86400.0); ===
    content = content.replace('(int)(diff / 86400.0;', '(int)(diff / 86400.0);')

    # === Fix: strcmp missing close paren ===
    content = content.replace('strcmp( g_games[i].sources[s], repacker)', 'strcmp(g_games[i].sources[s], repacker)')
    content = content.replace('strcmp( g_games[i].crackedDate, latest->crackedDate)', 'strcmp(g_games[i].crackedDate, latest->crackedDate)')
    content = content.replace('strcmp REPACK_CONFIGS[i].name, g->repack.title)', 'strcmp(REPACK_CONFIGS[i].name, g->repack.title)')
    content = content.replace('strcmp(genre, genres[i] == 0)', 'strcmp(genre, genres[i]) == 0')
    content = content.replace('strcmp( g->crackedDate, latest->crackedDate)', 'strcmp(g->crackedDate, latest->crackedDate)')

    # === Fix: g_games[0; -> g_games[0] ===
    content = content.replace('&g_games[0;', '&g_games[0]')
    content = content.replace('&g_games[i;', '&g_games[i]')

    # === Fix: g->repack.title[0] -> g->repack.title[0] ===
    content = content.replace('g->repack.title[0]', 'g->repack.title[0]')

    # === Fix: genres[] and emojis[] closing bracket ===
    content = content.replace('"racing};', '"racing};')
    content = content.replace('"racing};', '"racing};')
    content = content.replace('em[] = {"\xf0\x9f\x8f\x8e};', 'em[] = {"\xf0\x9f\x8f\x8e};')

    # === Fix: g->tags[t; -> g->tags[t] ===
    content = content.replace('g->tags[t;', 'g->tags[t]')

    # === Fix: g->sources[s; -> g->sources[s] ===
    content = content.replace('g->sources[s;', 'g->sources[s]')

    # === Fix: g_games[i; -> g_games[i] ===
    content = content.replace('g_games[i;', 'g_games[i]')

    # === Fix: g->crackedDate, g->crackedBy, g->size; -> g->crackedDate, g->crackedBy, g->size ===
    content = content.replace('g->crackedDate, g->crackedBy, g->size;', 'g->crackedDate, g->crackedBy, g->size);')

    # === Fix: g->title; -> g->title ===
    content = content.replace('g->title;', 'g->title);')

    # === Fix: g->description; -> g->description ===
    content = content.replace('g->description;', 'g->description);')

    # === Fix: g->imageGradient; -> g->imageGradient ===
    content = content.replace('g->imageGradient;', 'g->imageGradient);')

    # === Fix: g->genreLabel; -> g->genreLabel ===
    content = content.replace('g->genreLabel;', 'g->genreLabel);')

    # === Fix: g->repack.title, g->repack.size, g->repack.url; -> g->repack.title, g->repack.size, g->repack.url ===
    content = content.replace('g->repack.title, g->repack.size, g->repack.url);', 'g->repack.title, g->repack.size, g->repack.url);')

    # === Fix: g->size; -> g->size ===
    content = content.replace('g->size;', 'g->size);')

    # === Fix: g->crackedBy; -> g->crackedBy ===
    content = content.replace('g->crackedBy;', 'g->crackedBy);')

    # === Fix: g->crackedDate; -> g->crackedDate ===
    content = content.replace('g->crackedDate;', 'g->crackedDate);')

    # === Fix: g->isLatest ? "true" : "false; -> g->isLatest ? "true" : "false" ===
    content = content.replace('g->isLatest ? "true" : "false;', 'g->isLatest ? "true" : "false');')

    # === Fix: g->rating; -> g->rating ===
    content = content.replace('g->rating;', 'g->rating);')

    # === Fix: g->genre; -> g->genre ===
    content = content.replace('g->genre;', 'g->genre);')

    # === Fix: g->title; -> g->title ===
    content = content.replace('g->title;', 'g->title);')

    # === Fix: g->id; -> g->id ===
    content = content.replace('g->id;', 'g->id);')

    # === Fix: g->uploadedDate; -> g->uploadedDate ===
    content = content.replace('g->uploadedDate;
