import struct, sys

sz = int(sys.argv[1]) if len(sys.argv) > 1 else 48
img = bytearray(sz * sz * 4)
mask = bytearray((sz + 7) // 8 * sz)

for y in range(sz):
    for x in range(sz):
        i = (y * sz + x) * 4
        img[i] = int(10 + (x / sz) * 40)
        img[i+1] = int(14 + (y / sz) * 40)
        img[i+2] = int(23 + ((x + y) / (2 * sz)) * 80)
        img[i+3] = 255

cx, cy = sz // 2, sz // 2
rng = range(-3, 4)
for dy in rng:
    for dx in rng:
        ny, nx = cy + dy, cx + dx
        if 0 <= ny < sz and 0 <= nx < sz and dy*dy + dx*dx*2 < 16:
            i = (ny * sz + nx) * 4
            img[i] = 246; img[i+1] = 200; img[i+2] = 71

data_off = 6 + 16 + 40 + len(img) + len(mask)

with open('resources/tray.ico', 'wb') as f:
    f.write(struct.pack('<HH', 1, 1))
    f.write(struct.pack('<B', sz))
    f.write(struct.pack('<B', sz))
    f.write(struct.pack('<B', 0))
    f.write(struct.pack('<B', 32))
    f.write(struct.pack('<H', 32))
    f.write(struct.pack('<I', len(img)))
    f.write(struct.pack('<I', data_off))
    f.write(struct.pack('<I', 40))
    f.write(struct.pack('<I', sz))
    f.write(struct.pack('<I', sz * 2))
    f.write(struct.pack('<H', 1))
    f.write(struct.pack('<H', 32))
    f.write(struct.pack('<I', 0))
    f.write(struct.pack('<I', len(img)))
    f.write(struct.pack('<I', sz))
    f.write(struct.pack('<I', sz))
    f.write(struct.pack('<I', 0))
    f.write(struct.pack('<I', 0))
    f.write(img)
    f.write(mask)

print('Created: resources/tray.ico (%dx%d, %d bytes)' % (sz, sz, data_off + len(img) + len(mask)))
