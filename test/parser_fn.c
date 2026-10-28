int parse_games_json(void* buf, int len) {
    char* p = (char*)buf;
    setbuf(stdout, NULL); setbuf(stderr, NULL);
    long dbg_steps = 0;
    while (len-- > 0 && *p != '[') p++;
    if (*p != '[') return 0;
    p++; g_gameCount = 0;
    while (*p && g_gameCount < MAX_GAMES) {
        dbg_steps++;
        if (dbg_steps > 100000) { fprintf(stderr, "PARSE LOOP at offset %ld\n", p - (char*)buf); return g_gameCount; }
        while (*p && (*p == ' ' || *p == '\n' || *p == '\t')) p++;
        if (*p == ']') break;
        if (*p == ',') { p++; continue; }
        if (*p != '{') break;
        p++;
        Game* g = &g_games[g_gameCount];
        memset(g, 0, sizeof(Game));
        long dbg_inner = 0;
        while (*p && *p != '}') {
            dbg_inner++;
            if (g_gameCount == 0) { fprintf(stderr,"P%d@%ld '%c'", g_gameCount,(long)(p-(char*)buf),*p); }
            if (dbg_inner > 500) { fprintf(stderr,"\nTRIP off=%ld ctx=%.200s\n", (long)(p-(char*)buf), p-40 >= (char*)buf ? p-40 : (char*)buf); return g_gameCount; }
            while (*p && (*p == ' ' || *p == '\n' || *p == '\t')) p++;
            if (*p == '}') break;
            char key[64]; int ki = 0;
            if (*p == '"') p++;
            while (*p && *p != '"') { if (ki < 63) key[ki++] = *p; p++; }
            key[ki] = '\0'; if (*p == '"') p++;
            fprintf(stderr, "[g%d off=%ld k=%.20s]\n", g_gameCount, (long)(p-(char*)buf), key);
            while (*p == ' ') p++; if (*p == ':') p++; while (*p == ' ') p++;
            if (*p == '"') {
                p++; char val[256]; int vi = 0;
                while (*p && *p != '"') {
                    char c = *p;
                    if (c == '\\' && p[1]) { p++; c = *p; }
                    if (vi < 255) val[vi++] = c;
                    p++;
                    if (++dbg_steps > 1000000) { fprintf(stderr, "STRVAL spin off=%ld ctx=%.40s\n", (long)(p-(char*)buf), p); return g_gameCount; }
                }
                val[vi] = '\0'; if (*p == '"') p++;
                if (strcmp(key, "id") == 0) strncpy(g->id, val, 127);
                else if (strcmp(key, "title") == 0) strncpy(g->title, val, 127);
                else if (strcmp(key, "genre") == 0) strncpy(g->genre, val, 31);
                else if (strcmp(key, "genreLabel") == 0) strncpy(g->genreLabel, val, 63);
                else if (strcmp(key, "description") == 0) strncpy(g->description, val, 255);
                else if (strcmp(key, "crackedBy") == 0) strncpy(g->crackedBy, val, 31);
                else if (strcmp(key, "crackedDate") == 0) strncpy(g->crackedDate, val, 15);
                else if (strcmp(key, "uploadedDate") == 0) strncpy(g->uploadedDate, val, 15);
                else if (strcmp(key, "size") == 0) strncpy(g->size, val, 15);
                else if (strcmp(key, "version") == 0) strncpy(g->version, val, 31);
                else if (strcmp(key, "imageGradient") == 0) strncpy(g->imageGradient, val, 127);
            } else if (*p == 't') {
                if (strcmp(key, "isUpcoming") == 0) g->isUpcoming = 1;
                else if (strcmp(key, "isJustDropped") == 0) g->isJustDropped = 1;
                else if (strcmp(key, "isLatest") == 0) g->isLatest = 1;
                while (*p && *p != ',') p++;
            } else if (*p == 'f') {
                if (strcmp(key, "isUpcoming") == 0) g->isUpcoming = 0;
                else if (strcmp(key, "isJustDropped") == 0) g->isJustDropped = 0;
                else if (strcmp(key, "isLatest") == 0) g->isLatest = 0;
                while (*p && *p != ',') p++;
            } else if (*p == 'n') {
                if (strcmp(key, "repack") == 0) memset(&g->repack, 0, sizeof(g->repack));
                while (*p && *p != ',') p++;
            } else if (*p == '-' || (*p >= '0' && *p <= '9')) {
                char numval[32]; int ni = 0;
                if (*p == '-') { numval[ni++] = *p++; }
                while (*p && *p != ',' && *p != '}' && *p != ']') { if (ni < 31) numval[ni++] = *p; p++; }
                numval[ni] = '\0';
                if (strcmp(key, "sizeBytes") == 0) g->sizeBytes = atoll(numval);
                else if (strcmp(key, "rating") == 0) g->rating = (float)atof(numval);
                while (*p && *p != ',' && *p != '}') p++;
            } else if (*p == '[' && (strcmp(key, "tags") == 0 || strcmp(key, "sources") == 0)) {
                p++;
                while (*p && *p != ']') { dbg_steps++;
                    while (*p && (*p==' '||*p=='\n'||*p=='\t')) p++;
                    if (*p == '"') { p++; char arrval[32]; int ai = 0;
                        while (*p && *p != '"') { if (ai < 31) arrval[ai++] = *p; p++; }
                        arrval[ai] = '\0'; if (*p == '"') p++;
                        if (strcmp(key, "tags") == 0 && g->tagCount < MAX_TAG)
                            strncpy(g->tags[g->tagCount++], arrval, 31);
                        else if (strcmp(key, "sources") == 0 && g->sourceCount < MAX_SRC)
                            strncpy(g->sources[g->sourceCount++], arrval, 31);
                    } if (*p == ',') p++;
                }
                if (*p == ']') p++;
            } else if (*p == '{' && strcmp(key, "repack") == 0) {
                p++; memset(&g->repack, 0, sizeof(g->repack));
                while (*p && *p != '}') {
                    while (*p && (*p==' '||*p=='\n'||*p=='\t')) p++;
                    if (*p == '"') { p++; char rk[32]; int ri = 0;
                        while (*p && *p != '"') { if (ri < 31) rk[ri++] = *p; p++; }
                        rk[ri] = '\0'; if (*p == '"') p++;
                        while (*p==' '||*p=='\n'||*p=='\t') p++; if (*p == ':') p++; while (*p==' '||*p=='\n'||*p=='\t') p++;
                        if (*p == '"') { p++; char rv[256]; int vvi = 0;
                            while (*p && *p != '"') {
                                char rc = *p;
                                if (rc == '\\' && p[1]) { p++; rc = *p; }
                                if (vvi < 255) rv[vvi++] = rc;
                                p++;
                            }
                            rv[vvi] = '\0'; if (*p == '"') p++;
                            if (strcmp(rk, "title") == 0) strncpy(g->repack.title, rv, 63);
                            else if (strcmp(rk, "size") == 0) strncpy(g->repack.size, rv, 15);
                            else if (strcmp(rk, "url") == 0) strncpy(g->repack.url, rv, 127);
                        }
                    } if (*p == ',') p++;
                }
                if (*p == '}') p++;
            } else { while (*p && *p != ',' && *p != '}') p++; }
            while (*p == ' ') p++;
            if (*p == ',') p++;
        }
        if (*p == '}') p++;
        g_gameCount++;
    }
    return g_gameCount;
}
