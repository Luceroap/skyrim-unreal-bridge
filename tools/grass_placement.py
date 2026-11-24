"""Grass placement for the Unreal remaster (Skyrim's own grass is off in the remaster profile).

Skyrim chain: LAND (BTXT base + ATXT/VTXT blended layers per cell quadrant) -> LTEX GNAM (grass list) -> GRAS (model, density,
slope range, water rule, position/height/colour range, wave period, flags) -> grass NIF.

Placement follows the game: every grass type of every landscape texture is scattered on its own jittered grid of iMinGrassSize
(the grass mod's ini, Skoglendi: 35 units). A grid point keeps an instance with probability density% x (sum of the blended
weights of the textures that list this grass there), then the slope rule (face normal of the terrain triangle under it, same
diagonal as the terrain meshes), the water rule and the position jitter apply. Height range -> random scale (all axes with
'uniform scaling', else height only), 'fit to slope' -> instance tilted to the terrain normal, colour range -> shade.
Deterministic: every (cell, GRAS) pair has its own seeded generator.

LAND / CELL come from Skyrim.esm + Update.esm (same heights as the terrain tools); LTEX / GRAS from the whole active load
order (plugins.txt), so grass mods' lists, models and densities are used.

Output: area2/grass_place/<world>/
  models.json            [{name, nif, gras, edid, density, slope, water, pos_range, height_range, color_range, wave,
                           flags, count, bytes, file, tex, height}] + settings, per-cell counts
  <name>.bin             'SKGR' v1: header <4sIIIf (magic, version, count, ntiles, tile=4096); tile table ntiles x <hhII
                         (cell gx, gy, first, count); then count records of 22 bytes, sorted by cell:
                         <3f x,y,z (Skyrim units, z on the terrain)  H yaw (0..65535 = 0..360 deg)  e sxy  e sz
                         b nx  b ny (terrain normal x127 when fit-to-slope, else 0,0)  B shade (255 = full brightness)
                         B keep (uniform random: draw only keep < 255*f to thin far grass to fraction f)
Models (--models): grass NIFs -> area2/grass_place/obj (tools/nif2obj.py) + alpha textures area2/grass_place/tex/<key>.png
  -> FBX area2/grass_place/fbx/<name>.fbx via Blender (tools/grass_blender.py).
Preview (--preview): Blender render of a grassy patch -> area2/grass_place/preview_<world>.png

Usage: python tools/grass_placement.py [--world tamriel|whiterunworld|all] [--center 23000 -6000] [--radius 14000]
                                       [--spacing 35] [--seed 1] [--vanilla] [--models] [--preview [x y]] [--stats]"""
import glob, io, json, math, os, struct, subprocess, sys, zlib
import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
from distant_world import subs                       # read-only reuse of the subrecord iterator

ROOT = os.path.dirname(TOOLS)
AREA = os.path.join(ROOT, "area2")
OUT = os.path.join(AREA, "grass_place")
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
BLENDER = r"D:\blender.exe"
MASTERS = ["Skyrim.esm", "Update.esm"]
CENTER = (23000.0, -6000.0)                          # Whiterun, same as the terrain/distant tools
RADIUS = 14000.0                                     # the detailed terrain area (~37 cells)
MAX_TYPES_PER_TEXTURE = 10                           # iMaxGrassTypesPerTexure (Skoglendi ini)
CELL = 4096.0
DT = np.dtype([("x", "<f4"), ("y", "<f4"), ("z", "<f4"), ("yaw", "<u2"), ("sxy", "<f2"), ("sz", "<f2"),
               ("nx", "i1"), ("ny", "i1"), ("shade", "u1"), ("keep", "u1")])
F_VERTEX_LIGHTING, F_UNIFORM_SCALE, F_FIT_SLOPE = 1, 2, 4


def arg(name, default, n=1, cast=float):
    if name not in sys.argv:
        return default
    i = sys.argv.index(name)
    v = [cast(x) for x in sys.argv[i + 1:i + 1 + n]]
    return v[0] if n == 1 else tuple(v)


