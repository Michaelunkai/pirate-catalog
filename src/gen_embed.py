#!/usr/bin/env python3
"""Generate src/embedded.h with byte-level C array literals."""
import os

def byte_array(name, path):
    with open(path, 'rb') as f:
        data = f.read()
    lines = []
    lines.append('/* %s - %d bytes */' % (name, len(data))
    lines.append('/* static const unsigned char %s[] = { */' % name)
    for i in range(0, len(data), 16):
        chunk = data[i:i+16)
        hexes = ', '.join('0x%02X' % b for b in chunk)
        lines.append('    %s,' % hexes)
    lines.append('};')
    lines.append('static int %s_len = %d;' % (name, len(data)))
    lines.append('')
    return '\n'.join(lines)

bin_files = [
    ('games_bin', 'games.bin'),
    ('html_bin', 'html.bin'),
    ('css_bin', 'css.bin'),
    ('js_bin', 'js.bin'),
    ('jsdl_bin', 'jsdl.bin'),
    ('icon_bin', 'icon.bin'),
    ('tray_bin', 'tray.bin'),
)

with open('src/embedded.h', 'w') as out:
    out.write('/* Booty Catalog -- Embedded Resources Header */