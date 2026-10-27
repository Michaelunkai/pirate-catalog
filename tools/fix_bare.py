#!/usr/bin/env python3 -X utf8
"""Binary-safe fix for all .cpp files — target replacements only."""
import os, re

SRC = r'F:\study\projects\pirate-catalog\src'
INC = r'F:\study\projects\pirate-catalog\include'

def fix(path):
    with open(path, 'rb') as f:
        content = f.read().decode('latin-1')
    orig = content
    src = os.path.basename(path)

    # Targeted string replacements (exact patterns that need fixing)
    targets = [
        # ]->; swap in declarations
        ('MAX_GAMES;', 'MAX_GAMES;'),
        ('count[128;', 'count[128;'),
        ('s[i;', 's[i];'),

        # Missing ) before ;
        ('sizeof(g_nid.szTip) - 1;', 'sizeof(g_nid.szTip) - 1);'),
        ('sizeof(g_nid.szInfo) - 1;', 'sizeof(g_nid.szInfo) - 1);'),
        ('sizeof(g_nid.szInfo - 1);', 'sizeof(g_nid.szInfo) - 1);'),

        # szInfoTip -> szInfo (where it still exists)
        ('szInfoTip', 'szInfo'),

        # BIF
        ('BIF_RETURN_FSANCE_ONLY', 'BIF_RETURNFSANCESTORS'),

        # bi = {0;
        ('bi = {0;', 'bi = {0;'),

        # StrLen missing close paren
        ('strlen(APP_NAME;', 'strlen(APP_NAME);'),
        ('strlen(count;', 'strlen(count);'),
        ('strlen(sizeBuf;', 'strlen(sizeBuf);'),
        ('strlen(gi->game.title;', 'strlen(gi->game.title);'),
        ('strlen(gi->game.genreLabel;', 'strlen(gi->game.genreLabel);'),
        ('strlen(gi->game.crackedBy;', 'strlen(gi->game.crackedBy);'),

        # sprintf missing close paren
        ('sprintf(buf, "%lld B", bytes;', 'sprintf(buf, "%lld B", bytes);'),
        ('sprintf(buf, "%.1f KB", bytes / 1024.0;', 'sprintf(buf, "%.1f KB", bytes / 1024.0);'),
        ('sprintf(buf, "%.1f MB", bytes / (1024.0 * 1024.0;', 'sprintf(buf, "%.1f MB", bytes / (1024.0 * 1024.0);'),
        ('sprintf(buf, "%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0;', 'sprintf(buf, "%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0);'),
        ('sprintf(buf, "Today);', 'sprintf(buf, "Today");'),
        ('sprintf(buf, "Yesterday;', 'sprintf(buf, "Yesterday");'),
        ('sprintf(buf, "%d days ago", days;', 'sprintf(buf, "%d days ago", days);'),
        ('sprintf(buf, "%d weeks ago", days / 7;', 'sprintf(buf, "%d weeks ago", days / 7);'),
        ('sprintf(buf, "%d months ago", days / 30;', 'sprintf(buf, "%d months ago", days / 30);'),
        ('sprintf(buf, "%d years ago", days / 365;', 'sprintf(buf, "%d years ago", days / 365;'),

        # sprintf with "Today" broken quote
        ('strcpy(buf, "Today);', 'strcpy(buf, "Today");'),
        ('strcpy(buf, "Yesterday;', 'strcpy(buf, "Yesterday");'),

        # sprintf in HtmlRender
        ('sprintf(count, "Showing %d games from all repacker sources", g_gameCount;', 'sprintf(count, "Showing %d games from all repacker sources", g_gameCount;'),

        # sprintf in GridBrowser format_size
        ('sprintf()buf, "%.1f MB"', 'sprintf(buf, "%.1f MB"'),
        ('sprintf()buf, "%.1f GB"', 'sprintf(buf, "%.1f GB"'),

        # sprintf in theme
        ('sprintf()msg', 'sprintf(msg'),

        # create window ex missing )
        ('CreateWindowExA()', 'CreateWindowExA('),
        ('tray_bubble()APP_NAME', 'tray_bubble(APP_NAME'),

        # _beginthreadex missing )
        ('_beginthreadex()NULL', '_beginthreadex(NULL'),

        # SHBrowseForFolderA missing )
        ('SHBrowseForFolderA()&bi;', 'SHBrowseForFolderA(&bi);'),

        # icc.dwICC flags
        ('ICC_PROGRESS_CLASSES', 'ICC_PROGRESS_CLASS'),

        # strnncpy
        ('strnncpy', 'strncpy'),

        # str -> stristr_func
        ('str(', 'stristr_func('),

        # format_size
        ('format_size()long long', 'format_size(long long'),

        # main.cpp string
        ('g_games_resource[0;)', 'g_games_resource[0];'),
    ]

    # GridBrowser specific format_size fix
    if 'GridBrowser.cpp' in src:
        targets.append(('sprintf()buf, "%.1f MB"', 'sprintf(buf, "%.1f MB"'))
        targets.append(('sprintf()buf, "%.1f GB"', 'sprintf(buf, "%.1f GB"'))

    # Theme.cpp specific
    if 'Theme.cpp' in src:
        targets.append(('sprintf()msg', 'sprintf(msg'))

    for old, new in targets:
        content = content.replace(old, new)

    # Extra: fix strcpy(buf, "Today); → strcpy(buf, "Today");
    content = content.replace('strcpy(buf, "Today);', 'strcpy(buf, "Today");')
    content = content.replace('strcpy(buf, "Yesterday;', 'strcpy(buf, "Yesterday");')

    # Fix sprintf(buf, "%d years ago", days / 365;
    content = content.replace('sprintf(buf, "%d years ago", days / 365;', 'sprintf(buf, "%d years ago", days / 365)')

    # Fix sprintf(count, "Showing %d games from all repacker sources", g_gameCount;
    content = content.replace('sprintf(count, "Showing %d games from all repacker sources", g_gameCount;', 'sprintf(count, "Showing %d games from all repacker sources", g_gameCount;')

    # Fix GridBrowser format_size — the sprintf()buf pattern
    content = content.replace('sprintf()buf, "%.1f MB"', 'sprintf(buf, "%.1f MB"')
    content = content.replace('sprintf()buf, "%.1f GB"', 'sprintf(buf, "%.1f GB"')

    # Fix Theme sprintf()msg
    content = content.replace('sprintf()msg', 'sprintf(msg')

    if content != orig:
        with open(path, 'wb') as f:
            f.write(content.encode('latin-1'))
        print(f'Fixed: {src}')
    else:
        print(f'No change: {src}')

for path in sorted([os.path.join(SRC, f) for f in os.listdir(SRC) if f.endswith('.cpp')]
                  + [os.path.join(INC, f) for f in os.listdir(INC) if f.endswith('.h')]):
    fix(path)
print('All done')
