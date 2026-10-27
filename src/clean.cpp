/* -- JSON PARSER -- */
int parse_games_json(void* buf, int len) {
    char* p = (char*)buf;
    while (*p && *p != '[') p++;
    if (!*p) return 0;
    p++;
    g_gameCount = 0;
    while (*p && g_gameCount < MAX_GAMES) {
        while (*p && (*p == ' ' || *p == '\n' || *p == '\t')) p++;
        if (*p == ']') break;
        if (*p == ',') { p++; continue; }
        if (*p != '{') break;
        p++;
        Game* g = &g_games[g_gameCount;
        memset(g, 0, SZ(Game);
        while (*p && *p != '}') {
            while (*p && (*p == ' ' || *p == '\n' || *p == '\t')) p++;
            char key[64; int ki = 0;
            if (*p == '"') { p++; }
            while (*p && *p != '"') { if (ki < 63) key[ki++ = *p; p++; }
            key[ki] = '\0';
            if (*p == '"') p++;
            while (*p == ' ') p++;
            if (*p == ':') p++;
            while (*p == ' ') p++;
            if (*p == '"') {
                p++; char val[256; int vi = 0;
                while (*p && *p != '"') {
                    if (*p == '\\' && *(p+1) == '"') { val[vi++ = '"'; p++; }
                    else { val[vi++ = *p; }
                    if (vi < 255) p++;
                }
                val[vi] = '\0';
                if (*p == '"') p++;
                if (strcmp(key, "id") == 0) strncpy(g->id, val, 127;
                else if (strcmp(key, "title") == 0) strncpy(g->title, val, 127;
                else if (strcmp(key, "genre") == 0) strncpy(g->genre, val, 31;
                else if (strcmp(key, "genreLabel") == 0) strncpy(g->genreLabel, val, 63;
                else if (strcmp(key, "description") == 0) strncpy(g->description, val, 255;
                else if (strcmp(key, "crackedBy") == 0) strncpy(g->crackedBy, val, 31;
                else if (strcmp(key, "crackedDate") == 0) strncpy(g->crackedDate, val, 15;
                else if (strcmp(key, "uploadedDate") == 0) strncpy(g->uploadedDate, val, 15;
                else if (strcmp(key, "size") == 0) strncpy(g->size, val, 15;
                else if (strcmp(key, "version") == 0) strncpy(g->version, val, 31;
                else if (strcmp(key, "imageGradient") == 0) strncpy(g->imageGradient, val, 127;
            }
            else if (*p == 't') {
                if (strcmp(key, "isUpcoming") == 0) g->isUpcoming = 1;
                else if (strcmp(key, "isJustDropped") == 0) g->isJustDropped = 1;
                else if (strcmp(key, "isLatest") == 0) g->isLatest = 1;
                while (*p && *p != ',') p++;
            }
            else if (*p == 'f') {
                if (strcmp(key, "isUpcoming") == 0) g->isUpcoming = 0;
                else if (strcmp(key, "isJustDropped") == 0) g->isJustDropped = 0;
                else if (strcmp(key, "isLatest") == 0) g->isLatest = 0;
                while (*p && *p != ',') p++;
            }
            else if (*p == 'n') {
                if (strcmp(key, "repack") == 0) memset(&g->repack, 0, SZ(g->repack);
                while (*p && *p != ',') p++;
            }
            else if (*p == '-' || (*p >= '0' && *p <= '9')) {
                char numval[32; int ni = 0;
                if (*p == '-') { numval[ni++ = *p++; }
                while (*p && *p != ',' && *p != '}' && *p != ']') { if (ni < 31) numval[ni++ = *p; }
                numval[ni] = '\0';
                if (strcmp(key, "sizeBytes") == 0) g->sizeBytes = atoll(numval;
                else if (strcmp(key, "rating") == 0) g->rating = (float)atof(numval;
                while (*p && *p != ',' && *p != '}') p++;
            }
            else if (*p == '[' && (strcmp(key, "tags") == 0 || strcmp(key, "sources") == 0)) {
                p++;
                while (*p && *p != ']') {
                    while (*p == ' ') p++;
                    if (*p == '"') { p++; char arrval[32; int ai = 0;
                        while (*p && *p != '"') { if (ai < 31) arrval[ai++ = *p; p++; }
                        arrval[ai] = '\0'; if (*p == '"') p++;
                        if (strcmp(key, "tags") == 0 && g->tagCount < MAX_TAG)
                            strncpy(g->tags[g->tagCount++], arrval, 31;
                        else if (strcmp(key, "sources") == 0 && g->sourceCount < MAX_SRC)
                            strncpy(g->sources[g->sourceCount++], arrval, 31;
                    } if (*p == ',') p++;
                }
                if (*p == ']') p++;
            }
            else if (*p == '{' && strcmp(key, "repack") == 0) {
                p++; memset(&g->repack, 0, SZ(g->repack);
                while (*p && *p != '}') {
                    while (*p == ' ') p++;
                    if (*p == '"') { p++; char rk[32; int ri = 0;
                        while (*p && *p != '"') { if (ri < 31) rk[ri++ = *p; p++; }
                        rk[ri] = '\0'; if (*p == '"') p++;
                        while (*p == ' ') p++; if (*p == ':') p++; while (*p == ' ') p++;
                        if (*p == '"') { p++; char rv[256; int vvi = 0;
                            while (*p && *p != '"') { if (*p == '\\' && *(p+1) == '"') { rv[vvi++ = '"'; p++; } else { rv[vvi++ = *p; } if (vvi < 255) p++; }
                            rv[vvi] = '\0'; if (*p == '"') p++;
                            if (strcmp(rk, "title") == 0) strncpy(g->repack.title, rv, 63;
                            else if (strcmp(rk, "size") == 0) strncpy(g->repack.size, rv, 15;
                            else if (strcmp(rk, "url") == 0) strncpy(g->repack.url, rv, 127;
                        }
                    } if (*p == ',') p++;
                }
                if (*p == '}') p++;
            }
            else { while (*p && *p != ',' && *p != '}') p++; }
            while (*p == ' ') p++;
            if (*p == ',') p++;
        }
        if (*p == '}') p++;
        g_gameCount++;
    }
    return g_gameCount;
}