def min_grass_size():
    """iMinGrassSize from the grass mods' ini files in Data (Skyrim's default is 20)."""
    best = None
    for p in glob.glob(os.path.join(DATA, "*.ini")):
        for line in open(p, errors="replace"):
            k, _, v = line.partition("=")
            if k.strip().lower() == "imingrasssize":
                try: best = float(v)
                except ValueError: pass
    return best or 20.0


def load_order():
    names = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
    ccc = os.path.join(os.path.dirname(DATA), "Skyrim.ccc")
    if os.path.exists(ccc):
        names += [l.strip() for l in open(ccc) if l.strip()]
    pt = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Skyrim Special Edition", "plugins.txt")
    if os.path.exists(pt):
        names += [l.strip()[1:] for l in open(pt, encoding="utf-8", errors="replace") if l.startswith("*")]
    seen, out = set(), []
    for n in names:
        if n.lower() not in seen and os.path.exists(os.path.join(DATA, n)):
            seen.add(n.lower()); out.append(n)
    return out


# ------------------------------------------------------------------------------------------------------------- records
class Db:
    def __init__(self):
        self.worlds = {}          # key -> (edid, default water height)
        self.ltex = {}            # key -> {"edid", "grass": [keys]}
        self.gras = {}            # key -> dict
        self.land = {}            # (world edid, gx, gy) -> (heights 33x33 float64, base {q: ltex}, layers [q] -> [(ltex, op 17x17)])
        self.water = {}           # (world edid, gx, gy) -> water height


def _body(data, p, sz, flags):
    b = data[p + 24:p + 24 + sz]
    return zlib.decompress(b[4:]) if flags & 0x40000 else b


def land_heights(sd):
    off, = struct.unpack_from("<f", sd, 0)
    d = np.frombuffer(sd, np.int8, 1089, 4).reshape(33, 33).astype(np.float64)
    d[:, 0] = np.cumsum(d[:, 0])                     # first column accumulates down the rows, each row along x
    return (np.cumsum(d, axis=1) + off) * 8.0


