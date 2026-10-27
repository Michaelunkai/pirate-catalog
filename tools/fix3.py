#!/usr/bin/env python3 -X utf8
"""Inline fix assembled BootyCatalog.cpp"""
import os
SRC = r'F:\study\projects\pirate-catalog\src'
src = os.path.join(SRC, 'BootyCatalog.cpp')
with open(src, 'r', encoding='utf-8', errors='replace') as f:
    t = f.read()
SZ = 'sizeof'
t = t.replace('SZ(', SZ + '(')
# Fix missing ) before ;
FIXES = [
    'sizeof(Game)',
    'sizeof(LVCOLUMN)',
    'sizeof(g->repack)',
]
for f in FIXES:
    # Find the corrupted version and replace
    t = t.replace('sizeof(' + f + ';', f + ')')
    t = t.replace('sizeof(' + f + ')', f + ')')
# More specific: line 553 memset(&g->repack => memset(&g->repack)
t = t.replace('memset(&g->repack, 0, SZ(g->repack)', 'memset(&g->repack, 0, SZ(g->repack))')
# Fix game->tags[ => game->tags[
t = t.replace('g->tags[g->tagCount++]', 'g->tags[g->tagCount++]')
t = t.replace('g->tags[g->tagCount++]', 'g->tags[g->tagCount++]')
# Fix game->sources[ => game->sources[
t = t.replace('g->sources[g->sourceCount++]', 'g->sources[g->sourceCount++]')
# Fix game->repack.title[ => game->repack.title[
t = t.replace('g->repack.title[', 'g->repack.title[')
t = t.replace('g->repack.size[', 'g->repack.size[')
t = t.replace('g->repack.url[', 'g->repack.url[')
t = t.replace('g->repack.url[', 'g->repack.url[')
with open(src, 'w', encoding='utf-8', errors='replace') as f:
    f.write(t)
print(f"Fixed: {len(t)} bytes")
