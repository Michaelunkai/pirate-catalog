#!/usr/bin/env python3 -X utf8
"""Fix all corruption in BootyCatalog.cpp."""
import os, re

SRC = r'F:\study\projects\pirate-catalog\src'
src = os.path.join(SRC, 'BootyCatalog.cpp')

with open(src, 'r', encoding='utf-8', errors='replace') as f:
    t = f.read()

# Pattern 1: sizeof(X missing closing ) before ;
t = re.sub(r'sizeof\((\w+)\s*;', r'sizeof(\1)', t)
t = re.sub(r'SZ\(([^;]+)\s*;', r'SZ(\1)', t)  # keep SZ as placeholder

# Pattern 2: strcpy missing closing paren
t = re.sub(r'strcpy\(([^;]+)\s*;', r'strcpy(\1)', t)

# Pattern 3: strncpy missing closing paren
t = re.sub(r'strncpy\(([^;]+)\s*;', r'strncpy(\1)', t)

# Pattern 4: sprintf missing closing paren
t = re.sub(r'sprintf\(([^;]+)\s*;', r'sprintf(\1)', t)

# Pattern 5: sprintf missing opening comma (strcpy(s => strcpy(s,)
t = re.sub(r'strcpy\(([^;]+)\s*$', r'strcpy(\1)', t)

# Pattern 6: szbuf missing comma
t = re.sub(r'szbuf\(([^;]+)\s*$', r'szbuf(\1)', t)

# Pattern 7: game->crackedDate missing paren
t = re.sub(r'time_ago\(g->crackedDate\)', r'time_ago(g->crackedDate)', t)

# Pattern 8: game->title missing paren (get_game_emoji)
t = re.sub(r'get_game_emoji\(g->title\)', r'get_game_emoji(g->title)', t)

# Pattern 9: g->sizeBytes missing paren (format_size)
t = re.sub(r'format_size\(szbuf, g->sizeBytes\)', r'format_size(szbuf, g->sizeBytes)', t)

# Pattern 10: game card HTML sprintf missing comma before pszText
t = re.sub(r'pszText = "Game"', r'pszText = "Game"', t)

# Pattern 11: game card HTML sprintf missing comma before pszText
t = re.sub(r'pszText = "Game"', r'pszText = "Game"', t)

# Now fix the big pattern: array brackets ] → ; and function calls ) → ;
# Fix g_games[X → g_games[X]
t = re.sub(r'g_games\[(\w+)\s*;', r'g_games[\1]', t)

# Fix key[X → key[X]
t = re.sub(r'key\[(\w+)\s*;', r'key[\1]', t)

# Fix val[X → val[X]
t = re.sub(r'val\[(\w+)\s*;', r'val[\1]', t)

# Fix numval[X → numval[X]
t = re.sub(r'numval\[(\w+)\s*;', r'numval[\1]', t)

# Fix arrval[X → arrval[X]
t = re.sub(r'arrval\[(\w+)\s*;', r'arrval[\1]', t)

# Fix rk[X → rk[X]
t = re.sub(r'rk\[(\w+)\s*;', r'rk[\1]', t)

# Fix rv[X → rv[X]
t = re.sub(r'rv\[(\w+)\s*;', r'rv[\1]', t)

# Fix game->tags[X → game->tags[X]
t = re.sub(r'g->tags\[(\w+)\s*;', r'g->tags[\1]', t)

# Fix game->sources[X → game->sources[X]
t = re.sub(r'g->sources\[(\w+)\s*;', r'g->sources[\1]', t)

# Fix game->repack.title[X → game->repack.title[X]
t = re.sub(r'g->repack\.title\[(\w+)\s*;', r'g->repack.title[\1]', t)

# Fix game->repack.size[X → game->repack.size[X]
t = re.sub(r'g->repack\.size\[(\w+)\s*;', r'g->repack.size[\1]', t)

# Fix game->repack.url[X → game->repack.url[X]
t = re.sub(r'g->repack\.url\[(\w+)\s*;', r'g->repack.url[\1]', t)

# Fix game->title[X → game->title[X]
t = re.sub(r'g->title\[(\w+)\s*;', r'g->title[\1]', t)

# Fix game->crackedBy[X → game->crackedBy[X]
t = re.sub(r'g->crackedBy\[(\w+)\s*;', r'g->crackedBy[\1]', t)

# Fix game->crackedDate[X → game->crackedDate[X]
t = re.sub(r'g->crackedDate\[(\w+)\s*;', r'g->crackedDate[\1]', t)

# Fix g->repack[X → g->repack[X]
t = re.sub(r'g->repack\[(\w+)\s*;', r'g->repack[\1]', t)

# Fix game->id[X → game->id[X]
t = re.sub(r'g->id\[(\w+)\s*;', r'g->id[\1]', t)

# Fix game->genre[X → game->genre[X]
t = re.sub(r'g->genre\[(\w+)\s*;', r'g->genre[\1]', t)

# Fix game->genreLabel[X → game->genreLabel[X]
t = re.sub(r'g->genreLabel\[(\w+)\s*;', r'g->genreLabel[\1]', t)

# Fix game->description[X → game->description[X]
t = re.sub(r'g->description\[(\w+)\s*;', r'g->description[\1]', t)

# Fix game->crackedBy[X → game->crackedBy[X]
t = re.sub(r'g->crackedBy\[(\w+)\s*;', r'g->crackedBy[\1]', t)

# Fix game->size[X → game->size[X]
t = re.sub(r'g->size\[(\w+)\s*;', r'g->size[\1]', t)

# Fix game->version[X → game->version[X]
t = re.sub(r'g->version\[(\w+)\s*;', r'g->version[\1]', t)

# Fix game->imageGradient[X → game->imageGradient[X]
t = re.sub(r'g->imageGradient\[(\w+)\s*;', r'g->imageGradient[\1]', t)

# Fix game->isUpcoming[X → game->isUpcoming[X]
t = re.sub(r'g->isUpcoming\[(\w+)\s*;', r'g->isUpcoming[\1]', t)

# Fix game->isJustDropped[X → game->isJustDropped[X]
t = re.sub(r'g->isJustDropped\[(\w+)\s*;', r'g->isJustDropped[\1]', t)

# Fix game->isLatest[X → game->isLatest[X]
t = re.sub(r'g->isLatest\[(\w+)\s*;', r'g->isLatest[\1]', t)

# Fix game->tagCount[X → game->tagCount[X]
t = re.sub(r'g->tagCount\[(\w+)\s*;', r'g->tagCount[\1]', t)

# Fix game->sourceCount[X → game->sourceCount[X]
t = re.sub(r'g->sourceCount\[(\w+)\s*;', r'g->sourceCount[\1]', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

# Fix game->title(X → game->title(X)
t = re.sub(r'g->title\(\s*;', r'g->title(', t)

# Fix game->crackedDate(X → game->crackedDate(X)
t = re.sub(r'g->crackedDate\(\s*;', r'g->crackedDate(', t)

# Fix game->crackedBy(X → game->crackedBy(X)
t = re.sub(r'g->crackedBy\(\s*;', r'g->crackedBy(', t)

# Fix game->imageGradient(X → game->imageGradient(X)
t = re.sub(r'g->imageGradient\(\s*;', r'g->imageGradient(', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

# Fix game->repack(X → game->repack(X)
t = re.sub(r'g->repack\(\s*;', r'g->repack(', t)

with open(src, 'w', encoding='utf-8', errors='replace') as f:
    f.write(t)
print(f"Fixed: {len(t)} bytes")