def read_plugin(path, db, worlds, center, radius, full):
    """full: also walk WRLD/CELL/LAND (masters); otherwise only the top-level LTEX/GRAS groups (mods)."""
    with open(path, "rb") as f:
        data = f.read()
    own = os.path.basename(path).lower()
    tsz, = struct.unpack_from("<I", data, 4)
    tbody = _body(data, 0, tsz, struct.unpack_from("<I", data, 8)[0])
    masters = [sd.split(b"\0")[0].decode("cp1252").lower() for st, sd in subs(tbody) if st == b"MAST"]

    def G(fid):
        i = fid >> 24
        return (masters[i] if i < len(masters) else own, fid & 0xFFFFFF)

    def near(c):
        return math.hypot((c[0] + .5) * CELL - center[0], (c[1] + .5) * CELL - center[1]) <= radius + 2900

    cur = {"world": None, "cell": None}

    def record(t, p, sz, flags, fid):
        if t == b"LTEX":
            g, edid = [], ""
            for st, sd in subs(_body(data, p, sz, flags)):
                if st == b"EDID": edid = sd.split(b"\0")[0].decode("cp1252")
                elif st == b"GNAM": g += [G(struct.unpack_from("<I", sd, i)[0]) for i in range(0, len(sd) - 3, 4)]
            db.ltex[G(fid)] = {"edid": edid, "grass": g}
        elif t == b"GRAS":
            r = {"edid": "", "model": None}
            for st, sd in subs(_body(data, p, sz, flags)):
                if st == b"EDID": r["edid"] = sd.split(b"\0")[0].decode("cp1252")
                elif st == b"MODL": r["model"] = sd.split(b"\0")[0].decode("cp1252").lower().replace("\\", "/")
                elif st == b"DATA" and len(sd) >= 32:
                    (r["density"], r["min_slope"], r["max_slope"], _u, r["water_units"], _u2, r["water_rule"],
                     r["pos_range"], r["height_range"], r["color_range"], r["wave"], r["flags"]) = \
                        struct.unpack_from("<4BHHIffffB", sd, 0)
            if r["model"] and "density" in r:
                db.gras[G(fid)] = r
        elif t == b"WRLD":
            edid, water = "", None
            for st, sd in subs(_body(data, p, sz, flags)):
                if st == b"EDID": edid = sd.split(b"\0")[0].decode("cp1252").lower()
                elif st == b"DNAM" and len(sd) >= 8: water = struct.unpack_from("<ff", sd, 0)[1]
            old = db.worlds.get(G(fid), ("", None))
            db.worlds[G(fid)] = (edid or old[0], water if water is not None else old[1])
        elif t == b"CELL":
            xclc = xclw = None; has_water = False
            for st, sd in subs(_body(data, p, sz, flags)):
                if st == b"DATA": has_water = bool(sd[0] & 0x02)
                elif st == b"XCLC": xclc = struct.unpack("<ii", sd[:8])
                elif st == b"XCLW": xclw, = struct.unpack("<f", sd[:4])
            w = cur["world"]
            cur["cell"] = xclc
            if xclc and w:
                k = (w,) + tuple(xclc)
                default = next((v[1] for v in db.worlds.values() if v[0] == w), None)
                if has_water:
                    h = xclw if xclw is not None and abs(xclw) < 1e7 else default
                    if h is not None: db.water[k] = h
                else:
                    db.water.pop(k, None)
        elif t == b"LAND":
            c, w = cur["cell"], cur["world"]
            if c is None or w is None or (w == "tamriel" and not near(c)):
                return
            h, base, layers, lay = None, {}, [[], [], [], []], None
            for st, sd in subs(_body(data, p, sz, flags)):
                if st == b"VHGT": h = land_heights(sd)
                elif st == b"BTXT": base[sd[4]] = G(struct.unpack_from("<I", sd, 0)[0])
                elif st == b"ATXT":
                    f_, q, _u, li = struct.unpack("<IBBh", sd[:8])
                    lay = [li, G(f_), np.zeros((17, 17))]
                    if q < 4: layers[q].append(lay)
                elif st == b"VTXT" and lay is not None:
                    for i in range(len(sd) // 8):
                        pos, _u, op = struct.unpack_from("<HHf", sd, i * 8)
                        if pos < 289: lay[2][pos // 17, pos % 17] = op
            if h is not None:
                db.land[(w,) + tuple(c)] = (h, base, [[(l[1], l[2]) for l in sorted(q)] for q in layers])

    def walk(s, e, depth):
        p = s
        while p < e:
            t = data[p:p + 4]; sz, = struct.unpack_from("<I", data, p + 4)
            if t == b"GRUP":
                label = data[p + 8:p + 12]; gtype, = struct.unpack_from("<I", data, p + 12)
                if depth == 0 and (label not in (b"LTEX", b"GRAS") and not (full and label == b"WRLD")):
                    p += sz; continue
                if gtype == 1:                                           # world children
                    wk = G(struct.unpack("<I", label)[0])
                    edid = db.worlds.get(wk, ("",))[0]
                    if edid not in worlds:
                        p += sz; continue
                    saved = cur["world"]; cur["world"] = edid
                    walk(p + 24, p + sz, depth + 1)
                    cur["world"] = saved
                else:
                    walk(p + 24, p + sz, depth + 1)
                p += sz; continue
            flags, fid = struct.unpack_from("<II", data, p + 8)
            if not flags & 0x20:                                         # deleted records ignored
                record(t, p, sz, flags, fid)
            p += 24 + sz

    walk(24 + tsz, len(data), 0)


# ------------------------------------------------------------------------------------------------------------- scatter
def bilinear(g, u, v):
    """g[row=v, col=u], u/v arrays of fractional grid coordinates."""
    n = g.shape[0] - 1
    i = np.clip(u.astype(np.int64), 0, n - 1); j = np.clip(v.astype(np.int64), 0, n - 1)
    fu, fv = u - i, v - j
    return (g[j, i] * (1 - fu) + g[j, i + 1] * fu) * (1 - fv) + (g[j + 1, i] * (1 - fu) + g[j + 1, i + 1] * fu) * fv


def tex_weights(base, layers, fx, fy):
    """{ltex: weight array} at cell vertex coordinates fx, fy (0..32): per quadrant the base texture, then every ATXT
    layer alpha-composited over it in layer order (same blending as land_terrain.py)."""
    q = (fx >= 16).astype(np.int64) + 2 * (fy >= 16).astype(np.int64)
    out = {}
    for qi in range(4):
        m = q == qi
        if not m.any():
            continue
        u = fx[m] - 16 * (qi & 1); v = fy[m] - 16 * (qi >> 1)
        ws = [(base.get(qi), np.ones(m.sum()))]
        for lt, op in layers[qi]:
            a = np.clip(bilinear(op, u, v), 0.0, 1.0)
            ws = [(t, w * (1 - a)) for t, w in ws] + [(lt, a)]
        for t, w in ws:
            if t is None:
                continue
            full = out.get(t)
            if full is None:
                full = out[t] = np.zeros(len(fx))
            full[m] += w
    return out


def surface(h, fx, fy):
    """Height and face normal on the terrain triangles (diagonal (x, y)-(x+1, y+1), as terrain.obj / land_terrain)."""
    i = np.clip(fx.astype(np.int64), 0, 31); j = np.clip(fy.astype(np.int64), 0, 31)
    u, v = fx - i, fy - j
    a, b, c, d = h[j, i], h[j, i + 1], h[j + 1, i], h[j + 1, i + 1]
    up = u >= v
    z = np.where(up, a + u * (b - a) + v * (d - b), a + v * (c - a) + u * (d - c))
    dzdx = np.where(up, b - a, d - c) / 128.0
    dzdy = np.where(up, d - b, c - a) / 128.0
    n = np.stack([-dzdx, -dzdy, np.ones_like(z)], 1)
    return z, n / np.linalg.norm(n, axis=1, keepdims=True)


def water_ok(g, z, wh):
    units, rule = g["water_units"], g["water_rule"]
    if wh is None:                                       # dry cell: 'above water' rules pass, 'below' rules fail
        return np.full(len(z), rule in (0, 4) or (units == 0 and rule not in (2, 3, 7)))
    d = z - wh
    return {0: d >= units, 1: (d >= 0) & (d <= units), 2: d <= -units, 3: (d >= -units) & (d <= 0),
            4: np.abs(d) >= units, 5: np.abs(d) <= units, 6: (d >= 0) & (d <= units),
            7: (d <= 0) & (-d <= units)}.get(rule, d >= 0)


def grass_lists(db):
    """ltex -> GRAS keys that exist (first iMaxGrassTypesPerTexure entries, like the game)."""
    return {k: [g for g in v["grass"][:MAX_TYPES_PER_TEXTURE] if g in db.gras] for k, v in db.ltex.items()}


def scatter_cell(key, land, wh, db, lists, spacing, seed, stats):
    """-> {gras key: structured array of instances (DT)} for one cell."""
    h, base, layers = land
    gx, gy = key[1], key[2]
    present = set(base.values()) | {lt for q in layers for lt, _ in q}
    types = sorted({g for t in present for g in lists.get(t, ())})
    n = int(CELL // spacing)
    ix, iy = np.meshgrid(np.arange(n), np.arange(n))
    ix, iy = ix.ravel().astype(np.float64), iy.ravel().astype(np.float64)
    out = {}
    for gk in types:
        g = db.gras[gk]
        rng = np.random.default_rng([seed, gx & 0xFFFF, gy & 0xFFFF, zlib.crc32(("%s:%06X" % gk).encode())])
        lx = (ix + rng.random(len(ix))) * spacing
        ly = (iy + rng.random(len(iy))) * spacing
        pr = g["pos_range"]
        if pr > 0:                                                    # jitter, reflected at the cell edges
            lx = 4095.9 - np.abs(4095.9 - np.abs(lx + (rng.random(len(lx)) * 2 - 1) * pr))
            ly = 4095.9 - np.abs(4095.9 - np.abs(ly + (rng.random(len(ly)) * 2 - 1) * pr))
        fx, fy = lx / 128.0, ly / 128.0
        tw = tex_weights(base, layers, fx, fy)
        w = np.zeros(len(fx))
        for t, a in tw.items():
            if gk in lists.get(t, ()):
                w += a
        keep = rng.random(len(fx)) < (g["density"] / 100.0) * w
        stats["candidates"] += int((w > 0).sum())
        lx, ly, fx, fy = lx[keep], ly[keep], fx[keep], fy[keep]
        if not len(lx):
            continue
        z, nrm = surface(h, fx, fy)
        slope = np.degrees(np.arccos(np.clip(nrm[:, 2], -1, 1)))
        ok = (slope >= g["min_slope"]) & (slope <= (g["max_slope"] or 90))
        stats["slope"] += int((~ok).sum())
        wok = water_ok(g, z, wh)
        stats["water"] += int((ok & ~wok).sum())
        ok &= wok
        m = int(ok.sum())
        if not m:
            continue
        hr = g["height_range"]
        s = np.maximum(0.25, 1.0 + (rng.random(m) * 2 - 1) * hr) if hr > 0 else np.ones(m)
        a = np.zeros(m, DT)
        a["x"] = gx * CELL + lx[ok]; a["y"] = gy * CELL + ly[ok]; a["z"] = z[ok]
        a["yaw"] = (rng.random(m) * 65536).astype(np.uint32).clip(0, 65535)
        a["sz"] = s
        a["sxy"] = s if g["flags"] & F_UNIFORM_SCALE else 1.0
        if g["flags"] & F_FIT_SLOPE:
            a["nx"] = np.round(nrm[ok, 0] * 127); a["ny"] = np.round(nrm[ok, 1] * 127)
        a["shade"] = np.round(255 * (1.0 - rng.random(m) * min(1.0, g["color_range"])))
        a["keep"] = (rng.random(m) * 256).astype(np.uint32).clip(0, 255)
        out[gk] = a
    return out


def asset_name(nif):
    return nif[:-4].replace("/", "_")


def write_bin(path, parts):
    """parts: [((gx, gy), array)] -> SKGR file (instances sorted by cell)."""
    parts = sorted((c, a) for c, a in parts if len(a))
    table, first = [], 0
    for (gx, gy), a in parts:
        table.append(struct.pack("<hhII", gx, gy, first, len(a))); first += len(a)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sIIIf", b"SKGR", 1, first, len(table), CELL))
        f.write(b"".join(table))
        for _c, a in parts:
            f.write(a.tobytes())
    return os.path.getsize(path)


def read_bin(path):
    """-> {(gx, gy): structured array}. Reference reader for the format (grass_layer.py has a numpy-free one)."""
    raw = open(path, "rb").read()
    magic, ver, count, nt, _tile = struct.unpack_from("<4sIIIf", raw, 0)
    assert magic == b"SKGR" and ver == 1
    off = 20 + nt * 12
    allr = np.frombuffer(raw, DT, count, off)
    res = {}
    for i in range(nt):
        gx, gy, first, n = struct.unpack_from("<hhII", raw, 20 + i * 12)
        res[(gx, gy)] = allr[first:first + n]
    return res


def place(world, db, center, radius, spacing, seed):
    out = os.path.join(OUT, world)
    os.makedirs(out, exist_ok=True)
    lists = grass_lists(db)
    keys = sorted(k for k in db.land if k[0] == world and (world != "tamriel" or
                  math.hypot((k[1] + .5) * CELL - center[0], (k[2] + .5) * CELL - center[1]) <= radius))
    stats = {"candidates": 0, "slope": 0, "water": 0}
    per_model, per_cell = {}, {}
    for k in keys:
        res = scatter_cell(k, db.land[k], db.water.get(k), db, lists, spacing, seed, stats)
        per_cell["%d_%d" % (k[1], k[2])] = int(sum(len(a) for a in res.values()))
        for gk, a in res.items():
            per_model.setdefault(asset_name(db.gras[gk]["model"]), []).append(((k[1], k[2]), a, gk))
    for old in glob.glob(os.path.join(out, "*.bin")):
        os.remove(old)
    models = []
    for name, parts in sorted(per_model.items()):
        merged = {}
        for c, a, _gk in parts:
            merged[c] = np.concatenate([merged[c], a]) if c in merged else a
        size = write_bin(os.path.join(out, name + ".bin"), list(merged.items()))
        gks = sorted({gk for _c, _a, gk in parts})
        g = db.gras[gks[0]]
        models.append({"name": name, "nif": g["model"], "gras": ["%s:%06X" % k for k in gks],
                       "edid": [db.gras[k]["edid"] for k in gks], "density": g["density"],
                       "slope": [g["min_slope"], g["max_slope"]], "water": [g["water_units"], g["water_rule"]],
                       "pos_range": round(g["pos_range"], 2), "height_range": round(g["height_range"], 3),
                       "color_range": round(g["color_range"], 3), "wave": round(g["wave"], 2), "flags": g["flags"],
                       "count": int(sum(len(a) for a in merged.values())), "bytes": size, "file": name + ".bin"})
    total = sum(m["count"] for m in models)
    info = {"world": world, "center": center, "radius": radius, "spacing": spacing, "seed": seed, "cell": CELL,
            "record": DT.itemsize, "total": total, "models": models, "cells": per_cell}
    mj = os.path.join(out, "models.json")
    if os.path.exists(mj):                                    # keep model metadata (--models) of a previous run
        old = {m["name"]: m for m in json.load(open(mj)).get("models", [])}
        for m in models:
            for k in ("tex", "height", "alpha_ref", "fbx"):
                if k in old.get(m["name"], {}):
                    m[k] = old[m["name"]][k]
    json.dump(info, open(mj, "w"), indent=1)
    print("[%s] %d cells, %d instances (%.0f per cell), %d models, %.1f MB on disk; candidates %d, rejected slope %d, water %d"
          % (world, len(keys), total, total / max(1, len(keys)), len(models),
             sum(m["bytes"] for m in models) / 1e6, stats["candidates"], stats["slope"], stats["water"]))
    return info


# ------------------------------------------------------------------------------------------------------------- models
def archives():
    from bsa import Bsa
    mods, vanilla = [], []
    for p in sorted(glob.glob(os.path.join(DATA, "*.bsa"))):
        b = os.path.basename(p).lower()
        if b.startswith("skyrim - ") and "meshes" not in b and "textures" not in b:
            continue
        try:
            (vanilla if b.startswith("skyrim - ") else mods).append(Bsa(p))
        except Exception:
            pass
    return mods + vanilla                                     # mod archives override vanilla (build_area.py order)


def data_file(rel, arcs):
    rel = rel.lower().replace("/", "\\")
    loose = os.path.join(DATA, rel)
    if os.path.exists(loose):
        return open(loose, "rb").read()
    for a in arcs:
        if rel in a.files:
            return a.read(rel)
    return None


def dds_to_png(raw, png):
    from PIL import Image
    if raw[84:88] == b"DX10":                                 # Pillow lacks the *_SRGB DXGI formats (textures.py does the same)
        fmt = struct.unpack_from("<I", raw, 128)[0]
        if fmt in (72, 75, 78, 99):
            raw = raw[:128] + struct.pack("<I", fmt - 1) + raw[132:]
    im = Image.open(io.BytesIO(raw)); im.load()
    im = im.convert("RGBA")
    im.save(png)
    return im


def alpha_threshold(path):
    """NiAlphaProperty test threshold (0-255) of the first alpha property in the nif, or None."""
    import nif2obj
    try:
        data, blocks, _strings, _v = nif2obj.parse(open(path, "rb").read())
    except Exception:
        return None
    for typ, pos, _size in blocks:
        if typ == "NiAlphaProperty":
            r = nif2obj.R(data, pos)
            r.i32(); n = r.u32(); r.p += 4 * n; r.i32()       # NiObjectNET
            flags = r.u16(); thr = r.u8()
            return thr if flags & 0x200 else None             # alpha test enabled
    return None


def convert_models(world):
    import nif2obj
    out = os.path.join(OUT, world)
    mj = os.path.join(out, "models.json")
    info = json.load(open(mj))
    od, td, fd = (os.path.join(OUT, d) for d in ("obj", "tex", "fbx"))
    for d in (od, td, fd, os.path.join(OUT, "nif")):
        os.makedirs(d, exist_ok=True)
    arcs = archives()
    for m in info["models"]:
        name = m["name"]
        nifp = os.path.join(OUT, "nif", name + ".nif")
        if not os.path.exists(nifp):
            raw = data_file("meshes/" + m["nif"], arcs)
            if raw is None:
                print("MISSING mesh", m["nif"]); continue
            open(nifp, "wb").write(raw)
        shapes = nif2obj.extract(nifp)
        if not shapes:
            print("no geometry", name); continue
        texs = []
        for _n, verts, _uv, _t, tex in shapes:
            if tex:
                tex = tex.lower()
                i = tex.find("textures\\")
                tex = tex[i:] if i > 0 else tex
                if not tex.startswith("textures\\"): tex = "textures\\" + tex
                key = os.path.basename(tex)[:-4]
                png = os.path.join(td, key + ".png")
                if not os.path.exists(png):
                    raw = data_file(tex, arcs)
                    if raw is None:
                        print("MISSING texture", tex)
                    else:
                        dds_to_png(raw, png)
                        nraw = data_file(tex[:-4] + "_n.dds", arcs)
                        if nraw is not None:
                            dds_to_png(nraw, os.path.join(td, key + "_n.png"))
                texs.append(key)
        obj = os.path.join(od, name + ".obj")
        nif2obj.write_obj(shapes, obj)
        mtl = obj[:-4] + ".mtl"                                # point map_Kd at our own PNGs
        lines = []
        for line in open(mtl):
            lines.append(line.rstrip("\n"))
            if line.startswith("# skyrim diffuse:"):
                key = os.path.basename(line.split(":", 1)[1].strip().lower())[:-4]
                png = os.path.join(td, key + ".png")
                if os.path.exists(png):
                    lines.append("map_Kd " + png.replace("\\", "/"))
        open(mtl, "w").write("\n".join(lines) + "\n")
        zs = [v[2] for s in shapes for v in s[1]]
        m["tex"] = sorted(set(texs)); m["height"] = round(max(zs) - min(zs), 1) if zs else 0
        m["alpha_ref"] = alpha_threshold(nifp)
        m["fbx"] = name + ".fbx"
        print("model %-45s %d shapes, %d verts, h=%.0f, tex %s, alpha_ref %s" % (
            name, len(shapes), sum(len(s[1]) for s in shapes), m["height"], m["tex"], m["alpha_ref"]))
    json.dump(info, open(mj, "w"), indent=1)
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(TOOLS, "grass_blender.py"), "--",
                        "export", od, fd], capture_output=True, text=True)
    print("\n".join(l for l in r.stdout.splitlines() if l.startswith(("EXPORTED", "ERROR", "Traceback"))) or r.stderr[-2000:])


def preview(world, db, spot, radius=1400.0):
    """Blender render of the grass around spot (Skyrim units): terrain of the cells around it + instances."""
    out = os.path.join(OUT, world)
    pdir = os.path.join(OUT, "preview")
    os.makedirs(pdir, exist_ok=True)
    gx, gy = int(math.floor(spot[0] / CELL)), int(math.floor(spot[1] / CELL))
    verts, faces = [], []
    for cx in range(gx - 1, gx + 2):
        for cy in range(gy - 1, gy + 2):
            land = db.land.get((world, cx, cy))
            if not land:
                continue
            h = land[0]; base = len(verts)
            for y in range(33):
                for x in range(33):
                    verts.append((cx * CELL + x * 128 - spot[0], cy * CELL + y * 128 - spot[1], float(h[y, x])))
            for y in range(32):
                for x in range(32):
                    a = base + y * 33 + x
                    faces += [(a, a + 1, a + 34), (a, a + 34, a + 33)]
    np.savez(os.path.join(pdir, "terrain.npz"), v=np.array(verts, np.float32), f=np.array(faces, np.int32))
    info = json.load(open(os.path.join(out, "models.json")))
    inst = {}
    for m in info["models"]:
        cells = read_bin(os.path.join(out, m["file"]))
        rows = [a for (cx, cy), a in cells.items() if abs(cx - gx) <= 1 and abs(cy - gy) <= 1]
        if not rows:
            continue
        a = np.concatenate(rows)
        a = a[np.hypot(a["x"] - spot[0], a["y"] - spot[1]) <= radius]
        if len(a):
            inst[m["name"]] = np.stack([a["x"] - spot[0], a["y"] - spot[1], a["z"], a["yaw"] / 65536.0 * 360.0,
                                        a["sxy"].astype(np.float32), a["sz"].astype(np.float32),
                                        a["nx"] / 127.0, a["ny"] / 127.0, a["shade"] / 255.0], 1).astype(np.float32)
    np.savez(os.path.join(pdir, "instances.npz"), **inst)
    n = sum(len(v) for v in inst.values())
    png = os.path.join(OUT, "preview_%s.png" % world)
    print("preview: %d instances of %d models within %.0f units of (%.0f, %.0f)" % (n, len(inst), radius, *spot))
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(TOOLS, "grass_blender.py"), "--",
                        "preview", pdir, os.path.join(OUT, "obj"), png], capture_output=True, text=True)
    print("\n".join(l for l in r.stdout.splitlines() if l.startswith(("PREVIEW", "ERROR", "Traceback", "  "))) or r.stderr[-3000:])
    return png


