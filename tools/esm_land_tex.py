"""Terrain with real ground textures: reads LAND heightmaps + texture layers (BTXT/ATXT/VTXT) for one worldspace from the ESM,
bakes one albedo PNG per terrain tile (cell) and writes an OBJ with one object/material per tile (UVs 0..1 per tile).
Usage: python -I esm_land_tex.py <Data dir> <esm> <area dir> <worldspace edid> <cx> <cy> <radius> [bake_px=4096]"""
import struct, sys, zlib, math, os, io, glob
sys.path.insert(0, os.path.dirname(__file__))
from bsa import Bsa
from PIL import Image

data_dir, esm, area, wsname = sys.argv[1:5]
wslist = [w.strip() for w in wsname.lower().split(",")]   # first = highest priority (child worldspaces borrow terrain from their parent)
prio = {}
cx, cy, rad = map(float, sys.argv[5:8])
S = int(sys.argv[8]) if len(sys.argv) > 8 else 4096
TILE_UNITS = 512.0   # one repeat of a landscape texture
data = open(esm, "rb").read()
worlds, ltex, txst, tiles = {}, {}, {}, {}
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
            gtype, = struct.unpack_from("<I", data, p + 12); saved = state["world"]
            if gtype == 1: state["world"], = struct.unpack_from("<I", data, p + 8)
            walk(p + 24, p + sz); state["world"] = saved; p += sz; continue
        flags, fid = struct.unpack_from("<II", data, p + 8)
        if t in (b"WRLD", b"CELL", b"LAND", b"LTEX", b"TXST"):
            body = data[p + 24:p + 24 + sz]
            if flags & 0x40000: body = zlib.decompress(body[4:])
            if t == b"WRLD":
                for st, sd in subs(body):
                    if st == b"EDID": worlds[fid] = sd.split(b"\0")[0].decode().lower()
            elif t == b"LTEX":
                for st, sd in subs(body):
                    if st == b"TNAM": ltex[fid] = struct.unpack("<I", sd[:4])[0]
            elif t == b"TXST":
                for st, sd in subs(body):
                    if st == b"TX00": txst[fid] = sd.split(b"\0")[0].decode("cp1252").lower()
            elif t == b"CELL":
                state["cell"] = None
                for st, sd in subs(body):
                    if st == b"XCLC": state["cell"] = struct.unpack("<ii", sd[:8])
            elif t == b"LAND" and state["cell"] is not None and worlds.get(state["world"]) in wslist:
                gx, gy = state["cell"]
                if math.hypot((gx + .5) * 4096 - cx, (gy + .5) * 4096 - cy) <= rad:
                    h, base, layers, cur = None, {}, [], None
                    for st, sd in subs(body):
                        if st == b"VHGT":
                            off, = struct.unpack_from("<f", sd, 0); d = struct.unpack_from("<1089b", sd, 4)
                            h, rowbase = [], off
                            for y in range(33):
                                row = []
                                for x in range(33):
                                    if x == 0: rowbase += d[y * 33]; c = rowbase
                                    else: c += d[y * 33 + x]
                                    row.append(c * 8.0)
                                h.append(row)
                        elif st == b"BTXT":
                            f, q = struct.unpack("<IB", sd[:5]); base[q] = f
                        elif st == b"ATXT":
                            f, q, _u, lay = struct.unpack("<IBBh", sd[:8])
                            cur = {"ltex": f, "q": q, "layer": lay, "op": [[0.0] * 17 for _ in range(17)]}; layers.append(cur)
                        elif st == b"VTXT" and cur is not None:
                            for i in range(len(sd) // 8):
                                pos, _u, op = struct.unpack_from("<HHf", sd, i * 8)
                                if pos < 289: cur["op"][pos // 17][pos % 17] = op
                    pr = wslist.index(worlds.get(state["world"]))
                    if h and ((gx, gy) not in tiles or pr < prio[(gx, gy)]):
                        tiles[(gx, gy)] = (h, base, sorted(layers, key=lambda l: (l["q"], l["layer"]))); prio[(gx, gy)] = pr
        p += 24 + sz


walk(0, len(data))
print(len(tiles), "tiles; ltex", len(ltex), "txst", len(txst))
archives = [Bsa(p) for p in sorted(glob.glob(os.path.join(data_dir, "Skyrim - Textures*.bsa")))]
cache = {}


def tex_image(ltex_fid):
    if ltex_fid in cache: return cache[ltex_fid]
    path = txst.get(ltex.get(ltex_fid, 0))
    img = None
    if path:
        key = "textures\\" + path.replace("/", "\\")
        raw = None
        loose = os.path.join(data_dir, key)
        if os.path.exists(loose): raw = open(loose, "rb").read()
        else:
            for a in archives:
                if key in a.files: raw = a.read(key); break
        if raw:
            try:
                if raw[84:88] == b"DX10":
                    f = struct.unpack_from("<I", raw, 128)[0]
                    if f in (72, 75, 78, 99): raw = raw[:128] + struct.pack("<I", f - 1) + raw[132:]
                img = Image.open(io.BytesIO(raw)).convert("RGB")
            except Exception as e:
                print("tex fail", path, e)
    cache[ltex_fid] = img
    if img is None: print("NO TEXTURE for ltex %08x -> txst %08x -> %r" % (ltex_fid, ltex.get(ltex_fid, 0), path))
    return img


def default_tex():
    key = "textures\\landscape\\dirt02.dds"
    if "default" in cache: return cache["default"]
    img = None
    loose = os.path.join(data_dir, key)
    raw = open(loose, "rb").read() if os.path.exists(loose) else next((a.read(key) for a in archives if key in a.files), None)
    if raw:
        try: img = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception as e: print("default tex fail", e)
    cache["default"] = img
    return img


def tiled(img, size_px):
    """img tiled so one repeat = TILE_UNITS world units (1 px = 1 unit at S=4096 per 4096-unit tile)."""
    rep = max(8, int(TILE_UNITS * S / 4096))
    t = img.resize((rep, rep), Image.BILINEAR)
    out = Image.new("RGB", (size_px, size_px))
    for y in range(0, size_px, rep):
        for x in range(0, size_px, rep):
            out.paste(t, (x, y))
    return out


os.makedirs(os.path.join(area, "tex"), exist_ok=True)
os.makedirs(os.path.join(area, "terrain_obj"), exist_ok=True)
obj = open(os.path.join(area, "terrain_obj", "terrain.obj"), "w"); mtl = open(os.path.join(area, "terrain_obj", "terrain.mtl"), "w")
obj.write("mtllib terrain.mtl\n")
nbase = 1
Q = S // 2
for (gx, gy), (h, base, layers) in sorted(tiles.items()):
    canvas = Image.new("RGB", (S, S), (90, 80, 60))
    for q in range(4):
        ox, oy = (q % 2) * Q, (1 - q // 2) * Q            # q0 SW (bottom-left) ... q3 NE; image y grows downward
        b = tex_image(base[q]) if q in base else default_tex()      # quadrants without a base layer use the game's default dirt
        quad = tiled(b, Q) if b else Image.new("RGB", (Q, Q), (90, 80, 60))
        for l in [l for l in layers if l["q"] == q]:
            li = tex_image(l["ltex"])
            if not li: continue
            m = Image.new("L", (17, 17))
            m.putdata([int(max(0.0, min(1.0, l["op"][16 - r][c])) * 255) for r in range(17) for c in range(17)])   # row 0 = south -> bottom
            m = m.resize((Q, Q), Image.BILINEAR)
            quad = Image.composite(tiled(li, Q), quad, m)
        canvas.paste(quad, (ox, oy))
    name = "terrain_tile_%d_%d" % (gx, gy)
    canvas.save(os.path.join(area, "tex", name + ".png"))
    mtl.write("newmtl %s\nKd 0.8 0.8 0.8\nmap_Kd %s\n" % (name, os.path.join(area, "tex", name + ".png").replace("\\", "/")))
    obj.write("o %s\nusemtl %s\n" % (name, name))
    for y in range(33):
        for x in range(33):
            obj.write("v %.2f %.2f %.2f\n" % (gx * 4096 + x * 128, gy * 4096 + y * 128, h[y][x]))
    for y in range(33):
        for x in range(33):
            obj.write("vt %.5f %.5f\n" % (x / 32.0, y / 32.0))
    for y in range(32):
        for x in range(32):
            a = nbase + y * 33 + x; b2, c, d = a + 1, a + 33, a + 34
            obj.write("f %d/%d %d/%d %d/%d\nf %d/%d %d/%d %d/%d\n" % (a, a, b2, b2, d, d, a, a, d, d, c, c))
    nbase += 33 * 33
    print("baked", name)
obj.close(); mtl.close()



