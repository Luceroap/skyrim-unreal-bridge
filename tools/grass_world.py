"""Grass layer: Skyrim's landscape grass (GRAS records) scattered the way the game does it, from the plugins' data, because
grass is off in the remaster profile and distant_world.py skips /grass/ and /plants/.

  LTEX (landscape texture) GNAM -> list of GRAS form ids that grow on it
  GRAS MODL + DATA -> model, density (0-100 %), min/max slope (deg), units from water + rule, position/height range, flags
  LAND VHGT (heights) + BTXT/ATXT/VTXT (base texture per quadrant + blended layers with per-vertex opacity)
  CELL XCLW (water height, only with the 'has water' flag, as distant_world --water)

Per cell (seeded by its grid coordinates, so reruns give the same grass) a jittered grid of candidate points is laid over the
heightmap; each point picks a landscape texture by its blended opacity there, then a grass type from that texture's list,
and keeps it with the grass's density as probability if slope and water rules pass.

Output (area2/grass/):
  index.json            {"tile": 1024, "spacing": .., "models": [{name, nif, source, gras, ...}], "cells": {"gx_gy": n}}
  cell_<gx>_<gy>.json   {"<tx>_<ty>": [[model idx, x, y, z, yaw deg, scale], ...]}   tiles = 1024 Skyrim units, absolute
                        Skyrim coordinates (tile index = floor(x / 1024))
Models not converted yet are queued like live_bridge does (area2/models.json + area2/requests.txt); loose files in Data win
over BSAs (the converter, build_area.py, resolves them the same way).
LTEX/GRAS come from the whole active load order (plugins.txt; grass mods edit both), LAND/water only from Skyrim.esm +
Update.esm like the terrain tools. --vanilla ignores the mods. --world <edid> (e.g. whiterunworld: the city worldspace has
its own LAND) writes to area2/grass/<edid>/ instead.
Usage: python tools/grass_world.py [--world tamriel] [--radius 14000] [--center 23000 -6000] [--spacing 48] [--seed 1]
                                   [--vanilla] [--no-queue] [--stats]"""
import glob, json, math, os, random, struct, sys, zlib
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
OUT = os.path.join(AREA, "grass")
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
PLUGINS = ["Skyrim.esm", "Update.esm"]
WORLD = "tamriel"
CENTER = (23000.0, -6000.0)            # Whiterun area, same as the terrain/distant tools
RADIUS = 14000.0                       # ~37 cells: the detailed terrain (area2/terrain_obj) around Whiterun
SPACING = 48.0                         # candidate grid (Skyrim's iMinGrassSize is 20; grass mods use 50-75)
TILE = 1024.0
MAX_PER_CELL = 12000


def arg(name, default, n=1, cast=float):
    if name not in sys.argv:
        return default
    i = sys.argv.index(name)
    v = [cast(x) for x in sys.argv[i + 1:i + 1 + n]]
    return v[0] if n == 1 else tuple(v)


def subs(buf):
    p, ext = 0, None
    while p + 6 <= len(buf):
        t = buf[p:p + 4]; sz, = struct.unpack_from("<H", buf, p + 4); p += 6
        if t == b"XXXX":
            ext, = struct.unpack_from("<I", buf, p); p += 4; continue
        if ext is not None: sz, ext = ext, None
        yield t, buf[p:p + sz]; p += sz


def land_heights(sd):
    off, = struct.unpack_from("<f", sd, 0); d = struct.unpack_from("<1089b", sd, 4)
    h, rowbase = [], off
    for y in range(33):
        row = []
        for x in range(33):
            if x == 0: rowbase += d[y * 33]; c = rowbase
            else: c += d[y * 33 + x]
            row.append(c * 8.0)
        h.append(row)
    return h


def load_order():
    """Skyrim.esm, Update.esm, the DLCs, Creation Club (Skyrim.ccc), then the active plugins of plugins.txt, in order."""
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


def plugin_bytes(path, full):
    """The whole file, or (full=False) only its TES4 header plus the top-level LTEX/GRAS groups (cheap for big mods)."""
    if full:
        return open(path, "rb").read()
    parts = []
    with open(path, "rb") as f:
        hdr = f.read(24)
        if len(hdr) < 24 or hdr[:4] != b"TES4":
            return b""
        parts.append(hdr + f.read(struct.unpack_from("<I", hdr, 4)[0]))
        while True:
            h = f.read(24)
            if len(h) < 24:
                break
            sz, = struct.unpack_from("<I", h, 4)
            if h[:4] == b"GRUP" and h[8:12] in (b"LTEX", b"GRAS"):
                parts.append(h + f.read(sz - 24))
            else:
                f.seek(sz - 24 if h[:4] == b"GRUP" else sz, 1)
    return b"".join(parts)


