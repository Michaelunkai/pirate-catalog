# gen_cpp.py — generates BootyCatalog.cpp from hex chunks
import os, base64
BASE = r'F:\study\projects\pirate-catalog\src'
chunks = []
for i in range(1, 10):
    p = os.path.join(BASE, 'chunk_%02d.b64' % i)
    if not os.path.exists(p): break
    chunks.append(open(p).read())
    print('chunk %d: %d bytes' % (i, len(open(p).read())))
raw = base64.b64decode('\n'.join(chunks)).decode('utf-8')
with open(os.path.join(BASE, 'BootyCatalog.cpp'), 'w') as f:
    f.write(raw)
print('wrote %d chars' % len(raw))
