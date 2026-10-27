#!/usr/bin/env python3 -X utf8
import os, glob

SRC = r'F:\study\projects\pirate-catalog\src'
dst = os.path.join(SRC, 'BootyCatalog.cpp')

ALL = [
    # Part 1: headers/structs (clean parts only)
    'bc_part1.cpp',
    # JSON parser chunks
    'json1.cpp', 'json2.cpp', 'json3.cpp',
    # Remaining JSON (from json2 continuation)
    'json4.cpp', 'json5.cpp',
    # HTTP server chunks
    'json4.cpp',
    # Theme/emoji
    'bc_part3a1.cpp',
    # Game card HTML
    'bc_part3a3.cpp',
    # MainWndProc chunks (all clean)
    'bc_part3b.cpp',
    'bc_part3c.cpp',
    'bc_part3e.cpp',
    'bc_part3f.cpp',
    'bc_part3g.cpp',
    'bc_part3h.cpp',
    # Other clean files
    'src/DownloadManager.cpp',
    'src/GridBrowser.cpp',
    'src/TrayManager.cpp',
    'src/WebBrowser.cpp',
    'src/Theme.cpp',
    'src/HtmlRender.cpp',
    'src/Main.cpp',
]

parts = []
for f in ALL:
    fp = os.path.join(SRC, f)
    if os.path.exists(fp):
        parts.append(fp)

with open(dst, 'w', encoding='utf-8', errors='replace') as out:
    for fp in parts:
        with open(fp, 'r', encoding='utf-8', errors='replace') as infile:
            out.write(infile.read())
            out.write('\n')

print(f"Assembled {len(parts)} files -> {dst}")
