#!/usr/bin/env python3
"""Comprehensive C++ bug fixer for Booty Catalog."""
import re, os, sys

def fix_file(path):
    with open(path, 'r') as f:
        content = f.read()

    # Fix: `char hdr[512] int` -> `char hdr[512]; int`
    # (sed turned [N; into [N] but now we have [N] int which is broken)
    content = re.sub(r'(\[.*?\])\s+(int|char|const|short|long|float|double|BOOL|DWORD|UINT|HWND|HMENU|HICON|RECT|MSG|LPCSTR|LPSTR|WPARAM|LPARAM)\b', r'\1; \2', content)

    # Fix: `char buf[32]` at end of line -> `char buf[32];`
    content = re.sub(r'(\[.*?\])\n', r'\1;\n', content)
    # But only for lines that end with `]` and start with `char `
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.rstrip()
        if stripped.endswith(']') and not stripped.endswith('];') and not stripped.endswith('];') and stripped.strip().startswith('char '):
            new_lines.append(stripped + ';')
        else:
            new_lines.append(line)
    content = '\n'.join(new_lines)

    # Fix tray_bubble member names: hIconTip -> hIcon, szInfoTip -> szInfo
    content = content.replace('g_nid.hIconTip', 'g_nid.hIcon')
    content = content.replace('g_nid.szInfoTip', 'g_nid.szInfo')
    content = content.replace('NIIF_INFO', 'NIIF_INFO')

    # Fix APP_NAME TEXT() -> char* for MinGW
    content = content.replace('TEXT("Booty Catalog")', '"Booty Catalog"')
    content = content.replace('TEXT("BootyCatalogWindow")', '"BootyCatalogWindow"')
    content = content.replace('TEXT("1.0.0")', '"1.0.0"')
    content = content.replace('TEXT("1,0,0,0")', '"1,0,0,0"')

    # Fix: `CreatePopupMenu` -> `CreatePopupMenu()`
    content = content.replace('CreatePopupMenu', 'CreatePopupMenu()')
    content = content.replace('CreatePopupMenuA', 'CreatePopupMenuA()')

    # Fix: `hIinstance` -> `hInstance`
    content = content.replace('hIinstance', 'hInstance')

    # Fix: `IDC_arrow` -> `IDC_ARROW`
    content = content.replace('IDC_arrow', 'IDC_ARROW')

    # Fix: missing include <process.h>
    if '<process.h>' not in content:
        content = '#include <process.h>\n' + content

    # Fix: RGB(0xa8, 0xb8, 0_cc) -> RGB(0xa8, 0xb8, 0xcc)
    content = content.replace('0_cc', '0xcc')

    # Fix: sizeof(icc; -> sizeof(icc)
    content = content.replace('sizeof(', lambda m: m.group(0).replace('(', 'sizeof(') if m.group(0).count('sizeof') else m.group(0))
    # Simpler: just replace common broken patterns
    for broken, good in [
        ('sizeof(icc;', 'sizeof(icc)'),
        ('sizeof(wcx;', 'sizeof(wcx)'),
        ('sizeof(g_nid.szTip) - 1;', 'sizeof(g_nid.szTip) - 1'),
        ('sizeof(g_nid.szInfo) - 1;', 'sizeof(g_nid.szInfo) - 1'),
        ('sizeof(g_nid.szInfoTip) - 1;', 'sizeof(g_nid.szInfoTip) - 1'),
        ('sizeof(DWORD);', 'sizeof(DWORD)'),
        ('sizeof(lvc);', 'sizeof(lvc)'),
        ('sizeof(tm);', 'sizeof(tm)'),
    ]:
        content = content.replace(broken, good)

    with open(path, 'w') as f:
        f.write(content)

    print(f"Fixed: {os.path.basename(path)}")

if __name__ == '__main__':
    for name in ['BootyCatalog.cpp', 'Main.cpp', 'GridBrowser.cpp', 'DownloadManager.cpp', 'TrayManager.cpp', 'HtmlRender.cpp', 'WebBrowser.cpp', 'Theme.cpp']:
        fix_file(os.path.join('src', name))
