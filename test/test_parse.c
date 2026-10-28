#include "../include/BootyCatalog.h"
Game g_games[MAX_GAMES]; int g_gameCount = 0;
#include "parser_fn.c"
int main(void) {
    FILE* f = fopen("data/games.json", "rb");
    static char buf[65536];
    size_t n = fread(buf, 1, sizeof(buf), f); fclose(f);
    printf("file %zu bytes\n", n);
    int cnt = parse_games_json(buf, (int)n);
    printf("parsed %d games\n", cnt);
    if (cnt > 0) {
        Game* last = &g_games[cnt-1];
        printf("[last] id=%s title=%.40s rating=%.1f sources=%d\n", last->id, last->title, last->rating, last->sourceCount);
    }
    return 0;
}