def best_spot(world, info, center):
    """Densest cell near the centre -> its densest 1024-unit tile centre (a grassy patch for the preview)."""
    out = os.path.join(OUT, world)
    best = None
    for k, n in info["cells"].items():
        gx, gy = map(int, k.split("_"))
        d = math.hypot((gx + .5) * CELL - center[0], (gy + .5) * CELL - center[1])
        score = n / (1 + d / 8000.0)
        if best is None or score > best[0]:
            best = (score, gx, gy)
    _s, gx, gy = best
    grid = np.zeros((4, 4))
    for m in info["models"]:
        a = read_bin(os.path.join(out, m["file"])).get((gx, gy))
        if a is not None and len(a):
            tx = np.clip(((a["x"] - gx * CELL) // 1024).astype(int), 0, 3)
            ty = np.clip(((a["y"] - gy * CELL) // 1024).astype(int), 0, 3)
            np.add.at(grid, (ty, tx), 1)
    ty, tx = np.unravel_index(np.argmax(grid), grid.shape)
    return (gx * CELL + (tx + .5) * 1024, gy * CELL + (ty + .5) * 1024)


def main():
    center = arg("--center", CENTER, 2)
    radius = arg("--radius", RADIUS)
    spacing = arg("--spacing", min_grass_size())
    seed = arg("--seed", 1, cast=int)
    w = arg("--world", "all", cast=str).lower()
    worlds = ["tamriel", "whiterunworld"] if w == "all" else [w]
    db = Db()
    for p in MASTERS:
        read_plugin(os.path.join(DATA, p), db, set(worlds), center, radius, True)
        print("read %s: %d LTEX, %d GRAS, %d LAND" % (p, len(db.ltex), len(db.gras), len(db.land)))
    if "--vanilla" not in sys.argv:
        vanilla = {k: (v["model"], v["density"]) for k, v in db.gras.items()}
        lt0 = {k: tuple(v["grass"]) for k, v in db.ltex.items()}
        for p in load_order():
            if p not in MASTERS:
                read_plugin(os.path.join(DATA, p), db, set(worlds), center, radius, False)
        print("load order: %d GRAS changed by mods, %d LTEX grass lists changed" % (
            sum(1 for k, v in db.gras.items() if vanilla.get(k) != (v["model"], v["density"])),
            sum(1 for k, v in db.ltex.items() if lt0.get(k) != tuple(v["grass"]))))
    print("grid spacing %.0f units (iMinGrassSize), %d grass types per texture max" % (spacing, MAX_TYPES_PER_TEXTURE))
    infos = {wd: place(wd, db, center, radius, spacing, seed) for wd in worlds}
    if "--stats" in sys.argv:
        for wd, info in infos.items():
            for m in sorted(info["models"], key=lambda m: -m["count"]):
                print("  %-9s %8d  %-42s d%3d slope %s flags %d  %.2f MB" % (wd, m["count"], m["name"], m["density"],
                                                                            m["slope"], m["flags"], m["bytes"] / 1e6))
    if "--models" in sys.argv:
        for wd in worlds:
            convert_models(wd)
    if "--preview" in sys.argv:
        i = sys.argv.index("--preview")
        try:
            spot = (float(sys.argv[i + 1]), float(sys.argv[i + 2]))
        except (IndexError, ValueError):
            spot = best_spot(worlds[0], infos[worlds[0]], center)
        preview(worlds[0], db, spot)


if __name__ == "__main__":
    main()
