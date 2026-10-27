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
