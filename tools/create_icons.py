"""
Create proper ICO files for Windows RC compiler.
Windres requires proper ICO headers with BITMAPINFOHEADER.
"""
import struct

def create_icon(path, size=256):
    # Create 256x256 RGBA pixel data
    img = bytearray(size * size * 4)
    mask = bytearray((size + 7) // 8 * size)
    for y in range(size):
        for x in range(size):
            i = (y * size + x) * 4
            r = int(10 + (x / size) * 40)
            g = int(14 + (y / size) * 40)
            b = int(23 + ((x + y) / (2 * size)) * 80)
            img[i] = r
            img[i+1] = g
            img[i+2] = b
            img[i+3] = 255

    # Gold anchor (circle) in center
    cx, cy = size // 2, size // 2
    for dy in range(-15, 15):
        for dx in range(-15, 15):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < size and 0 <= nx < size and dy*dy + dx*dx*2 < 225:
                i = (ny * size + nx) * 4
                img[i] = 0xf6
                img[i+1] = 0xc8
                img[i+2] = 0x47

    with open(path, 'wb') as f:
        # ICO header: type(2), count(2)
        f.write(struct.pack('<H', 1))
        f.write(struct.pack('<H', 1))
        # Image directory entry (16 bytes)
        # width(1), height(1), colors(1), reserved(1),
        # color_planes(2), bpp(2), raw_data_size(4), offset(4)
        f.write(struct.pack('<BB', size if size <= 255 else 0, size if size <= 255 else 0))
        f.write(struct.pack('<B', 0))    # palette
        f.write(struct.pack('<B', 32))    # reserved (alpha channel)
        f.write(struct.pack('<H', 32))    # color planes
        offset = 6 + 16 + 40 + len(img) + len(mask)
        f.write(struct.pack('<I', len(img)))
        f.write(struct.pack('<I', offset))
        # BITMAPINFOHEADER (40 bytes)
        f.write(struct.pack('<I', 40))     # header size
        f.write(struct.pack('<I', size))   # width
        f.write(struct.pack('<I', size * 2))  # height (doubled for mask)
        f.write(struct.pack('<H', 1))      # planes
        f.write(struct.pack('<H', 32))     # bpp
        f.write(struct.pack('<I', 0))      # compression (BI_RGB)
        f.write(struct.pack('<I', len(img)))  # image size
        f.write(struct.pack('<I', size))   # h resolution
        f.write(struct.pack('<I', size))   # v resolution
        f.write(struct.pack('<I', 0))      # colors
        f.write(struct.pack('<I', 0))      # important colors
        # Image data
        f.write(img)
        # Mask data
        f.write(mask)

    print(f'Created: {path} ({size}x{size})')

create_icon('resources/booty.ico', 256)
create_icon('resources/tray.ico', 48)
print('Done!')