def read_plugin(path, db, center, radius, full=True):
    """Records of one plugin into db. Form ids become (defining plugin, low 24 bits) through the plugin's master list, so
    overrides from mods (grass mods edit LTEX grass lists and GRAS models/densities) replace the vanilla records."""
    data = plugin_bytes(path, full)
    if not data:
        return
    own = os.path.basename(path).lower()
    masters = []
    tsz, = struct.unpack_from("<I", data, 4)
    tbody = data[24:24 + tsz]
    if struct.unpack_from("<I", data, 8)[0] & 0x40000: tbody = zlib.decompress(tbody[4:])
    for st, sd in subs(tbody):
        if st == b"MAST": masters.append(sd.split(b"\0")[0].decode("cp1252").lower())

    def G(fid):
        i = fid >> 24
        return (masters[i] if i < len(masters) else own, fid & 0xFFFFFF)

    cur = [None]

    def in_range(c):
        return math.hypot((c[0] + .5) * 4096 - center[0], (c[1] + .5) * 4096 - center[1]) <= radius + 2900

    def walk(s, e, world):
        p = s
        while p < e:
            t = data[p:p + 4]; sz, = struct.unpack_from("<I", data, p + 4)
            if t == b"GRUP":
                label, gtype = struct.unpack_from("<II", data, p + 8)
                walk(p + 24, p + sz, G(label) if gtype == 1 else world)
                p += sz; continue
            flags, fid = struct.unpack_from("<II", data, p + 8)
            if t in (b"WRLD", b"CELL", b"LAND", b"LTEX", b"GRAS"):
                if t in (b"CELL", b"LAND") and db["worlds"].get(world) != WORLD:
                    p += 24 + sz; continue
                if t == b"LAND" and (cur[0] is None or not in_range(cur[0])):
                    p += 24 + sz; continue
                body = data[p + 24:p + 24 + sz]
                if flags & 0x40000: body = zlib.decompress(body[4:])
                if t == b"WRLD":
                    for st, sd in subs(body):
                        if st == b"EDID": db["worlds"][G(fid)] = sd.split(b"\0")[0].decode().lower()
                elif t == b"LTEX":
                    g, edid = [], ""
                    for st, sd in subs(body):
                        if st == b"EDID": edid = sd.split(b"\0")[0].decode("cp1252")
                        elif st == b"GNAM": g += [G(struct.unpack_from("<I", sd, i)[0]) for i in range(0, len(sd) - 3, 4)]
                    db["ltex"][G(fid)] = {"edid": edid, "grass": g}
                elif t == b"GRAS":
                    r = {"edid": "", "model": None}
                    for st, sd in subs(body):
                        if st == b"EDID": r["edid"] = sd.split(b"\0")[0].decode("cp1252")
                        elif st == b"MODL": r["model"] = sd.split(b"\0")[0].decode("cp1252").lower().replace("\\", "/")
                        elif st == b"DATA" and len(sd) >= 32:
                            (r["density"], r["min_slope"], r["max_slope"], _u, r["water_units"], _u2, r["water_rule"],
                             r["pos_range"], r["height_range"], r["color_range"], r["wave"], r["flags"]) = \
                                struct.unpack_from("<4BHHIffffB", sd, 0)
                    if r["model"] and "density" in r:
                        db["gras"][G(fid)] = r
                elif t == b"CELL":
                    xclc = xclw = None; has_water = False
                    for st, sd in subs(body):
                        if st == b"DATA": has_water = bool(sd[0] & 0x02)
                        elif st == b"XCLC": xclc = struct.unpack("<ii", sd[:8])
                        elif st == b"XCLW": xclw, = struct.unpack("<f", sd[:4])
                    cur[0] = xclc
                    if xclc:
                        if has_water and xclw is not None and abs(xclw) < 1e7: db["water"][xclc] = xclw
                        else: db["water"].pop(xclc, None)
                elif t == b"LAND":
                    h, base, layers, lay = None, {}, [], None
                    for st, sd in subs(body):
                        if st == b"VHGT": h = land_heights(sd)
                        elif st == b"BTXT": base[sd[4]] = G(struct.unpack_from("<I", sd, 0)[0])
                        elif st == b"ATXT":
                            f, q, _u, li = struct.unpack("<IBBh", sd[:8])
                            lay = {"ltex": G(f), "q": q, "layer": li, "op": [[0.0] * 17 for _ in range(17)]}; layers.append(lay)
                        elif st == b"VTXT" and lay is not None:
                            for i in range(len(sd) // 8):
                                pos, _u, op = struct.unpack_from("<HHf", sd, i * 8)
                                if pos < 289: lay["op"][pos // 17][pos % 17] = op
                    if h:
                        layers.sort(key=lambda l: (l["q"], l["layer"]))
                        db["land"][cur[0]] = (h, base, [[l for l in layers if l["q"] == q] for q in range(4)])
            p += 24 + sz

    walk(24 + tsz, len(data), None)


def bilinear(g, u, v):
    """g[row=v][col=u], u, v fractional grid coordinates."""
    n = len(g) - 1
    i, j = min(int(u), n - 1), min(int(v), n - 1)
    fu, fv = u - i, v - j
    return (g[j][i] * (1 - fu) + g[j][i + 1] * fu) * (1 - fv) + (g[j + 1][i] * (1 - fu) + g[j + 1][i + 1] * fu) * fv


def height(h, fx, fy):
    """Terrain height on the same triangles as the terrain meshes (esm_land_tex: diagonal from (x, y) to (x+1, y+1))."""
    i, j = min(int(fx), 31), min(int(fy), 31)
    u, v = fx - i, fy - j
    a, b, c, d = h[j][i], h[j][i + 1], h[j + 1][i], h[j + 1][i + 1]
    return a + u * (b - a) + v * (d - b) if u >= v else a + v * (c - a) + u * (d - c)


def tex_weights(base, layers, fx, fy):
    """Blended landscape textures at cell vertex coordinates (fx, fy) in 0..32 -> [(ltex form id or 0, weight)]."""
    qx, qy = (1 if fx >= 16 else 0), (1 if fy >= 16 else 0)
    q = qx + 2 * qy
    u, v = fx - 16 * qx, fy - 16 * qy
    w = [(base.get(q), 1.0)]
    for l in layers[q]:
        a = max(0.0, min(1.0, bilinear(l["op"], u, v)))
        if a <= 0.0:
            continue
        w = [(t, x * (1 - a)) for t, x in w] + [(l["ltex"], a)]
    return w


def water_ok(g, z, wh):
    """GRAS 'units from water' rule. wh = cell water height or None (no water in the cell)."""
    units, rule = g["water_units"], g["water_rule"]
    if wh is None:
        return rule in (0, 4) or (units == 0 and rule not in (2, 3, 7))
    d = z - wh
    if rule == 0: return d >= units                       # above, at least
    if rule == 1: return 0 <= d <= units                  # above, at most
    if rule == 2: return d <= -units                      # below, at least
    if rule == 3: return -units <= d <= 0                 # below, at most
    if rule == 4: return abs(d) >= units                  # either, at least
    if rule == 5: return abs(d) <= units                  # either, at most
    if rule == 6: return d >= 0 and d <= units            # either, at most above
    if rule == 7: return d <= 0 and -d <= units           # either, at most below
    return d >= 0


def scatter_cell(gx, gy, land, water, db, model_idx, spacing, seed, stats):
    h, base, layers = land
    wh = water.get((gx, gy))
    rng = random.Random((gx * 73856093) ^ (gy * 19349663) ^ (seed * 83492791))
    out = {}
    n = int(4096 / spacing)
    count = 0
    for iy in range(n):
        for ix in range(n):
            if count >= MAX_PER_CELL:
                stats["capped"] += 1; return out, count
            lx = (ix + rng.random()) * spacing; ly = (iy + rng.random()) * spacing
            fx, fy = lx / 128.0, ly / 128.0
            w = tex_weights(base, layers, fx, fy)
            r = rng.random() * sum(x for _, x in w)
            lt = w[-1][0]
            for t, x in w:
                r -= x
                if r <= 0: lt = t; break
            grasses = [gid for gid in db["ltex"].get(lt, {}).get("grass", ()) if gid in model_idx]
            if not grasses:
                stats["bare"] += 1; continue
            gid = grasses[int(rng.random() * len(grasses)) % len(grasses)]
            g = db["gras"][gid]
            if rng.random() * 100.0 >= g["density"]:
                continue
            pr = g["pos_range"]
            if pr > 0:
                lx = 4095.9 - abs(4095.9 - abs(lx + (rng.random() * 2 - 1) * pr))   # reflect at the cell edges
                ly = 4095.9 - abs(4095.9 - abs(ly + (rng.random() * 2 - 1) * pr))
                fx, fy = lx / 128.0, ly / 128.0
            z = height(h, fx, fy)
            dzx = (bilinear(h, min(32.0, fx + .25), fy) - bilinear(h, max(0.0, fx - .25), fy)) / (min(32.0, fx + .25) - max(0.0, fx - .25)) / 128.0
            dzy = (bilinear(h, fx, min(32.0, fy + .25)) - bilinear(h, fx, max(0.0, fy - .25))) / (min(32.0, fy + .25) - max(0.0, fy - .25)) / 128.0
            slope = math.degrees(math.atan(math.hypot(dzx, dzy)))
            mx = g["max_slope"] or 90
            if slope < g["min_slope"] or slope > mx:
                stats["slope"] += 1; continue
            if not water_ok(g, z, wh):
                stats["water"] += 1; continue
            hr = g["height_range"]
            s = max(0.3, 1.0 + (rng.random() * 2 - 1) * hr) if hr > 0 else 1.0
            x, y = gx * 4096 + lx, gy * 4096 + ly
            key = "%d_%d" % (math.floor(x / TILE), math.floor(y / TILE))
            out.setdefault(key, []).append([model_idx[gid], round(x, 1), round(y, 1), round(z, 1),
                                            round(rng.random() * 360.0, 1), round(s, 3)])
            stats["models"][gid] += 1
            count += 1
    return out, count


def mesh_sources(nifs):
    """nif -> 'loose' / 'bsa:<archive>' / None, mod BSAs before vanilla (build_area.open_archives order)."""
    from bsa import Bsa
    res = {}
    for n in nifs:
        if os.path.exists(os.path.join(DATA, "meshes", n.replace("/", "\\"))):
            res[n] = "loose"
    rest = [n for n in nifs if n not in res]
    if rest:
        mods, vanilla = [], []
        for p in sorted(glob.glob(os.path.join(DATA, "*.bsa"))):
            b = os.path.basename(p).lower()
            if b.startswith("skyrim - ") and "meshes" not in b:
                continue
            (vanilla if b.startswith("skyrim - ") else mods).append(p)
        for p in mods + vanilla:
            if not rest:
                break
            try:
                a = Bsa(p)
            except Exception:
                continue
            for n in list(rest):
                if "meshes\\" + n.replace("/", "\\") in a.files:
                    res[n] = "bsa:" + os.path.basename(p); rest.remove(n)
    return res


def queue(models):
    """Append unconverted models to area2/requests.txt with their nif paths merged into area2/models.json (the same files
    live_bridge.request writes; asset_service.py converts them)."""
    done = set()
    for n in ("ready.txt", "failed.txt", "requests.txt"):
        p = os.path.join(AREA, n)
        if os.path.exists(p):
            done |= set(open(p).read().split())
    new = [m for m in models if m["source"] and m.get("count") and m["name"] not in done and
           not os.path.exists(os.path.join(AREA, "export", m["name"] + ".fbx"))]
    new = list({m["name"]: m for m in new}.values())
    if not new:
        return 0
    mp = os.path.join(AREA, "models.json")
    mapping = json.load(open(mp)) if os.path.exists(mp) else {}
    mapping.update({m["name"]: m["nif"] for m in new})
    with open(mp, "w") as f:
        json.dump(mapping, f)
    with open(os.path.join(AREA, "requests.txt"), "a") as f:
        f.write("".join(m["name"] + "\n" for m in new))
    return len(new)


def main():
    global WORLD, OUT
    WORLD = arg("--world", WORLD, cast=str).lower()
    if WORLD != "tamriel":
        OUT = os.path.join(OUT, WORLD)
    center = arg("--center", CENTER, 2)
    radius = arg("--radius", RADIUS)
    spacing = arg("--spacing", SPACING)
    seed = arg("--seed", 1, cast=int)
    db = {"worlds": {}, "ltex": {}, "gras": {}, "land": {}, "water": {}}
    for p in PLUGINS:
        path = os.path.join(DATA, p)
        if os.path.exists(path):
            read_plugin(path, db, center, radius)
            print("read %s: %d LTEX, %d GRAS, %d LAND" % (p, len(db["ltex"]), len(db["gras"]), len(db["land"])))
    if "--vanilla" not in sys.argv:                  # LTEX/GRAS overrides of the active load order (grass mods)
        before = {k: (v["model"], v["density"]) for k, v in db["gras"].items()}
        lt_before = {k: tuple(v["grass"]) for k, v in db["ltex"].items()}
        touched = Counter()
        for p in load_order():
            if p in PLUGINS:
                continue
            snap_g = {k: id(v) for k, v in db["gras"].items()}; snap_l = {k: id(v) for k, v in db["ltex"].items()}
            read_plugin(os.path.join(DATA, p), db, center, radius, full=False)
            n = sum(1 for k, v in db["gras"].items() if snap_g.get(k) != id(v)) + \
                sum(1 for k, v in db["ltex"].items() if snap_l.get(k) != id(v))
            if n: touched[p] = n
        print("load order: LTEX/GRAS records from", dict(touched))
        print("  GRAS changed vs vanilla: %d, LTEX grass lists changed: %d" % (
            sum(1 for k, v in db["gras"].items() if before.get(k) != (v["model"], v["density"])),
            sum(1 for k, v in db["ltex"].items() if lt_before.get(k) != tuple(v["grass"]))))
    cells = sorted(c for c in db["land"] if math.hypot((c[0] + .5) * 4096 - center[0], (c[1] + .5) * 4096 - center[1]) <= radius)
    used = set()
    for c in cells:
        _h, base, layers = db["land"][c]
        for t in list(base.values()) + [l["ltex"] for q in layers for l in q]:
            used |= set(db["ltex"].get(t, {}).get("grass", ()))
    used = sorted(g for g in used if g in db["gras"] and " " not in db["gras"][g]["model"])
    src = mesh_sources(sorted({db["gras"][g]["model"] for g in used}))
    models, model_idx = [], {}
    for g in used:
        r = db["gras"][g]
        if not src.get(r["model"]):
            print("missing mesh for GRAS %s: %s" % (r["edid"], r["model"])); continue
        model_idx[g] = len(models)
        models.append({"name": r["model"][:-4].replace("/", "_"), "nif": r["model"], "source": src[r["model"]],
                       "gras": "%s:%06X" % g, "edid": r["edid"], "density": r["density"], "slope": [r["min_slope"], r["max_slope"]],
                       "water": [r["water_units"], r["water_rule"]], "pos_range": r["pos_range"],
                       "height_range": r["height_range"], "flags": r["flags"]})
    os.makedirs(OUT, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, "cell_*.json")):
        os.remove(old)
    stats = {"bare": 0, "slope": 0, "water": 0, "capped": 0, "models": Counter()}
    counts = {}
    for gx, gy in cells:
        tiles, n = scatter_cell(gx, gy, db["land"][(gx, gy)], db["water"], db, model_idx, spacing, seed, stats)
        counts["%d_%d" % (gx, gy)] = n
        if n:
            with open(os.path.join(OUT, "cell_%d_%d.json" % (gx, gy)), "w") as f:
                json.dump(tiles, f, separators=(",", ":"))
    for g, i in model_idx.items():
        models[i]["count"] = stats["models"][g]
    json.dump({"tile": TILE, "spacing": spacing, "seed": seed, "center": center, "radius": radius, "world": WORLD,
               "models": models, "cells": counts}, open(os.path.join(OUT, "index.json"), "w"), indent=1)
    total = sum(counts.values())
    print("%d cells, %d grass instances (%.0f per cell), %d models; rejected: bare %d, slope %d, water %d; capped cells %d"
          % (len(cells), total, total / max(1, len(cells)), len(models), stats["bare"], stats["slope"], stats["water"],
             stats["capped"]))
    if "--stats" in sys.argv:
        for m in sorted(models, key=lambda m: -m["count"]):
            print("%7d  %-40s %-50s d%3d slope%s %s" % (m["count"], m["edid"], m["nif"], m["density"], m["slope"], m["source"]))
    if "--no-queue" not in sys.argv:
        print("queued %d models for conversion" % queue(models))


if __name__ == "__main__":
    main()
