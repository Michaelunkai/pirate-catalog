#!/usr/bin/env python3 -X utf8
"""Fix all corruption in BootyCatalog.cpp."""
import os

SRC = r'F:\study\projects\pirate-catalog\src'
src = os.path.join(SRC, 'BootyCatalog.cpp')

with open(src, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

out = []
for i, line in enumerate(lines):
    # Fix key[64] => key[64]
    if 'char key[64] int' in line:
        line = line.replace('char key[64] int', 'char key[64]; int')
    # Fix val[256] int => val[256]; int
    if 'char val[256] int' in line:
        line = line.replace('char val[256] int', 'char val[256]; int')
    # Fix numval[32] int => numval[32]; int
    if 'char numval[32] int' in line:
        line = line.replace('char numval[32] int', 'char numval[32]; int')
    # Fix SZ(X => SZ(X)
    if 'SZ(g->repack)' in line:
        line = line.replace('SZ(g->repack)', 'SZ(g->repack))')
    # Fix memset(&g->repack, 0, SZ(g->repack) => memset(&g->repack, 0, SZ(g->repack))
    if 'memset(&g->repack, 0, SZ(g->repack)' in line and 'SZ(g->repack))' not in line:
        line = line.replace('SZ(g->repack)', 'SZ(g->repack))')
    out.append(line)

with open(src, 'w', encoding='utf-8', errors='replace') as f:
    f.writelines(out)

print(f"Fixed {len(lines) - len(out)} lines")
