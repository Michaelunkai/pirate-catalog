#include "../include/BootyCatalog.h"
#include "../src/embedded.h"
Game g_games[MAX_GAMES]; int g_gameCount = 0;
int main(void){
    const unsigned char* b=games_bin;
    printf("len=%d\n", games_bin_len);
    for(int i=0;i<40;i++) printf("%c",(b[i]>=32&&b[i]<127)?(char)b[i]:'.');
    printf("\n"); return 0;}
