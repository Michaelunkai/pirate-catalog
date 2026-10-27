#!/usr/bin/env python3 -X utf8
with open(r'F:\study\projects\pirate-catalog\src\BootyCatalog.cpp', 'rb') as f:
    data = f.read()
lines = data.split(b'\r\n')
# Line 275 (0-indexed 274) needs C escape '\\\\' = four bytes: 5c 5c 5c 5c
bs = bytes([0x5c, 0x5c, 0x5c, 0x5c])
q = bytes([0x22])  # "
line = (
    b'                                if (*p == ' +
    bs + b' && *(p+1 == ' + q +
    b') { rv[vvi++ = ' + q + b']; p++; }'
)
lines[274] = line
with open(r'F:\study\projects\pirate-catalog\src\BootyCatalog.cpp', 'wb') as f:
    f.write(b'\r\n'.join(lines))
print('Fixed')
