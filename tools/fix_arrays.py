#!/usr/bin/env python3 -X utf8
"""Fix remaining [; -> ] array corruption in all C++ source files"""
import os, re

def fix(path):
    with open(path, 'rb') as f:
        content = f.read().decode('latin-1')
    orig = content
    src = os.path.basename(path)

    # Fix array brackets: identifier[256; -> identifier[256]
    content = re.sub(r'(\[\d+)\s*;\s*([,\)\}\]])', r'\1\2', content)
    content = re.sub(r'(char\s+\w+)\[(\d+)\s*;', r'\1[\2]', content)
    content = re.sub(r'(\w+)\[(\w+)\s*;', r'\1[\2]', content)
    content = re.sub(r'(\w+)\[(\w+)\]\[(\d+)\s*;', r'\1[\2][\3]', content)

    # Fix parse_games_json internal arrays
    for name in ['key', 'val', 'numval', 'arrval', 'rk', 'rv']:
        content = re.sub(r'({}\[[\d]+)\s*;'.format(name), r'\1]', content)

    # Fix array bracket assignments: arrval[ai++ = -> arrval[ai++] =
    fixes = [
        ('arrval[ai++ =', 'arrval[ai++] ='),
        ('key[ki++ =', 'key[ki++] ='),
        ('rk[ri++ =', 'rk[ri++] ='),
        ('val[vi++ =', 'val[vi++] ='),
        ('rv[vvi++ =', 'rv[vvi++] ='),
        ('numval[ni++ =', 'numval[ni++] ='),
        ('out[oi++ =', 'out[oi++] ='),
    ]
    for old, new in fixes:
        content = content.replace(old, new)

    if content != orig:
        print(f"  {src}: changed")
    else:
        print(f"  {src}: no change needed")
    with open(path, 'wb') as f:
        f.write(content.encode('latin-1'))

for root, dirs, files in os.walk(r'F:\study\projects\pirate-catalog\src'):
    for fn in files:
        if fn.endswith('.cpp'):
            fix(os.path.join(root, fn))
    for fn in files:
        if fn.endswith('.h') or fn.endswith('.hpp'):
            fix(os.path.join(root, fn))

print("Done.")
