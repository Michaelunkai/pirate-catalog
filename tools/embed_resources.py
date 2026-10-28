#!/usr/bin/env python3
"""
Booty Catalog — Resource Embedding Tool

Converts the web assets and game data into binary blobs suitable for
embedding as C arrays in embedded.h.

Usage:
    python embed_resources.py games.bin html.bin css.bin js.bin jsdl.bin icon.bin tray.bin

Arguments:
    games.bin    → data/games.json
    html.bin     → index.html (web app)
    css.bin      → styles/app.css
    js.bin       → scripts/app.js
    jsdl.bin     → scripts/download.js
    icon.bin     → booty.ico (256x256 icon)
    tray.bin     → tray.ico (16x16 icon)

Output:
    .bin files with a header: "BCAT" + 4-byte length + raw data
    embedded.h with C arrays for direct compilation
"""

import sys
import os
import struct

MAGIC = b'BCAT'

def embed(path, out_path):
    """Read a file and write it with the BCAT header."""
    with open(path, 'rb') as f:
        data = f.read()

    # Write: MAGIC (4) + length (4, little-endian) + data
    with open(out_path, 'wb') as f:
        f.write(MAGIC)
        f.write(struct.pack('<I', len(data)))
        f.write(data)

    print(f"  Embedded: {os.path.basename(path)} → {out_path} ({len(data):,} bytes)")
    return data


def to_c_array(name, data):
    """Convert binary data to C array string."""
    lines = []
    lines.append(f"const unsigned char {name}[] = {{")
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_vals = ', '.join(f'0x{b:02x}' for b in chunk)
        lines.append(f"    {hex_vals},")
    lines.append("};")
    lines.append(f"int {name}_len = {len(data)};")
    return '\n'.join(lines)


def main():
    # Accept 5 mandatory + 2 optional args
    mandatory = ['games.bin', 'html.bin', 'css.bin', 'js.bin', 'jsdl.bin']
    optional = ['icon.bin', 'tray.bin']
    all_names = mandatory + optional

    # Check command line args
    out_paths = sys.argv[1:1+len(all_names)]
    if len(out_paths) < len(mandatory):
        print(f"Usage: python embed_resources.py games.bin html.bin css.bin js.bin jsdl.bin [icon.bin] [tray.bin]")
        sys.exit(1)

    src_paths = [
        os.path.join('data', 'games.json'),
        'index.html',
        os.path.join('styles', 'app.css'),
        os.path.join('scripts', 'app.js'),
        os.path.join('scripts', 'download.js'),
    ]

    if len(out_paths) >= 6:
        src_paths.append('resources/booty.ico')
    if len(out_paths) >= 7:
        src_paths.append('resources/tray.ico')

    # Fix stdin/stdout encoding for Windows cp1252
    _sys, _io = sys, __import__('io')
    if sys.stdout.encoding and 'cp1252' in sys.stdout.encoding.lower():
        sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
        sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', write_through=True)

    print("Booty Catalog -- Resource Embedding", flush=True)
    print("=" * 40, flush=True)

    arrays = []
    for src, out in zip(src_paths, out_paths):
        if not os.path.exists(src):
            print(f"  Warning: {src} not found, skipping...", flush=True)
            continue
        data = embed(src, out)
        # Extract variable name from output path
        name = os.path.splitext(os.path.basename(out))[0]
        if name == 'tray':
            name = 'tray_icon_resource'
        elif name == 'games':
            name = 'games_bin'
        elif name == 'html':
            name = 'html_bin'
        elif name == 'css':
            name = 'css_bin'
        elif name == 'js':
            name = 'js_bin'
        elif name == 'jsdl':
            name = 'jsdl_bin'
        elif name == 'icon':
            name = 'icon_bin'
        arrays.append(to_c_array(name, data))

    print("=" * 40)
    total = 0
    for p in out_paths:
        if os.path.exists(p):
            total += os.path.getsize(p)
    print(f"Total: {total:,} bytes embedded in EXE")

    # Write the header file for C++ to include
    header_path = os.path.join('resources', 'embedded.h')
    with open(header_path, 'w') as f:
        f.write("/* Booty Catalog -- Embedded Resources Header (regenerated) */\n")
        f.write("#ifndef EMBEDDED_H\n")
        f.write("#define EMBEDDED_H\n\n")
        f.write('\n\n'.join(arrays))
        f.write("\n\n#endif // EMBEDDED_H\n")
    print(f"Header written: {header_path}")


if __name__ == '__main__':
    main()