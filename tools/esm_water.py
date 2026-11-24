"""Water heights per exterior cell (CELL XCLW) near a point -> water.csv (gx,gy,height). Child worldspaces fall back to the parent.
Usage: python -I esm_water.py <esm> <out.csv> <worldspaces comma list> <cx> <cy> <radius>"""
import struct, sys, zlib, math

esm, out, wsl = sys.argv[1:4]
wslist = [w.strip() for w in wsl.lower().split(",")]
cx, cy, rad = map(float, sys.argv[4:7])
data = open(esm, "rb").read()
worlds, state, cells, prio = {}, {"world": None}, {}, {}


def subs(buf):
    p, ext = 0, None
    while p + 6 <= len(buf):
        t = buf[p:p + 4]; sz, = struct.unpack_from("<H", buf, p + 4); p += 6
        if t == b"XXXX":
            ext, = struct.unpack_from("<I", buf, p); p += 4; continue
        if ext is not None: sz, ext = ext, None
        yield t, buf[p:p + sz]; p += sz


def walk(s, e):
    p = s
    while p < e:
        t = data[p:p + 4]; sz, = struct.unpack_from("<I", data, p + 4)
        if t == b"GRUP":
            gtype, = struct.unpack_from("<I", data, p + 12); saved = state["world"]
            if gtype == 1: state["world"], = struct.unpack_from("<I", data, p + 8)
            walk(p + 24, p + sz); state["world"] = saved; p += sz; continue
        flags, fid = struct.unpack_from("<II", data, p + 8)
        if t in (b"WRLD", b"CELL"):
            body = data[p + 24:p + 24 + sz]
            if flags & 0x40000: body = zlib.decompress(body[4:])
            if t == b"WRLD":
                for st, sd in subs(body):
                    if st == b"EDID": worlds[fid] = sd.split(b"\0")[0].decode().lower()
            elif worlds.get(state["world"]) in wslist:
                xclc = xclw = None
                for st, sd in subs(body):
                    if st == b"XCLC": xclc = struct.unpack("<ii", sd[:8])
                    elif st == b"XCLW": xclw, = struct.unpack("<f", sd[:4])
                if xclc and xclw is not None and xclw > -1e7 and abs(xclw) < 1e7:
                    gx, gy = xclc
                    if math.hypot((gx + .5) * 4096 - cx, (gy + .5) * 4096 - cy) <= rad:
                        pr = wslist.index(worlds[state["world"]])
                        if (gx, gy) not in cells or pr < prio[(gx, gy)]:
                            cells[(gx, gy)] = xclw; prio[(gx, gy)] = pr
        p += 24 + sz


walk(0, len(data))
open(out, "w").write("\n".join("%d,%d,%.1f" % (gx, gy, h) for (gx, gy), h in sorted(cells.items())) + "\n")
print(len(cells), "cells with water:", sorted(cells.items())[:8])
