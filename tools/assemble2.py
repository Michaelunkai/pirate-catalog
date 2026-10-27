#!/usr/bin/env python3 -X utf8
"""Assemble bc_parts into BootyCatalog.cpp, fix corruption."""
import os, re

SRC = r'F:\study\projects\pirate-catalog\src'
dst = os.path.join(SRC, 'BootyCatalog.cpp')

PARTS = [
    'bc_part1.cpp',
    'json1.cpp',
    'json2.cpp',
    'json3.cpp',
    'bc_part3a1.cpp',
    'bc_part3a2.cpp',
    'bc_part3a3.cpp',
    'bc_part3a3b.cpp',
    'bc_part3b.cpp',
    'bc_part3c.cpp',
    'bc_part3e.cpp',
    'bc_part3f.cpp',
    'bc_part3g.cpp',
    'bc_part3h.cpp',
]

all_text = ''
for p in PARTS:
    fp = os.path.join(SRC, p)
    if os.path.exists(fp):
        with open(fp, 'r', errors='replace') as f:
            all_text += f.read()
            all_text += '\n'

# Fix known corruption patterns
# sizeof(X => sizeof(X) (missing closing paren)
all_text = re.sub(r'sizeof\(([a-zA-Z0_]+)\s*;', r'sizeof(\1)', all_text)

# strcpy(s => strcpy(s,) (missing closing paren)
all_text = re.sub(r'strcpy\(([^(;]+)\s*;', r'strcpy(\1)', all_text)
all_text = re.sub(r'strncpy\(([^(;]+)\s*;', r'strncpy(\1)', all_text)

# sprintf(s => sprintf(s,) (missing closing paren)
all_text = re.sub(r'sprintf\(([^(;]+)\s*;', r'sprintf(\1)', all_text)
all_text = re.sub(r'g_card_html\[([^\]]+)\]\s*=\s\'\\\\0\'', r'g_card_html[\1] = \'\\0\'', all_text)

# strncpy(, val, N => strncpy(, val, N); (missing closing paren)
all_text = re.sub(r'strncpy\(([^(]+),\s*val,\s*(\d+)\s*$', r'strncpy(\1, val, \2)', all_text)

# Fix [ => [ (array brackets swapped)
all_text = re.sub(r'\[\s*;', r']', all_text)
all_text = re.sub(r'\s*;\s*\]', r']', all_text)

# Fix ) => ; (function calls swapped)
all_text = re.sub(r'\(\s*;', r')', all_text)
all_text = re.sub(r'\s*;\s*\)', r')', all_text)

with open(dst, 'w', encoding='utf-8', errors='replace') as f:
    f.write(all_text)

print(f"Written {len(all_text)} bytes to {dst}")
