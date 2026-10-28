#include "../include/BootyCatalog.h"
#include "../src/embedded.h"
Game g_games[MAX_GAMES]; int g_gameCount = 0;
#include "parser_fn.c"
int main(void){
    printf("blob=%d\n", games_bin_len);
    printf("parsed %d\n", parse_games_json((void*)games_bin, games_bin_len));
    return 0;}
