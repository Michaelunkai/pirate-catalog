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
