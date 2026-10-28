#include "../include/BootyCatalog.h"
Game g_games[MAX_GAMES]; int g_gameCount = 0;
#define DBG(x) do{fprintf(stderr,x);}while(0)
#include ".pf.c"
int main(void){ FILE*f=fopen(".sj.json","rb"); static char buf[200000]; size_t n=fread(buf,1,sizeof buf,f); fclose(f);
 int c=parse_games_json(buf,(int)n); printf("file=%zu parsed=%d\n",n,c); return 0;}
