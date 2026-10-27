#!/bin/bash
# Generate embedded.h from .bin blobs using byte-level hex literals
# Avoids Python corruption targets

BIN_DIR="F:/study/projects/pirate-catalog"
OUT="$BIN_DIR/src/embedded.h"

cat > "$OUT" <<'HEADER'
/* Booty Catalog -- Embedded Resources Header */
/* Byte-level C array literals for EXE embedding */

#ifndef EMBEDDED_H
#define EMBEDDED_H

HEADER

for pair in games_bin:games.bin html_bin:html.bin css_bin:app.css js_bin:app.js jsdl_bin:download.js icon_bin:icon.bin tray_bin:tray.bin; do
    name="${pair%%:*}"
    file="${pair##*:}"
    path="$BIN_DIR/$file"
    if [ -f "$path" ]; then
        len=$(wc -c < "$path")
        echo "extern const unsigned char ${name}[];" >> "$OUT"
        echo "extern int ${name}_len;" >> "$OUT"
        echo "" >> "$OUT"
        echo "/* ${name} - ${len} bytes */" >> "$OUT"
        echo "static const unsigned char ${name}[] = {" >> "$OUT"
        # Convert binary to hex bytes
        od -An -tx1 -v "$path" | tr -d '\n ' | fold -w 16 | while read line; do
            result=""
            for ((i=0; i<${#line}; i+=2)); do
                byte="${line:$i:2}"
                result="${result}0x${byte}, "
            done
            result="${result% ,}"
            echo "    ${result}" >> "$OUT"
        done
        echo "};" >> "$OUT"
        echo "static int ${name}_len = ${len};" >> "$OUT"
        echo "" >> "$OUT"
    fi
done

cat >> "$OUT" <<'FOOTER'
#endif /* EMBEDDED_H */
FOOTER

echo "embedded.h generated with byte-level hex literals"
