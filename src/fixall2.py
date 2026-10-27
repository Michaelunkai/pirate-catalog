import re, os
f = r'F:\study\projects\pirate-catalog\src\BootyCatalog.cpp'
c = open(f).read()
L = len(c)
# Fix sizeof(X; -> sizeof(X)
c = re.sub(r'sizeof\s*(\([^)]+\))\x3b', lambda m: 'sizeof(' + m.group(1) + ')', c)
# Fix strncpy(a,b,N; -> strncpy(a,b,N)
c = re.sub(r'strncpy\s*(\([^,]+,[^,]+,[\s]*\d+)\x3b', lambda m: 'strncpy(' + m.group(1) + ')', c)
# Fix strcpy(a,b; -> strcpy(a,b)
c = re.sub(r'strcpy\s*(\([^,]+,[^,]+)\x3b', lambda m: 'strcpy(' + m.group(1) + ')', c)
# Fix sprintf(a,b,c; -> sprintf(a,b,c)
c = re.sub(r'sprintf\s*(\([^,]+,[^,]+,[^,]+)\x3b', lambda m: 'sprintf(' + m.group(1) + ')', c)
# Fix strlen(a; -> strlen(a)
c = re.sub(r'strlen\s*(\([^)]+)\x3b', lambda m: 'strlen(' + m.group(1) + ')', c)
# Fix GetModuleHandleA(a; -> GetModuleHandleA(a)
c = re.sub(r'GetModuleHandleA\s*(\([^)]+)\x3b', lambda m: 'GetModuleHandleA(' + m.group(1) + ')', c)
# Fix atoll/atof
c = re.sub(r'(atoll|atof)\x28(\w+)\x3b', r'\1(\2)', c)
# Fix WSACleanup
c = c.replace('WSACleanup\x28\x3b', 'WSACleanup\x29')
# Fix g->field, rv
c = re.sub(r'strncpy\s*(g->repack\.\w+)\x2c\x20rv\x2c\s*(\d+)\x3b', lambda m: 'strncpy(' + m.group(1) + ', rv, ' + m.group(2) + ')', c)
# Fix g->field, val
c = re.sub(r'strncpy\s*(g->\w+)\x2c\x20val\x2c\s*(\d+)\x3b', lambda m: 'strncpy(' + m.group(1) + ', val, ' + m.group(2) + ')', c)
open(f, 'w').write(c)
print('Fixed: %d -> %d' % (L, len(c))strncpy\s*(g->\w+)\x2c\x20(\w+)\x2c\s*(\d+)\x3b', lambda m: 'strncpy(' + m.group(1) + ', ' + m.group(2) + ', ' + m.group(3) + ')', c)

# Fix strncpy with g->field, val
c = re.sub(r'strncpy\s*(g->\w+)\x2c\x20val\x2c\s*(\d+)\x3b', lambda m: 'strncpy(' + m.group(1) + ', val, ' + m.group(2) + ')', c)

# Fix strncpy with g->repack.field, val
c = re.sub(r'strncpy\s*(g->repack\.\w+)\x2c\x20rv\x2c\s*(\d+)\x3b', lambda m: 'strncpy(' + m.group(1) + ', rv, ' + m.group(2) + ')', c)

open(f, 'w').write(c)
print('Fixed: %d -> %d bytes' % (L, len(c))
