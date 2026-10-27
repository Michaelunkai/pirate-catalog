f = r'F:\study\projects\pirate-catalog\src\BootyCatalog.cpp'
c = open(f).read()
L = len(c)

# p++] → p++; (very common)
c = c.replace('p++]', 'p++;')
# memset g;
c = c.replace('memset(g, 0, (int)sizeof(Game)', 'memset(g, 0, (int)sizeof(Game)')
# strncpy corruption: 127)127) → 127)
c = c.replace('127)127)', '127)')
c = c.replace('31)31)', '31)')
c = c.replace('63)63)', '63)')
c = c.replace('255)255)', '255)')
c = c.replace('15)15)', '15)')
c = c.replace('128)128)', '128)')
# vi++; → vi++
c = c.replace('vi++]', 'vi++')
c = c.replace('ni++]', 'ni++')
c = c.replace('ai++]', 'ai++')
c = c.replace('ri++]', 'ri++')
c = c.replace('vvi++]', 'vvi++')
c = c.replace('ki++]', 'ki++')
# strncpy(g->field, val, X; → strncpy(g->field, val, X)
c = c.replace('strncpy(g->id, val, 127)', 'strncpy(g->id, val, 127)')
c = c.replace('strncpy(g->title, val, 127)', 'strncpy(g->title, val, 127)')
c = c.replace('strncpy(g->genre, val, 127)', 'strncpy(g->genre, val, 31)')
c = c.replace('strncpy(g->genreLabel, val, 127)', 'strncpy(g->genreLabel, val, 63)')
c = c.replace('strncpy(g->description, val, 127)', 'strncpy(g->description, val, 255)')
c = c.replace('strncpy(g->crackedBy, val, 127)', 'strncpy(g->crackedBy, val, 31)')
c = c.replace('strncpy(g->crackedDate, val, 127)', 'strncpy(g->crackedDate, val, 15)')
c = c.replace('strncpy(g->uploadedDate, val, 127)', 'strncpy(g->uploadedDate, val, 15)')
c = c.replace('strncpy(g->size, val, 127)', 'strncpy(g->size, val, 15)')
c = c.replace('strncpy(g->version, val, 127)', 'strncpy(g->version, val, 31)')
c = c.replace('strncpy(g->imageGradient, val, 127)', 'strncpy(g->imageGradient, val, 127)')
# strncpy g->repack, rv
c = c.replace('strncpy(g->repack.title, rv, 63)', 'strncpy(g->repack.title, rv, 63)')
c = c.replace('strncpy(g->repack.size, rv, 15)', 'strncpy(g->repack.size, rv, 15)')
c = c.replace('strncpy(g->repack.url, rv, 127)', 'strncpy(g->repack.url, rv, 127)')
# strncpy g->tags, g->sources arrval 31
c = c.replace('strncpy(g->tags[g->tagCount++], arrval, 31)', 'strncpy(g->tags[g->tagCount++], arrval, 31)')
c = c.replace('strncpy(g->sources[g->sourceCount++], arrval, 31)', 'strncpy(g->sources[g->sourceCount++], arrval, 31)')
# sizeof fixes
c = c.replace('sizeof(g_httpServer.addr)', 'sizeof(g_httpServer.addr)')
c = c.replace('sizeof(REPACK_CONFIGS) / sizeof(REPACK_CONFIGS[0)', 'sizeof(REPACK_CONFIGS) / sizeof(REPACK_CONFIGS[0])')
c = c.replace('sizeof(BROWSEINFOA)', 'sizeof(BROWSEINFOA)')
c = c.replace('sizeof(NOTIFYICONDATAA)', 'sizeof(NOTIFYICONDATAA)')
c = c.replace('sizeof(LVCOLUMN)', 'sizeof(LVCOLUMN)')
c = c.replace('sizeof(LVITEMA)', 'sizeof(LVITEMA)')
c = c.replace('sizeof(icc)', 'sizeof(icc)')
c = c.replace('sizeof(wcx)', 'sizeof(wcx)')
c = c.replace('sizeof(Game)', 'sizeof(Game)')
# atoll/atof fixes
c = c.replace('atoll(numval)', 'atoll(numval)')
c = c.replace('atof(numval)', 'atof(numval)')
# WSACleanup
c = c.replace('WSACleanup()', 'WSACleanup()')
# strlen
c = c.replace('strlen(APP_NAME)', 'strlen(APP_NAME)')
# GetModuleHandle
c = c.replace('GetModuleHandleA(NULL)', 'GetModuleHandleA(NULL)')
# strncpy g->title GTA VI
c = c.replace('strncpy(g->title, "GTA VI", 127)', 'strncpy(g->title, "GTA VI", 127)')
# strcpy
c = c.replace('strcpy(g->installDir, "C:\\Games"', 'strcpy(g->installDir, "C:\\Games")')
# send
c = c.replace('send(client, body, bodyLen, 0)', 'send(client, body, bodyLen, 0)')
# memcpy
c = c.replace('memcpy(body + b, css, cssLen)', 'memcpy(body + b, css, cssLen)')
c = c.replace('memcpy(body + b, js, jsLen)', 'memcpy(body + b, js, jsLen)')
c = c.replace('memcpy(body + b, jsdl, jsdlLen)', 'memcpy(body + b, jsdl, jsdlLen)')
# malloc
c = c.replace('malloc(bodyLen)', 'malloc(bodyLen)')
# find_resource
c = c.replace('find_resource(hInst, 1001, RT_RCDATA)', 'find_resource(hInst, 1001, RT_RCDATA)')
# sizeBytes atoll
c = c.replace('g->sizeBytes = atoll(numval)', 'g->sizeBytes = atoll(numval)')
# rating atof
c = c.replace('g->rating = (float)atof(numval)', 'g->rating = (float)atof(numval)')
# g_games[i;
c = c.replace('g_games[i]', 'g_games[i]')
# g_games[g_gameCount;
c = c.replace('g_games[g_gameCount]', 'g_games[g_gameCount]')
# array[64] int
c = c.replace('key[64] int ki', 'key[64]; int ki')
c = c.replace('val[256] int vi', 'val[256]; int vi')
c = c.replace('numval[32] int ni', 'numval[32]; int ni')
c = c.replace('arrval[32] int ai', 'arrval[32]; int ai')
c = c.replace('rk[32] int ri', 'rk[32]; int ri')
c = c.replace('rv[256] int vvi', 'rv[256]; int vvi')
# char arrays
c = c.replace('char hdr[1024]', 'char hdr[128]')
c = c.replace('char body[16384]', 'char body[16384]')
c = c.replace('char buf[512]', 'char buf[512]')
# strncpy with val 31→31)
c = c.replace('strncpy(g->repack.title, rv, 63)', 'strncpy(g->repack.title, rv, 63)')

open(f, 'w').write(c)
print 'Fixed: %d bytes processed' % L
