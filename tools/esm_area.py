"""All placed refs near a point whose base object's model path contains a substring.
Usage: python -I esm_area.py <esm> <out.json> <substring> <cx> <cy> <radius>
Handles STAT/DOOR/MSTT/ACTI/FURN bases. Output: [{"nif":"architecture/whiterun/x.nif","pos":[..],"rot":[..],"scale":s}]"""
import struct, sys, zlib, json, math

path, out, sub = sys.argv[1], sys.argv[2], sys.argv[3].lower()
cx, cy, rad = map(float, sys.argv[4:7])
WS = sys.argv[7].lower() if len(sys.argv) > 7 else None
worlds, state = {}, {"world": None}
data = open(path, "rb").read()
base_nif = {}
refs = []
BASES = (b"STAT", b"DOOR", b"MSTT", b"ACTI", b"FURN", b"TREE", b"FLOR", b"MISC", b"ALCH", b"INGR", b"BOOK", b"LIGH")


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
        if t == b"WRLD":
            for st, sd in subs(data[p + 24:p + 24 + sz] if not flags & 0x40000 else zlib.decompress(data[p + 28:p + 24 + sz])):
                if st == b"EDID": worlds[fid] = sd.split(b"\0")[0].decode().lower()
        if t in BASES or t == b"REFR":
            body = data[p + 24:p + 24 + sz]
            if flags & 0x40000: body = zlib.decompress(body[4:])
            if t == b"REFR":
                base = pos = scale = None
                for st, sd in subs(body):
                    if st == b"NAME": base, = struct.unpack("<I", sd[:4])
                    elif st == b"DATA" and len(sd) >= 24: pos = struct.unpack("<6f", sd[:24])
                    elif st == b"XSCL": scale, = struct.unpack("<f", sd[:4])
                if base is not None and pos and not flags & 0x20 and (WS is None or worlds.get(state["world"]) == WS) and math.hypot(pos[0] - cx, pos[1] - cy) <= rad:
                    refs.append((base, pos, scale or 1.0))
            else:
                for st, sd in subs(body):
                    if st == b"MODL":
                        n = sd.split(b"\0")[0].decode("cp1252").lower().replace("\\", "/")
                        if sub in n: base_nif[fid] = n
        p += 24 + sz


walk(0, len(data))
res, seen = [], set()
for base, pos, scale in refs:
    if base in base_nif:
        k = (base, tuple(round(x, 1) for x in pos))
        if k in seen: continue
        seen.add(k)
        res.append({"nif": base_nif[base], "pos": pos[:3], "rot": pos[3:], "scale": scale})
json.dump(res, open(out, "w"))
print(len(base_nif), "bases,", len(res), "refs,", len({r["nif"] for r in res}), "unique nifs")


