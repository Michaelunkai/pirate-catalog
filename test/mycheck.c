#include "../include/BootyCatalog.h"
Game g_games[MAX_GAMES]; int g_gameCount = 0;
#include "parser_fn.c"
int main(void){ FILE*f=fopen("../data/games.json","rb"); static char buf[200000]; size_t n=fread(buf,1,sizeof buf,f); fclose(f);
 /* manual re-run with trace */
 char*p=(char*)buf; long steps=0;
 while(*p&&*p!='[')p++; p++; g_gameCount=0;
 while(*p&&g_gameCount<MAX_GAMES){
   while(*p&&(*p==' '||*p=='\n'||*p=='\t'))p++;
   if(*p==']'){fprintf(stderr,"EXIT outer at ] off=%ld\n",p-buf);break;}
   if(*p==','){p++;continue;}
   if(*p!='{'){fprintf(stderr,"EXIT outer non-{ '%c' off=%ld ctx=%.40s\n",*p,p-buf,p);break;}
   p++; Game*g=&g_games[g_gameCount]; memset(g,0,sizeof(Game)); long inr=0;
   while(*p&&*p!='}'){
     inr++;
     while(*p&&(*p==' '||*p=='\n'||*p=='\t'))p++;
     char key[64];int ki=0; if(*p=='"')p++;
     while(*p&&*p!='"'){if(ki<63)key[ki++]=*p;p++;} key[ki]=0; if(*p=='"')p++;
     fprintf(stderr,"  [k=%s] val-start='%c'\n",key,*p);
     while(*p==' ')p++; if(*p==':')p++; while(*p==' ')p++;
     if(*p=='"'){p++;char val[512];int vi=0;while(*p&&*p!='"'){if(vi<511)val[vi++]=*p;p++;}val[vi]=0;if(*p=='"')p++;}
     else if(*p=='t'||*p=='f'||*p=='n'){while(*p&&*p!=','&&*p!='}'&&*p!=']')p++;}
     else if((*p>='0'&&*p<='9')||*p=='-'){while(*p&&*p!=','&&*p!='}'&&*p!=']')p++;}
     else if(*p=='['){p++;while(*p&&*p!=']'){while(*p&&(*p==' '||*p=='\n'||*p=='\t'))p++;if(*p=='"'){p++;while(*p&&*p!='"')p++;if(*p=='"')p++;}if(*p==',')p++;}if(*p==']')p++;}
     else if(*p=='{'){p++;while(*p&&*p!='}'){while(*p&&(*p==' '||*p=='\n'||*p=='\t'))p++;if(*p=='"'){p++;while(*p&&*p!='"')p++;if(*p=='"')p++;while(*p==' ')p++;if(*p==':')p++;while(*p==' ')p++;if(*p=='"'){p++;while(*p&&*p!='"')p++;if(*p=='"')p++;}}if(*p==',')p++;}if(*p=='}')p++;}
     else {fprintf(stderr,"    UNHANDLED val '%c' off=%ld\n",*p,p-buf);while(*p&&*p!=','&&*p!='}')p++;}
   }
   fprintf(stderr,"  inner done, p='%c' off=%ld gcount=%d\n",*p,p-buf,g_gameCount);
   if(*p=='}')p++; g_gameCount++;
 }
 printf("parsed=%d\n",g_gameCount); return 0;}
