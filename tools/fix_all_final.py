#!/usr/bin/env python3 -X utf8
"""Final fix for ALL C++ corruption: ]->; swap, spurious ) from fix2, missing )."""
import os, re

SRC = r'F:\study\projects\pirate-catalog\src'
INC = r'F:\study\projects\pirate-catalog\include'

def fix_file(path):
    with open(path, 'rb') as f:
        content = f.read().decode('latin-1')
    orig = content
    src = os.path.basename(path)

    # === PASS 1: Fix ]->; corruption in array brackets ===
    # Pattern: [identifier;  where identifier has no closing ]
    content = re.sub(r'\[([A-Za-z_][\w\d_]*)\;([,\s\)])', r'[\1]\2', content)
    # Nested bracket case: xxx][ci;
    content = re.sub(r'\[([^\]]+)\]\;([,\s)])', r'[\1]]\2', content)
    # Larger bracket patterns: g_theme_colors[g_current_theme][ci;
    content = re.sub(r'\[([^\]]+)\]\;\s*$', r'[\1]]', content)

    # === PASS 2: Fix strn -> strncpy ===
    content = content.replace('strnncpy', 'strncpy')  # double-fix cleanup
    content = re.sub(r'\bstrncpy\(', 'strncpy(', content)  # ensure it's clean
    content = re.sub(r'\bstrn\(\s*', 'strncpy(', content)

    # === PASS 3: Fix str -> stristr_func (where it's the search function) ===
    content = re.sub(r'\bstr\( ', 'stristr_func(', content)  # with space
    content = re.sub(r'\bstr\(( ', 'stristr_func(', content)  # with space after open paren
    content = re.sub(r'\bstr\((\s*[a-zA-Z_]', 'stristr_func(\1', content)  # without space

    # === PASS 4: Fix strlen missing closing paren ===
    content = re.sub(r'strlen\(([^)]+)\s*,\s*0\;?([^)]*)\)',
                     r'strlen(\1, 0\2)', content)
    content = re.sub(r'strlen\(([^)]+)\s*,\s*[0-9]+\;',
                     r'strlen(\1, 0)', content)

    # === PASS 5: Fix spurious ) after function names ===
    # Pattern: function_name() followed by 2+ excess ) before args
    content = re.sub(r'([A-Z][A-Za-z0-9_]+)\(\)\s*\)', r'\1(', content)
    content = re.sub(r'([A-Z][A-Za-z0-9_]+)\(\s*\)\)\s*\)', r'\1(', content)
    content = re.sub(r'([A-Z][A-Za-z0-9_]+)\(\s*\)\s*\)\s*\)\s*\)', r'\1(', content)
    # Heavy chains: function_name)))))...)
    content = re.sub(r'([A-Z][A-Za-z0-9_]+)\(\)\s*\)\)\s*\)\)\s*\)\)\s*\)\s*\)\s*\)', r'\1(', content)
    content = re.sub(r'([A-Z][A-Za-z0-9_]+)\(\s*\)\)\s*\)\)\s*\)\)\s*\)\)', r'\1(', content)
    # Generic heavy chain (7+ parens)
    content = re.sub(r'([A-Z][A-Za-z0-9_]+)\(\s*\)\)\s*\)\)\s*\)\)\s*\)\)\s*\)', r'\1(', content)
    content = re.sub(r'([A-Z][A-Za-z0-9_]+)\(\s*\)\)\s*\)\)\s*\)\)\s*\)\)\s*\)\)\s*\)', r'\1(', content)

    # === PASS 6: Fix missing ) before ; ===
    # send calls
    content = re.sub(r'send\(([^)]+,\s*[^;]+)\s*;\s*\)', r'send(\1)', content)
    # sprintf calls ending with variable
    content = re.sub(r'sprintf\(([^)]+,\s*"[^"]*"[^)]+)\s*;\s*\)', r'sprintf(\1)', content)
    content = re.sub(r'sprintf\(([^)]+,\s*[^;]+)\s*;\s*\)', r'sprintf(\1)', content)

    # === PASS 7: Targeted replacements ===
    targeted = [
        ('g_nid.szInfoTip', 'g_nid.szInfo'),
        ('BIF_RETURN_FSANCE_ONLY', 'BIF_RETURNFSANCESTORS'),
        ('bi = {0;', 'bi = {0;'),  # just clean up if still broken
        ('numval[n]', 'numval[ni]'),
    ]
    for old, new in targeted:
        content = content.replace(old, new)

    # === PASS 8: Specific file fixes ===
    if 'BootyCatalog.cpp' in src:
        fixes = [
            ('lvc.cx = 250; lvc.pszText = (LPSTR)"Genre";"Game Title";',
             'lvc.cx = 250; lvc.pszText = (LPSTR)"Game Title";'),
            ('lvc.cx = 100; lvc.pszText = (LPSTR)',
             'lvc.cx = 100; lvc.pszText = (LPSTR)"Genre";'),
            ('memset()&tm, 0, sizeof(tm);',
             'memset(&tm, 0, sizeof(tm));'),
            ('sscanf(dateStr, "%d-%d-%d", &tm.tm_year, &tm.tm_mon - ;',
             'sscanf(dateStr, "%d-%d-%d", &tm.tm_year, &tm.tm_mon, &tm.tm_mday);'),
        ]
        for old, new in fixes:
            content = content.replace(old, new)

    if 'Main.cpp' in src:
        fixes = [
            ('extern const char* format_size()long long bytes',
             'extern const char* format_size(long long bytes'),
            ('CreateWindowExA()\n        WS_EX',
             'CreateWindowExA(\n        WS_EX'),
            ('tray_bubble()APP_NAME, "Booty Catalog loaded',
             'tray_bubble(APP_NAME, "Booty Catalog loaded'),
            ('g_games_resource[0;)',
             'g_games_resource[0];'),
        ]
        for old, new in fixes:
            content = content.replace(old, new)

    if 'DownloadManager.cpp' in src:
        fixes = [
            ('BROWSEINFOA bi = {0;',
             'BROWSEINFOA bi = {0;'),
            ('SHBrowseForFolderA()&bi;',
             'SHBrowseForFolderA(&bi);'),
        ]
        for old, new in fixes:
            content = content.replace(old, new)

    if 'GridBrowser.cpp' in src:
        fixes = [
            ('format_size(long long bytes',
             'format_size(long long bytes'),
        ]
        for old, new in fixes:
            content = content.replace(old, new)

    if 'WebBrowser.cpp' in src or 'HtmlRender.cpp' in src:
        fixes = [
            ('strlen(sizeBuf;',
             'strlen(sizeBuf)'),
            ('sprintf()buf, "%.1f',
             'sprintf(buf, "%.1f'),
        ]
        for old, new in fixes:
            content = content.replace(old, new)

    if 'Theme.cpp' in src:
        fixes = [
            ('RegSetValueExA()',
             'RegSetValueExA('),
            ('RegSetValueExA(hKey, "Theme)',
             'RegSetValueExA(hKey, "Theme"'),
            ('sizeof(DWORD);',
             'sizeof(DWORD));'),
            ('ListView_SetTextColor()g_hGrid',
             'ListView_SetTextColor(g_hGrid'),
            ('sprintf()msg',
             'sprintf(msg'),
        ]
        for old, new in fixes:
            content = content.replace(old, new)

    if 'HtmlRender.cpp' in src:
        fixes = [
            ('sprintf()))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))buf + i, "  <div class',
             'sprintf(buf + i, "  <div class'),
            ('sprintf())))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))buf + i, "    <div class',
             'sprintf(buf + i, "    <div class'),
        ]
        for old, new in fixes:
            content = content.replace(old, new)

    if content != orig:
        with open(path, 'wb') as f:
            f.write(content.encode('latin-1'))
        print(f'Fixed: {src}')
    else:
        print(f'No change: {src}')

for path in sorted([os.path.join(SRC, f) for f in os.listdir(SRC) if f.endswith('.cpp')]
                  + [os.path.join(INC, f) for f in os.listdir(INC) if f.endswith('.h')]):
    fix_file(path)
print('All done')
