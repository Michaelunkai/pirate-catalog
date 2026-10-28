#include "../include/BootyCatalog.h"
#include "../src/embedded.h"
int main(void){
    char* p=(char*)games_bin; int len=games_bin_len;
    while(len-->0 && *p!='[') p++;
    printf("at '[' off=%ld\n",(long)(p-(char*)games_bin));
    p++; 
    // now mimic outer loop start
    while(*p && (*p==' '||*p=='\n'||*p=='\t')) p++;
    printf("after ws: off=%ld c='%c'\n",(long)(p-(char*)games_bin),*p);
    if(*p==']'){printf("break ]\n");return 0;}
    if(*p==','){p++;} else if(*p!='{'){printf("BREAK not { : '%c'\n",*p);return 0;}
    p++;
    printf("entered obj, off=%ld\n",(long)(p-(char*)games_bin));
    return 0;}
