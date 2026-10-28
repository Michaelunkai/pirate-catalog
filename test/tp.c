#include "../include/BootyCatalog.h"
Game g_games[MAX_GAMES]; int g_gameCount = 0;
#include "parser_fn.c"
int main(int argc,char**argv){ FILE* f=fopen(argv[1],"rb"); static char buf[700000]; size_t n=fread(buf,1,sizeof buf,f); fclose(f);
    printf("%s: %zu bytes -> parsed %d\n",argv[1],n,parse_games_json(buf,(int)n)); return 0;}
