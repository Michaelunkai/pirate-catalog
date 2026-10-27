use strict;
use warnings;
my $f = 'F:/study/projects/pirate-catalog/src/BootyCatalog.cpp';
open my $fh, '<', $f or die;
my $c = do { local $/; <$fh> };
close $fh;

# Fix p++] → p++; everywhere
$c =~ s/p\]\]\s*/p++;/g;

# Fix strncpy(a,b,N; → strncpy(a,b,N)
$c =~ s/strncpy\(([^,]+,[^,]+,[\s]*\d+)\;/strncpy($1)/g;

# Fix strcpy(a,b; → strcpy(a,b)
$c =~ s/strcpy\(([^,]+,[^,]+)\;/strcpy($1)/g;

# Fix sprintf(a,b,c; → sprintf(a,b,c)
$c =~ s/sprintf\(([^,]+,[^,]+,[^,]+)\;/sprintf($1)/g;

# Fix memset, memset; → memset(...)
$c =~ s/memset\(([^)]+)\;/memset($1)/g;

# Fix SizeofResource, LockResource
$c =~ s/SizeofResource\(([^)]+)\;/SizeofResource($1)/g;
$c =~ s/LockResource\(([^)]+)\;/LockResource($1)/g;

# Fix strncpy g->field with val
$c =~ s/strncpy\((g->[a-zA-Z_]+), val, (\d+)\)/strncpy($1, val, $2)/g;

# Fix strncpy g->repack.field with rv
$c =~ s/strncpy\((g->repack\.[a-zA-Z_]+), rv, (\d+)\)/strncpy($1, rv, $2)/g;

# Fix strncpy g->tags/sources with arrval
$c =~ s/strncpy\((g->[a-zA-Z_]+\[[^\]]*\]), arrval, (\d+)\)/strncpy($1, arrval, $2)/g;

# Fix atoll/atof
$c =~ s/((?:g->sizeBytes = )?)atoll\(numval\)/$1atoll(numval)/g;
$c =~ s/((?:g->rating = )?)\(float\)atof\(numval\)/$1(float)atof(numval)/g;

# Fix strlen
$c =~ s/strlen\(([^)]+)\)/strlen($1)/g;

# Fix GetModuleHandleA
$c =~ s/GetModuleHandleA\(([^)]+)\)/GetModuleHandleA($1)/g;

# Fix strcpy GTA VI
$c =~ s/strcpy\(([^,]+), "C:\\Games"\)/strcpy($1, "C:\\Games")/g;

# Fix memcpy
$c =~ s/memcpy\(([^,]+), (css|js|jsdl), (\w+)\)/memcpy($1, $2, $3)/g;

# Fix malloc
$c =~ s/malloc\((\w+)\)/malloc($1)/g;

# Fix find_resource
$c =~ s/find_resource\(([^)]+)\)/find_resource($1)/g;

# Fix g->sizeBytes = atoll
$c =~ s/g->sizeBytes = atoll\(numval\)/g->sizeBytes = atoll(numval)/g;

# Fix g->rating = (float)atof
$c =~ s/g->rating = \(float\)atof\(numval\)/g->rating = (float)atof(numval)/g;

# Fix g_games[i;
$c =~ s/g_games\[(\w+)\]/g_games[$1]/g;
$c =~ s/g_games\[g_gameCount\]/g_games[g_gameCount]/g;

# Fix array[64] int → array[64]; int
$c =~ s/([a-z]+)\[(\d+)\]\s*int ([a-z]+)/$1[$2]; int $3/g;

# Fix char arrays
$c =~ s/char (\w+)\[([0-9]+)\]/char $1[$2]/g;

# Fix sizeof
$c =~ s/sizeof\(([^)]+)\)/sizeof($1)/g;

# Fix WSACleanup
$c =~ s/WSACleanup\(\)/WSACleanup()/g;

# Fix send
$c =~ s/send\(([^,]+), (hdr|body), ([\w]+), (0)\)/send($1, $2, $3, $4)/g;

# Fix strncpy with "GTA VI
$c =~ s/strncpy\((g->title), "GTA VI", (\d+)\)/strncpy($1, "GTA VI", $2)/g;

# Fix strcpy g->installDir
$c =~ s/strcpy\((g->installDir), "C:\\Games"\)/strcpy($1, "C:\\Games")/g;

# Fix strncpy g->repack with val
$c =~ s/strncpy\((g->repack\.title), rv, (\d+)\)/strncpy($1, rv, $2)/g;

# Fix strncpy g->repack.size
$c =~ s/strncpy\((g->repack\.size), rv, (\d+)\)/strncpy($1, rv, $2)/g;

# Fix strncpy g->repack.url
$c =~ s/strncpy\((g->repack\.url), rv, (\d+)\)/strncpy($1, rv, $2)/g;

open my $out, '>', $f or die;
print $out $c;
close $out;
print "Fixed: %d bytes\n", length($c);
