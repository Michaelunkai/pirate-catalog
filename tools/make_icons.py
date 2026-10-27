#!/usr/bin/env python3
"""Create proper ICO files with valid headers for Windows RC compiler."""
import struct
import os

def make_icon(path, sizes):
    """Write a multi-size ICO file. sizes = list of (width, height) tuples."""
    images = []
    for w, h in sizes:
        rgba = bytearray(w * h * 4)
        for y in range(h):
            for x in range(w):
                i = (y * w + x) * 4
                r = int(10 + (x / w) * 40)
                g = int(14 + (y / h) * 40)
                b = int(23 + ((x + y) / (2 * max(w, h))) * 80)
                rgba[i]   = r
                rgba[i+1] = g
                rgba[i+2] = b
                rgba[i+3] = 255

        # Gold anchor in center
        cx, cy = w // 2, h // 2
        radius = min(w, h) // 6
        for dy in range(-radius, radius):
            for dx in range(-radius, radius):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and dy*dy + dx*dx < radius*radius:
                    i = (ny * w + nx) * 4
                    rgba[i]   = 0xf6
                    rgba[i+1] = 0xc8
                    rgba[i+2] = 0x47
                    rgba[i+3] = 255

        mask = bytearray((w + 7) // 8 * h)
        images.append((w, h, rgba, mask))

    with open(path, 'wb') as f:
        # ICO header
        f.write(struct.pack('<HH', 1, len(images)))  # type=1, count=N

        dir_offset = 6 + 16 * len(images)
        for img in images:
            w, h, rgba, mask = img
            data = rgba + mask
            # Write directory entry
            fw = w if w < 256 else 0
            fh = h if h < 256 else 0
            f.write(struct.pack('<BB', fw, fh))
            f.write(struct.pack('<B', 0))     # palette
            f.write(struct.pack('<B', 0))     # reserved
            f.write(struct.pack('<H', 1))     # color planes
            f.write(struct.pack('<H', 32))    # bpp
            f.write(struct.pack('<I', len(data)))   # raw data size
            f.write(struct.pack('<I', dir_offset))  # offset

        # Write image data blocks
        for img in images:
            w, h, rgba, mask = img
            f.write(rgba)
            f.write(mask)

    print(f'Created: {path} ({len(images)} sizes, {os.path.getsize(path):,} bytes)')

os.makedirs('resources', exist_ok=True)
make_icon('resources/booty.ico', [(256, 256), (128, 128), (48, 48), (32, 32), (16, 16)])
make_icon('resources/tray.ico', [(48, 48), (32, 32), (16, 16)])
print('Done!')
