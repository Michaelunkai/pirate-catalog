#include "../include/BootyCatalog.h"
Game g_games[MAX_GAMES]; int g_gameCount = 0;
#include "parser_fn.c"
int main(void){ FILE* f=fopen("resources/games.bin","rb"); static char buf[65536]; size_t n=fread(buf,1,sizeof buf,f); fclose(f);
    printf("blob %zu bytes\n",n); int c=parse_games_json(buf,(int)n); printf("parsed %d games\n",c);
    if(c>0){ Game*g=&g_games[c-1]; printf("[last] id=%s title=%.40s rating=%.1f src=%d\n",g->id,g->title,g->rating,g->sourceCount);} return 0;}
