WS = ' \n\t'
Q = '"'
BS = '\\'

def parse(buf):
    p = 0
    n = len(buf)
    count = 0
    steps = 0
    while buf[p] != '[':
        p += 1
    p += 1
    count = 0
    while p < n and count < 256:
        steps += 1
        if steps > 200000:
            print("LOOP pos", p, repr(buf[max(0, p - 80):p + 40]))
            return None
        while p < n and buf[p] in WS:
            p += 1
        if buf[p] == ']':
            break
        if buf[p] == ',':
            p += 1
            continue
        if buf[p] != '{':
            break
        p += 1
        while buf[p] != '}':
            steps += 1
            if steps > 200000:
                print("LOOP obj pos", p, repr(buf[max(0, p - 80):p + 40]))
                return None
            while buf[p] in WS:
                p += 1
            key = ''
            if buf[p] == Q:
                p += 1
            while buf[p] != Q:
                key += buf[p]
                p += 1
            p += 1
            while buf[p] == ' ':
                p += 1
            if buf[p] == ':':
                p += 1
            while buf[p] == ' ':
                p += 1
            c = buf[p]
            if c == Q:
                p += 1
                v = ''
                while buf[p] != Q:
                    if buf[p] == BS and buf[p + 1] == Q:
                        v += Q
                        p += 1
                    else:
                        v += buf[p]
                    if len(v) < 255:
                        p += 1
                p += 1
            elif c in 'tfn':
                while buf[p] != ',':
                    p += 1
            elif c == '-' or c.isdigit():
                while buf[p] not in ',}]':
                    p += 1
            elif c == '[' and key in ('tags', 'sources'):
                p += 1
                while buf[p] != ']':
                    while buf[p] == ' ':
                        p += 1
                    if buf[p] == Q:
                        p += 1
                        a = ''
                        while buf[p] != Q:
                            a += buf[p]
                            p += 1
                        p += 1
                    if buf[p] == ',':
                        p += 1
            elif c == '{' and key == 'repack':
                p += 1
                while buf[p] != '}':
                    while buf[p] == ' ':
                        p += 1
                    if buf[p] == Q:
                        p += 1
                        rk = ''
                        while buf[p] != Q:
                            rk += buf[p]
                            p += 1
                        p += 1
                        while buf[p] == ' ':
                            p += 1
                        if buf[p] == ':':
                            p += 1
                        while buf[p] == ' ':
                            p += 1
                        if buf[p] == Q:
                            p += 1
                            rv = ''
                            while buf[p] != Q:
                                if buf[p] == BS and buf[p + 1] == Q:
                                    rv += Q
                                    p += 1
                                else:
                                    rv += buf[p]
                                if len(rv) < 255:
                                    p += 1
                            p += 1
                    if buf[p] == ',':
                        p += 1
                p += 1
            else:
                while buf[p] not in ',}':
                    p += 1
            while buf[p] == ' ':
                p += 1
            if buf[p] == ',':
                p += 1
        p += 1
        count += 1
    return count


buf = open('data/games.json', encoding='utf-8').read()
print("parsed:", parse(buf))
