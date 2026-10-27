#!/usr/bin/env python3 -X utf8
"""Binary-safe C++ bug fixer for Booty Catalog."""
import re, os, sys

def fix_file(path):
    # Read as bytes, decode with latin-1 (lossless)
    with open(path, 'rb') as f:
        raw = f.read()
    content = raw.decode('latin-1')

    # Fix: `char hdr[512] int` -> `char hdr[512]; int`
    content = re.sub(r'(\[.*?\])\s+(int|char|const|short|long|float|double|BOOL|DWORD|UINT|RECT|MSG|LPCSTR|LPSTR|WPARAM|LPARAM|HWND|HMENU|HICON|HBRUSH|HPEN|HDC|WNDCLASSEXA|INITCOMMONCONTROLSEX)\b', r'\1; \2', content)

    # Fix: trailing `]` at end of line -> `];`
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.rstrip()
        # Skip already correct
        if stripped.endswith('];'):
            new_lines.append(line)
            continue
        # Lines that are just `char buf[N]` at end (no semicolon)
        if re.match(r'^\s*(char|int|short|long|float|double|const)\s+\w+\[.*\]\s*$', stripped) and not stripped.endswith('];') and not stripped.endswith(' ='):
            new_lines.append(line.rstrip() + ';')
        else:
            new_lines.append(line)
    content = '\n'.join(new_lines)

    # Fix tray_bubble member names
    content = content.replace('g_nid.hIconTip', 'g_nid.hIcon')
    content = content.replace('g_nid.szInfoTip', 'g_nid.szInfo')

    # Fix APP_NAME TEXT() -> direct string for MinGW
    content = content.replace('TEXT("Booty Catalog")', '"Booty Catalog"')
    content = content.replace('TEXT("BootyCatalogWindow")', '"BootyCatalogWindow"')
    content = content.replace('TEXT("1.0.0")', '"1.0.0"')
    content = content.replace('TEXT("1,0,0,0")', '"1,0,0,0"')

    # Fix: `CreatePopupMenu` -> `CreatePopupMenu()`
    content = content.replace('CreatePopupMenuA', 'CreatePopupMenuA()')
    content = content.replace('CreatePopupMenu ', 'CreatePopupMenu() ')

    # Fix: `hIinstance` -> `hInstance`
    content = content.replace('hIinstance', 'hInstance')

    # Fix: `IDC_arrow` -> `IDC_ARROW`
    content = content.replace('IDC_arrow', 'IDC_ARROW')

    # Fix RGB(0xa8, 0xb8, 0_cc) -> RGB(0xa8, 0xb8, 0xcc)
    content = content.replace('0_cc', '0xcc')

    # Fix missing includes
    if '<process.h>' not in content:
        content = '#include <process.h>\n' + content

    # Fix: `sizeof` broken patterns
    content = content.replace('sizeof(icc;', 'sizeof(icc)')
    content = content.replace('sizeof(wcx;', 'sizeof(wcx)')
    content = content.replace('sizeof(g_nid.szTip) - 1;', 'sizeof(g_nid.szTip) - 1')
    content = content.replace('sizeof(g_nid.szInfo) - 1;', 'sizeof(g_nid.szInfo) - 1')
    content = content.replace('sizeof(g_nid.szInfoTip) - 1;', 'sizeof(g_nid.szInfoTip) - 1')
    content = content.replace('sizeof(DWORD);', 'sizeof(DWORD)')
    content = content.replace('sizeof(lvc);', 'sizeof(lvc)')
    content = content.replace('sizeof(tm);', 'sizeof(tm)')

    # Write back as latin-1
    with open(path, 'wb') as f:
        f.write(content.encode('latin-1'))

    print(f"Fixed: {os.path.basename(path)}")

if __name__ == '__main__':
    for name in ['BootyCatalog.cpp', 'Main.cpp', 'GridBrowser.cpp', 'DownloadManager.cpp', 'TrayManager.cpp', 'HtmlRender.cpp', 'WebBrowser.cpp', 'Theme.cpp']:
        fix_file(os.path.join('src', name))
