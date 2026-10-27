"""Create proper ICO file for windres compatibility."""
import struct, sys

def create_ico(path, size):
    img = bytearray(size * size * 4)
    mask = bytearray((size + 7) // 8 * size)
    for y in range(size):
        for x in range(size):
            i = (y * size + x) * 4
            img[i] = int(10 + (x / size) * 40)
            img[i+1] = int(14 + (y / size) * 40)
            img[i+2] = int(23 + ((x + y) / (2 * size)) * 80)
            img[i+3] = 255
    cx, cy = size // 2, size // 2
    for dy in range(min(-15, -cy), min(15, size-cy)):
        for dx in range(min(-15, -cx), min(15, size-cx)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < size and 0 <= nx < size and dy*dy + dx*dx*2 < 225:
                i = (ny * size + nx) * 4
                img[i] = 0xf6; img[i+1] = 0xc8; img[i+2] = 0x47
    data_off = 6 + 16 + 40 + len(img) + len(mask)
    with open(path, 'wb') as f:
        f.write(struct.pack('<HH', 1, 1))
        f.write(struct.pack('<BB', size if size <= 255 else 0, size if size <= 255 else 0))
        f.write(struct.pack('<BB', 0, 32))
        f.write(struct.pack('<H', 32))
        f.write(struct.pack('<II', len(img), data_off))
        f.write(struct.pack('<II', 40, size))
        f.write(struct.pack('<II', size * 2, 1))
        f.write(struct.pack('<HH', 32, 0))
        f.write(struct.pack('<II', len(img), size))
        f.write(struct.pack('<II', size, 0))
        f.write(struct.pack('<I', 0))
        f.write(img)
        f.write(mask)
    print(f'Created {path} ({size}x{size}, {data_off + len(img) + len(mask)} bytes)')

sz = int(sys.argv[1]) if len(sys.argv) > 1 else 256
create_ico('resources/tray.ico', sz)
