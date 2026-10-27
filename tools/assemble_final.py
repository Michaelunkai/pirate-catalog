#!/usr/bin/env python3 -X utf8
import os, sys
SRC = r'F:\study\projects\pirate-catalog\src'
dst = os.path.join(SRC, 'BootyCatalog.cpp')
PARTS = [
    'bc_part1.cpp',
    'b2_1.cpp',
    'b2_3.cpp',
    'b2_4.cpp',
    'b2_5.cpp',
    'b3b.cpp',
    'b3c.cpp',
    'bc_part3a.cpp',
    'bc_part3a1.cpp',
    'bc_part3a2.cpp',
    'bc_part3a3.cpp',
    'bc_part3a3b.cpp',
    'bc_part3b.cpp',
    'bc_part3c.cpp',
    'bc_part3d.cpp',
    'bc_part3e.cpp',
    'bc_part3f.cpp',
    'bc_part3g.cpp',
    'bc_part3h.cpp',
    'json1.cpp',
    'json2a.cpp',
    'json2b.cpp',
    'json2c.cpp',
    'json2e.cpp',
    'json2f.cpp',
    'json3.cpp',
    'json4.cpp',
    'b2_http.cpp',
    'src/DownloadManager.cpp',
    'src/GridBrowser.cpp',
    'src/TrayManager.cpp',
    'src/WebBrowser.cpp',
    'src/Theme.cpp',
    'src/HtmlRender.cpp',
    'src/Main.cpp',
]
t = ''
for p in PARTS:
    fp = os.path.join(SRC, p)
    if os.path.exists(fp):
        with open(fp, 'r', errors='replace') as f:
            t += f.read() + '\n'
# Replace SZ() with sizeof()
t = t.replace('SZ(', 'sizeof(')
with open(dst, 'w', encoding='utf-8', errors='replace') as f:
    f.write(t)
print(f"Assembled {len(PARTS)} parts: {len(t)} bytes")
