#!/usr/bin/env python3 -X utf8
import os, re
SRC = r'F:\study\projects\pirate-catalog\src'
dst = os.path.join(SRC, 'BootyCatalog.cpp')
PARTS = ['bc_part1.cpp', 'json1.cpp', 'json2.cpp', 'json3.cpp',
    'bc_part3a1.cpp', 'bc_part3a2.cpp', 'bc_part3a3.cpp',
    'bc_part3a3b.cpp', 'bc_part3b.cpp', 'bc_part3c.cpp',
    'bc_part3e.cpp', 'bc_part3f.cpp', 'bc_part3g.cpp',
    'bc_part3h.cpp']
all_text = ''
for p in PARTS:
    fp = os.path.join(SRC, p)
    if os.path.exists(fp):
        with open(fp, 'r', errors='replace') as f:
            all_text += f.read()
            all_text += '\n'
SZ = r'sizeof\((\w+)\s*;'
all_text = re.sub(SZ, r'sizeof(\1)', all_text)
ST = r'strcpy\(([^;]+)\s*;'
all_text = re.sub(ST, r'strcpy(\1)', all_text)
SN = r'strncpy\(([^;]+)\s*;'
all_text = re.sub(SN, r'strncpy(\1)', all_text)
SP = r'sprintf\(([^;]+)\s*;'
all_text = re.sub(SP, r'sprintf(\1)', all_text)
with open(dst, 'w', encoding='utf-8', errors='replace') as f:
    f.write(all_text)
print(f"Written {len(all_text)} bytes to {dst}")
