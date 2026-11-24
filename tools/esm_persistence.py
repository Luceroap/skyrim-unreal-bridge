"""Count placed refs in a worldspace by persistence (persistent vs temporary cell children) for models matching a filter.
Usage: python -I esm_persistence.py <esm> <worldspace edid> <model substring> [cx cy radius]"""
import collections, math, struct, sys, zlib

path, wsname, sub = sys.argv[1], sys.argv[2].lower(), sys.argv[3].lower()
cx, cy, rad = map(float, sys.argv[4:7]) if len(sys.argv) > 6 else (0.0, 0.0, 1e9)
data = open(path, "rb").read()
worlds, base_nif, refs = {}, {}, []
state = {"world": None, "grp": None}
GROUP_KIND = {8: "persistent", 9: "temporary", 10: "visible-distant"}


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
            saved = dict(state)
            if gtype == 1: state["world"], = struct.unpack_from("<I", data, p + 8)
            if gtype in GROUP_KIND: state["grp"] = GROUP_KIND[gtype]
            walk(p + 24, p + sz); state.update(saved); p += sz; continue
        flags, fid = struct.unpack_from("<II", data, p + 8)
        body = data[p + 24:p + 24 + sz]
        if t == b"WRLD":
            if flags & 0x40000: body = zlib.decompress(body[4:])
            for st, sd in subs(body):
                if st == b"EDID": worlds[fid] = sd.split(b"\0")[0].decode().lower()
        elif t == b"REFR" and worlds.get(state["world"]) == wsname:
            if flags & 0x40000: body = zlib.decompress(body[4:])
            base = pos = None
            for st, sd in subs(body):
                if st == b"NAME": base, = struct.unpack("<I", sd[:4])
                elif st == b"DATA" and len(sd) >= 24: pos = struct.unpack("<6f", sd[:24])
            if base is not None and pos and math.hypot(pos[0] - cx, pos[1] - cy) <= rad:
                refs.append((base, state["grp"], bool(flags & 0x400)))
        elif t in (b"STAT", b"MSTT", b"DOOR", b"ACTI", b"FURN", b"TREE"):
            if flags & 0x40000: body = zlib.decompress(body[4:])
            for st, sd in subs(body):
                if st == b"MODL":
                    base_nif[fid] = sd.split(b"\0")[0].decode("cp1252").lower().replace("\\", "/")
        p += 24 + sz


walk(0, len(data))
by = collections.Counter()
models = collections.defaultdict(collections.Counter)
for base, grp, persistent_flag in refs:
    n = base_nif.get(base)
    if n and sub in n:
        kind = grp or "?"
        by[kind] += 1
        models[kind][n] += 1
print("refs by group:", dict(by))
for kind, c in models.items():
    print("\n== %s (%d models)" % (kind, len(c)))
    for n, k in c.most_common(25):
        print("  %3d %s" % (k, n))
