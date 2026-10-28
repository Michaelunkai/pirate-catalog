#include "../include/BootyCatalog.h"
#include "../src/embedded.h"
int main(void){
    char* p=(char*)games_bin; int len=games_bin_len;
    while(len-->0 && *p!='[') p++;
    printf("found '[' at %ld, next chars:",(long)(p-(char*)games_bin));
    for(int i=1;i<=6;i++) printf("%c",(p[i]>=32&&p[i]<127)?(char)p[i]:'.');
    printf("\n"); return 0;}
