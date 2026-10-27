import os, re
f = r'F:\study\projects\pirate-catalog\src\BootyCatalog.cpp'
c = open(f).read()
old = c

# Fix: sizeof(Game; -> sizeof(Game)
c = c.replace('sizeof\x28Game\x3b', 'sizeof\x28Game\x29')
c = c.replace('sizeof\x28g->repack\x3b', 'sizeof\x28g->repack\x29')
# Fix: array[64; -> array[64]
for name in ['key', 'val', 'numval', 'arrval', 'rk', 'rv']:
    c = c.replace(name + '[32\x3b', name + '[32\x5d')
    c = c.replace(name + '[256\x3b', name + '[256\x5d')
    c = c.replace(name + '[64\x3b', name + '[64\x5d')
# Fix: vi++; -> vi++]
for name in ['ki', 'vi', 'ni', 'ai', 'ri', 'vvi']:
    c = c.replace(name + '++\x3b', name + '++\x5d')
# Fix strncpy commas
for s in ['127\x3b', '31\x3b', '63\x3b', '255\x3b', '15\x3b', '128\x3b']:
    c = c.replace('strncpy(g-' + s, 'strncpy(g-' + s.replace('3b', '29'))
    c = c.replace('strncpy(g->' + s, 'strncpy(g->' + s.replace('3b', '29'))
# Fix function calls
c = c.replace('WSACleanup\x28\x3b', 'WSACleanup\x29')
c = c.replace('strlen(APP_NAME\x28\x3b', 'strlen(APP_NAME\x29')
c = c.replace('SIZEOF(BROWSEINFOA\x3b', 'sizeof\x28BROWSEINFOA\x29')
c = c.replace('sizeof\x28LVCOLUMN\x3b', 'sizeof\x28LVCOLUMN\x29')
c = c.replace('sizeof\x28LVITEMA\x3b', 'sizeof\x28LVITEMA\x29')
c = c.replace('sizeof\x28icc\x3b', 'sizeof\x28icc\x29')
c = c.replace('sizeof\x28wcx\x3b', 'sizeof\x28wcx\x29')
# atoll/atof
c = c.replace('atoll\x28numval\x3b', 'atoll\x28numval\x29')
c = c.replace('atof\x28numval\x3b', 'atof\x28numval\x29')
# strncpy with g->
for fld in ['id', 'title', 'genre', 'genreLabel', 'description', 'crackedBy', 'crackedDate', 'uploadedDate', 'size', 'version', 'imageGradient']:
    c = c.replace('strncpy(g->' + fld + ', val, ', 'strncpy(g->' + fld + ', val, 127)')
    c = c.replace('strncpy(g->' + fld + ', rv, ', 'str strncpy(g->' + fld + ', rv, 63)')
    c = c.replace('strncpy(g->' + fld + ', rv, ', 'strncpy(g->' + fld + ', rv, 63)')

open(f, 'w').write(c)
print('Fixed: %d -> %d bytes' % (len(old), len(c)))
