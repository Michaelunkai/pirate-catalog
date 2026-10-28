#include "../include/BootyCatalog.h"
Game g_games[MAX_GAMES]; int g_gameCount = 0;
#include "parser_fn.c"
int main(void){ FILE*f=fopen("../.snap.json","rb"); static char buf[200000]; size_t n=fread(buf,1,sizeof buf,f); fclose(f);
 int c=parse_games_json(buf,(int)n); printf("file=%zu parsed=%d\n",n,c);
 if(c>0){ Game*l=&g_games[c-1]; printf("[last] id=%s title=%.30s rating=%.1f src=%d tags=%d\n",l->id,l->title,l->rating,l->sourceCount,l->tagCount);} return 0;}
