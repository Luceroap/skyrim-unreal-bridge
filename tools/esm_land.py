"""Extract terrain (LAND heightmaps) near a point for one worldspace -> OBJ.
Usage: python -I esm_land.py <esm> <out.obj> <worldspace edid> <cx> <cy> <radius>"""
import struct, sys, zlib, math

path, out, wsname = sys.argv[1], sys.argv[2], sys.argv[3].lower()
cx, cy, rad = map(float, sys.argv[4:7])
data = open(path, "rb").read()
worlds = {}
tiles = {}  # (gx, gy) -> 33x33 heights
state = {"cell": None, "world": None}


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
            gtype, = struct.unpack_from("<I", data, p + 12)
            saved = state["world"]
            if gtype == 1:
                state["world"], = struct.unpack_from("<I", data, p + 8)
            walk(p + 24, p + sz)
            state["world"] = saved
            p += sz; continue
        flags, fid = struct.unpack_from("<II", data, p + 8)
        if t in (b"WRLD", b"CELL", b"LAND"):
            body = data[p + 24:p + 24 + sz]
            if flags & 0x40000: body = zlib.decompress(body[4:])
            if t == b"WRLD":
                for st, sd in subs(body):
                    if st == b"EDID": worlds[fid] = sd.split(b"\0")[0].decode().lower()
            elif t == b"CELL":
                state["cell"] = None
                for st, sd in subs(body):
                    if st == b"XCLC": state["cell"] = struct.unpack("<ii", sd[:8])
            elif t == b"LAND" and state["cell"] is not None and worlds.get(state["world"]) == wsname:
                gx, gy = state["cell"]
                if math.hypot((gx + .5) * 4096 - cx, (gy + .5) * 4096 - cy) <= rad:
                    cols = None
                    for st, sd in subs(body):
                        if st == b"VCLR" and len(sd) >= 3267:
                            cols = sd
                    for st, sd in subs(body):
                        if st == b"VHGT":
                            off, = struct.unpack_from("<f", sd, 0)
                            d = struct.unpack_from("<1089b", sd, 4)
                            h, rowbase = [], off
                            for y in range(33):
                                row = []
                                for x in range(33):
                                    if x == 0:
                                        rowbase += d[y * 33]; cur = rowbase
                                    else:
                                        cur += d[y * 33 + x]
                                    row.append(cur * 8.0)
                                h.append(row)
                            tiles[(gx, gy)] = (h, cols)
        p += 24 + sz


walk(0, len(data))
with open(out, "w") as f:
    f.write("o terrain\n")
    n = 1
    for (gx, gy), (h, cols) in sorted(tiles.items()):
        for y in range(33):
            for x in range(33):
                wx, wy = gx * 4096 + x * 128, gy * 4096 + y * 128
                if cols:
                    i = (y * 33 + x) * 3
                    c = (cols[i] / 255.0, cols[i + 1] / 255.0, cols[i + 2] / 255.0)
                else:
                    c = (0.5, 0.45, 0.35)
                f.write("v %.2f %.2f %.2f %.3f %.3f %.3f\n" % (wx, wy, h[y][x], *c))
        for y in range(33):
            for x in range(33):
                f.write("vt %.4f %.4f\n" % ((gx * 4096 + x * 128) / 1024.0, (gy * 4096 + y * 128) / 1024.0))
        for y in range(32):
            for x in range(32):
                a = n + y * 33 + x
                b, c, d = a + 1, a + 33, a + 34
                f.write("f %d/%d %d/%d %d/%d\nf %d/%d %d/%d %d/%d\n" % (a, a, b, b, d, d, a, a, d, d, c, c))
        n += 33 * 33
print(len(tiles), "terrain tiles", sorted(tiles)[:3])
