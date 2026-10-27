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
