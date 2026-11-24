"""Distant world layer: every mountain, cliff, big rock and tree that Skyrim places around the play area, read from the
plugins' REFR records (Skyrim.esm + Update.esm overrides), so Unreal can show the real full-detail models far beyond the
loaded cells (Skyrim itself only shows low-detail object LOD out there).

Output: area2/distant_refs.json  [{id, model, nif, pos, rot(3x3 row-major), scale, kind}]
  model = asset name (same convention as the live stream), nif = path under meshes/ for the asset service.
live_bridge places these like the large-reference preview and drops each one as soon as the live stream delivers the same
form id (the loaded cells), so nothing is drawn twice.
Usage: python tools/distant_world.py [--stats]
       python tools/distant_world.py --interiors <edid prefix> | --world <ws edid> | --water
       python tools/distant_world.py --dungeons   (every other interior cell of the official masters, see dump_dungeons)"""
import json, math, os, struct, sys, zlib
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
PLUGINS = ["Skyrim.esm", "Update.esm"]               # later files override earlier ones (same form id)
WORLD = "tamriel"
CENTER = (23000.0, -6000.0)                          # Whiterun area, Skyrim units (same as the terrain tools)

# model path prefix -> (kind, radius in Skyrim units). Mountains are what you see on the horizon; trees and rocks only matter
# closer in (beyond that the terrain and haze hide them and they would cost thousands of draw calls).
RULES = [("landscape/mountains/", "mountain", 420000.0),
         ("landscape/cliffs/", "mountain", 300000.0),
         ("landscape/dirtcliffs/", "cliff", 200000.0),
         ("landscape/rocks/rockcliff", "cliff", 250000.0),
         ("landscape/rocks/rockl", "rock", 120000.0),
         ("landscape/rocks/rockpilel", "rock", 100000.0),
         ("landscape/tundra/", "rock", 120000.0),
         ("landscape/trees/", "tree", 110000.0),
         ("landscape/treessnow/", "tree", 110000.0)]
SKIP = ("lod", "marker", "/plants/", "/grass/", "effects/")


def subs(buf):
    p, ext = 0, None
    while p + 6 <= len(buf):
        t = buf[p:p + 4]; sz, = struct.unpack_from("<H", buf, p + 4); p += 6
        if t == b"XXXX":
            ext, = struct.unpack_from("<I", buf, p); p += 4; continue
        if ext is not None: sz, ext = ext, None
        yield t, buf[p:p + sz]; p += sz


def rot_from_angles(rx, ry, rz):
    """Same as RotFromAngles in plugin/src/main.cpp (and tools/large_refs_preview.py)."""
    ax, ay, az = -rx, -ry, -rz
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    X = [1, 0, 0, 0, cx, -sx, 0, sx, cx]; Y = [cy, 0, sy, 0, 1, 0, -sy, 0, cy]; Z = [cz, -sz, 0, sz, cz, 0, 0, 0, 1]
    mul = lambda A, B: [sum(A[i * 3 + k] * B[k * 3 + j] for k in range(3)) for i in range(3) for j in range(3)]
    return mul(mul(X, Y), Z)


def read_plugin(path, model_of, refs, worlds):
    data = open(path, "rb").read()
    # form ids are stored with the plugin's own master index; Skyrim.esm is index 0 in Update.esm too, so they line up

    def walk(s, e, world):
        p = s
        while p < e:
            t = data[p:p + 4]; sz, = struct.unpack_from("<I", data, p + 4)
            if t == b"GRUP":
                label, gtype = struct.unpack_from("<II", data, p + 8)
                walk(p + 24, p + sz, label if gtype == 1 else world)
                p += sz; continue
            flags, fid = struct.unpack_from("<II", data, p + 8)
            if t in (b"WRLD", b"REFR", b"STAT", b"TREE"):
                body = data[p + 24:p + 24 + sz]
                if flags & 0x40000: body = zlib.decompress(body[4:])
                if t == b"WRLD":
                    for st, sd in subs(body):
                        if st == b"EDID": worlds[fid] = sd.split(b"\0")[0].decode().lower()
                elif t == b"REFR":
                    if flags & 0x820:                                     # deleted / initially disabled
                        refs.pop(fid, None)
                    else:
                        r = {"scale": 1.0, "world": world}
                        for st, sd in subs(body):
                            if st == b"NAME": r["base"], = struct.unpack("<I", sd[:4])
                            elif st == b"DATA" and len(sd) >= 24: r["data"] = struct.unpack("<6f", sd[:24])
                            elif st == b"XSCL": r["scale"], = struct.unpack("<f", sd[:4])
                            elif st == b"XESP": r["parent"] = True                # enable parent: quest-state dependent
                        refs[fid] = r
                else:
                    for st, sd in subs(body):
                        if st == b"MODL": model_of[fid] = sd.split(b"\0")[0].decode("cp1252").lower().replace("\\", "/")
            p += 24 + sz

    walk(0, len(data), None)


def land_heights(sd):
    """LAND VHGT -> 33x33 absolute heights (rows = +y, columns = +x, 128 units apart)."""
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


def read_water(path, cells, worlds, radius=170000.0, land=None):
    """Exterior cells of WORLD whose CELL DATA has the 'has water' flag (0x2) and an explicit XCLW height ->
    cells[(gx, gy)] = height. Without the flag Skyrim draws no water even if XCLW is set (many mountain cells carry one).
    With `land`, also land[(gx, gy)] = 33x33 heights of every exterior cell of WORLD."""
    data = open(path, "rb").read()
    cur = [None]

    def walk(s, e, world):
        p = s
        while p < e:
            t = data[p:p + 4]; sz, = struct.unpack_from("<I", data, p + 4)
            if t == b"GRUP":
                label, gtype = struct.unpack_from("<II", data, p + 8)
                walk(p + 24, p + sz, label if gtype == 1 else world)
                p += sz; continue
            flags, fid = struct.unpack_from("<II", data, p + 8)
            if t == b"LAND" and land is not None and cur[0] is not None and worlds.get(world) == WORLD:
                body = data[p + 24:p + 24 + sz]
                if flags & 0x40000: body = zlib.decompress(body[4:])
                for st, sd in subs(body):
                    if st == b"VHGT": land[cur[0]] = land_heights(sd)
            if t in (b"WRLD", b"CELL"):
                body = data[p + 24:p + 24 + sz]
                if flags & 0x40000: body = zlib.decompress(body[4:])
                if t == b"WRLD":
                    for st, sd in subs(body):
                        if st == b"EDID": worlds[fid] = sd.split(b"\0")[0].decode().lower()
                elif worlds.get(world) == WORLD:
                    xclc = xclw = None; has_water = False
                    for st, sd in subs(body):
                        if st == b"DATA": has_water = bool(sd[0] & 0x02)
                        elif st == b"XCLC": xclc = struct.unpack("<ii", sd[:8])
                        elif st == b"XCLW": xclw, = struct.unpack("<f", sd[:4])
                    cur[0] = xclc
                    if xclc and xclw is not None and abs(xclw) < 1e7:
                        if math.hypot((xclc[0] + .5) * 4096 - CENTER[0], (xclc[1] + .5) * 4096 - CENTER[1]) <= radius:
                            if has_water: cells[xclc] = xclw
                            else: cells.pop(xclc, None)
            p += 24 + sz

    walk(0, len(data), None)


def classify(m):
    if any(s in m for s in SKIP) or " " in m:
        return None
    for prefix, kind, rad in RULES:
        if m.startswith(prefix):
            return kind, rad
    return None


MODEL_TYPES = (b"STAT", b"TREE", b"MSTT", b"FURN", b"ACTI", b"CONT", b"DOOR", b"LIGH", b"FLOR", b"MISC", b"MOVS",
               b"TACT", b"IDLM", b"ADDN", b"WEAP", b"ARMO", b"BOOK", b"INGR", b"ALCH", b"KEYM", b"SLGM", b"AMMO", b"SCRL")


MASTERS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]   # runtime load order 00-04


def remapper(name, data):
    """Plugin-local form id -> runtime form id (official masters, same as tools/tamriel_world.py Remap). The high byte of a
    stored id indexes the plugin's MAST list, then the plugin itself; identity for Skyrim.esm and Update.esm."""
    sz, = struct.unpack_from("<I", data, 4)
    order = [m.lower() for m in MASTERS]
    mast = [sd.split(b"\0")[0].decode("latin1").lower() for st, sd in subs(data[24:24 + sz]) if st == b"MAST"]
    idx = [order.index(m) if m in order else 0xFF for m in mast] + [order.index(name.lower())]
    return lambda fid: ((idx[fid >> 24] if (fid >> 24) < len(idx) else idx[-1]) << 24) | (fid & 0xFFFFFF)


def scan_refs(plugins=PLUGINS, interiors_only=False, templates=None):
    """All placed references of the plugins (later plugins override) with their worldspace and cell, base models/types,
    worldspace names and cells (EDID, interior flag, XCLL lighting). Form ids are runtime ids (see remapper).
    interiors_only skips the worldspace groups (most of the data); with a `templates` dict, lighting templates (LGTM)
    land there and each cell records its LTMP id as c["ltmp"]."""
    model_of, typ, refs, worlds, cells = {}, {}, {}, {}, {}
    for p in plugins:
        path = os.path.join(DATA, p)
        if not os.path.exists(path):
            continue
        data = open(path, "rb").read()
        rm = remapper(p, data)

        def walk(s, e, world, cell):
            q = s
            while q < e:
                t = data[q:q + 4]; sz, = struct.unpack_from("<I", data, q + 4)
                if t == b"GRUP":
                    label, gtype = struct.unpack_from("<II", data, q + 8)
                    if not (interiors_only and gtype == 0 and data[q + 8:q + 12] == b"WRLD"):
                        walk(q + 24, q + sz, rm(label) if gtype == 1 else world, rm(label) if gtype in (6, 8, 9) else cell)
                    q += sz; continue
                flags, fid = struct.unpack_from("<II", data, q + 8)
                fid = rm(fid)
                if t in (b"WRLD", b"REFR", b"CELL") or t in MODEL_TYPES or (t == b"LGTM" and templates is not None):
                    body = data[q + 24:q + 24 + sz]
                    if flags & 0x40000: body = zlib.decompress(body[4:])
                    if t == b"WRLD":
                        for st, sd in subs(body):
                            if st == b"EDID": worlds[fid] = sd.split(b"\0")[0].decode().lower()
                    elif t == b"LGTM":
                        for st, sd in subs(body):
                            if st == b"DATA" and len(sd) >= 12:
                                templates[fid] = [[sd[i], sd[i + 1], sd[i + 2]] for i in (0, 4, 8)]
                    elif t == b"CELL":
                        c = cells.setdefault(fid, {"edid": "", "interior": False})
                        for st, sd in subs(body):
                            if st == b"EDID": c["edid"] = sd.split(b"\0")[0].decode("latin1")
                            elif st == b"DATA": c["interior"] = bool(sd[0] & 0x01)
                            elif st == b"XCLL" and len(sd) >= 12:     # ambient, directional, fog near colours (RGBA bytes)
                                c["ambient"], c["directional"], c["fog"] = ([sd[i], sd[i + 1], sd[i + 2]] for i in (0, 4, 8))
                            elif st == b"LTMP" and templates is not None: c["ltmp"] = rm(struct.unpack("<I", sd[:4])[0])
                    elif t == b"REFR":
                        if flags & 0x20:
                            refs.pop(fid, None)
                        else:
                            r = {"scale": 1.0, "world": world, "cell": cell, "disabled": bool(flags & 0x800)}
                            for st, sd in subs(body):
                                if st == b"NAME": r["base"] = rm(struct.unpack("<I", sd[:4])[0])
                                elif st == b"DATA" and len(sd) >= 24: r["data"] = struct.unpack("<6f", sd[:24])
                                elif st == b"XSCL": r["scale"], = struct.unpack("<f", sd[:4])
                                elif st == b"XESP": r["parent"] = rm(struct.unpack("<I", sd[:4])[0])
                            refs[fid] = r
                    else:
                        for st, sd in subs(body):
                            if st == b"MODL" and fid not in model_of:      # first MODL = world model (ARMO etc. have more)
                                model_of[fid] = sd.split(b"\0")[0].decode("latin1").lower().replace("\\", "/")
                                typ[fid] = t.decode()
                q += 24 + sz

        walk(0, len(data), None, None)
    return model_of, typ, refs, worlds, cells


def ref_items(refs, model_of, typ, keep):
    out = []
    for fid, r in refs.items():
        if not keep(r) or "data" not in r:
            continue
        m = model_of.get(r.get("base"))
        if not m or not m.endswith(".nif"):
            continue
        d = r["data"]
        out.append({"id": fid, "model": m[:-4].replace("/", "_").replace(" ", "_"), "nif": m, "type": typ[r["base"]],
                    "pos": list(d[:3]),
                    "rot": rot_from_angles(*d[3:]), "scale": r["scale"], "disabled": r["disabled"],
                    "parent": r.get("parent", 0)})
    return out


def dump_world(ws):
    """Every placed reference with a model in worldspace `ws` (all base types) -> area2/world_<ws>.json, for comparing
    against what Unreal draws (the stream and the previews)."""
    model_of, typ, refs, worlds, _ = scan_refs()
    out = ref_items(refs, model_of, typ, lambda r: worlds.get(r.get("world")) == ws)
    json.dump(out, open(os.path.join(ROOT, "area2", "world_%s.json" % ws), "w"))
    print("%s: %d refs with models" % (ws, len(out)), Counter(it["type"] for it in out).most_common())


def dump_interiors(prefix):
    """Interior cells whose editor id starts with `prefix` (e.g. 'Whiterun': Dragonsreach, Jorrvaskr, Breezehome, the
    Bannered Mare, shops, houses) -> area2/interiors_<prefix>.json {edid: {id, ambient, directional, fog, refs: [...]}}."""
    model_of, typ, refs, worlds, cells = scan_refs()
    want = {fid: c for fid, c in cells.items() if c["interior"] and c["edid"].lower().startswith(prefix.lower())}
    by_cell = {}
    for it in ref_items(refs, model_of, typ, lambda r: r.get("cell") in want):
        by_cell.setdefault(refs[it["id"]]["cell"], []).append(it)
    out = {}
    for fid, c in want.items():
        out[c["edid"]] = {"id": fid, "ambient": c.get("ambient"), "directional": c.get("directional"), "fog": c.get("fog"),
                          "refs": by_cell.get(fid, [])}
    json.dump(out, open(os.path.join(ROOT, "area2", "interiors_%s.json" % prefix.lower()), "w"))
    for k, v in sorted(out.items(), key=lambda kv: -len(kv[1]["refs"])):
        print("%5d %s" % (len(v["refs"]), k))
    print("%d interior cells, %d refs" % (len(out), sum(len(v["refs"]) for v in out.values())))


LOOSE_ITEMS = {"ALCH", "BOOK", "INGR", "MISC", "WEAP", "ARMO", "KEYM", "SLGM", "AMMO", "SCRL"}
REAL_MARKERS = ("forge", "tanningrack", "smelter", "grindstone", "anvil", "workbench", "enchant", "alchemy",
                "cookingpot", "cookingspit")


def drawn(it):
    """Same rules as Live.city_keep in live_bridge.py: the references the interior layer actually places."""
    m = it["nif"]
    if it["disabled"] or it["parent"] or it["type"] in LOOSE_ITEMS or " " in it["model"]:
        return False
    if m.startswith(("effects/", "fx")) or "/fx" in m:
        return False
    return "marker" not in m or any(k in m for k in REAL_MARKERS)


def dump_dungeons(refs_per_file=30000):
    """Every interior cell of the official masters (Skyrim, Update, Dawnguard, HearthFires, Dragonborn; runtime form ids)
    that no other area2/interiors_*.json covers (caves, barrows, Dwemer ruins, forts, mines, DLC interiors...) ->
    area2/interiors_dungeons_<n>.json (same per-cell format as --interiors, ~refs_per_file refs each) and
    area2/dungeon_models.txt: count<TAB>model<TAB>nif<TAB>converted, models of the drawn refs, most used first, and
    area2/dungeon_index.json {edid: {file, id, refs, probe: up to 64 drawn STAT ref ids}} for lazy loading.
    Cells without XCLL take the colours of their lighting template (LTMP -> LGTM)."""
    area = os.path.join(ROOT, "area2")
    covered = set()
    for p in os.listdir(area):
        if p.startswith("interiors_") and p.endswith(".json") and not p.startswith("interiors_dungeons_"):
            covered |= set(json.load(open(os.path.join(area, p))))
    templates = {}
    model_of, typ, refs, worlds, cells = scan_refs(MASTERS, interiors_only=True, templates=templates)
    want = {fid: c for fid, c in cells.items() if c["interior"] and c["edid"] not in covered}
    by_cell = {}
    for it in ref_items(refs, model_of, typ, lambda r: r.get("cell") in want):
        by_cell.setdefault(refs[it["id"]]["cell"], []).append(it)
    out, lit = {}, Counter()
    for fid, c in sorted(want.items(), key=lambda kv: kv[1]["edid"].lower() or "~%08x" % kv[0]):
        if not by_cell.get(fid):
            continue
        light = [c.get("ambient"), c.get("directional"), c.get("fog")]
        lit["xcll" if light[0] is not None else "none"] += 1
        if light[0] is None and c.get("ltmp") in templates:
            light = templates[c["ltmp"]]; lit["template"] += 1; lit["none"] -= 1
        out[c["edid"] or "cell_%08X" % fid] = {"id": fid, "ambient": light[0], "directional": light[1], "fog": light[2],
                                               "refs": by_cell[fid]}
    for p in os.listdir(area):                                           # stale parts of an earlier, bigger run
        if p.startswith("interiors_dungeons_") and p.endswith(".json"):
            os.remove(os.path.join(area, p))
    part, n, files = {}, 0, []

    def flush():
        name = "interiors_dungeons_%d.json" % (len(files) + 1)
        json.dump(part, open(os.path.join(area, name), "w"))
        files.append((name, len(part), sum(len(v["refs"]) for v in part.values())))

    index = {}
    for k, v in out.items():
        part[k] = v; n += len(v["refs"])
        probe = [it["id"] for it in v["refs"] if it["type"] == "STAT" and drawn(it)][:64]
        index[k] = {"file": "interiors_dungeons_%d.json" % (len(files) + 1), "id": v["id"], "refs": len(v["refs"]),
                    "probe": probe}
        if n >= refs_per_file:
            flush(); part, n = {}, 0
    if part:
        flush()
    # dungeon_index.json (deliberately outside the interiors_*.json glob): enough to detect the cell from streamed ids
    # and load only its file, instead of holding all ~380k dungeon refs in the editor.
    json.dump(index, open(os.path.join(area, "dungeon_index.json"), "w"))
    uses, nif_of = Counter(), {}
    for v in out.values():
        for it in v["refs"]:
            if drawn(it):
                uses[it["model"]] += 1; nif_of[it["model"]] = it["nif"]
    content = os.path.join(ROOT, "unreal", "SkyBridge", "Content", "Area2")
    done = 0
    with open(os.path.join(area, "dungeon_models.txt"), "w") as f:
        f.write("# count\tmodel\tnif\tconverted (Content/Area2/<model>.uasset exists); drawn dungeon refs, most used first\n")
        for m, cnt in uses.most_common():
            conv = os.path.exists(os.path.join(content, m + ".uasset")); done += conv
            f.write("%d\t%s\t%s\t%d\n" % (cnt, m, nif_of[m], conv))
    for name, nc, nr in files:
        print("%s: %d cells, %d refs, %.1f MB" % (name, nc, nr, os.path.getsize(os.path.join(area, name)) / 1e6))
    total = sum(len(v["refs"]) for v in out.values())
    print("%d dungeon cells (%d already covered by other interiors files), %d refs, %d drawn refs, %d distinct models "
          "(%d drawn, %d already converted); lighting %s" % (len(out), len(covered), total, sum(uses.values()),
          len({it["model"] for v in out.values() for it in v["refs"]}), len(uses), done, dict(lit)))
    print("by plugin:", dict(Counter(MASTERS[v["id"] >> 24] for v in out.values())))
    counts = [c for _, c in uses.most_common()]
    print("drawn refs covered by the top N models:",
          ", ".join("%d: %.0f%%" % (k, 100.0 * sum(counts[:k]) / max(1, sum(counts))) for k in (100, 250, 500, 1000, 2000)))


def main():
    if "--dungeons" in sys.argv:
        dump_dungeons()
        return
    if "--world" in sys.argv:
        dump_world(sys.argv[sys.argv.index("--world") + 1].lower())
        return
    if "--interiors" in sys.argv:
        dump_interiors(sys.argv[sys.argv.index("--interiors") + 1])
        return
    if "--water" in sys.argv:
        cells, worlds, land = {}, {}, {}
        for p in PLUGINS:
            if os.path.exists(os.path.join(DATA, p)):
                read_water(os.path.join(DATA, p), cells, worlds, land=land)
        with open(os.path.join(ROOT, "area2", "water_wide.csv"), "w") as f:
            for (gx, gy), h in sorted(cells.items()):
                f.write("%d,%d,%.1f\n" % (gx, gy, h))
        # Visible water only: 128-unit squares where the real terrain dips below the cell's water height (dilated by one
        # square so shores meet the land), merged into runs along x. A whole-cell plane floated as a dark see-through
        # slab wherever Unreal's coarser terrain is lower than Skyrim's.
        runs = 0
        with open(os.path.join(ROOT, "area2", "water_quads.csv"), "w") as f:
            for (gx, gy), h in sorted(cells.items()):
                hm = land.get((gx, gy))
                if hm is None:
                    for r in range(32):
                        f.write("%d,%d,32,%.1f\n" % (gx * 4096, gy * 4096 + r * 128, h)); runs += 1
                    continue
                wet = [[min(hm[r][c], hm[r][c + 1], hm[r + 1][c], hm[r + 1][c + 1]) < h for c in range(32)] for r in range(32)]
                grow = [[any(wet[rr][cc] for rr in range(max(0, r - 1), min(32, r + 2))
                             for cc in range(max(0, c - 1), min(32, c + 2))) for c in range(32)] for r in range(32)]
                for r in range(32):
                    c = 0
                    while c < 32:
                        if not grow[r][c]:
                            c += 1; continue
                        s = c
                        while c < 32 and grow[r][c]: c += 1
                        f.write("%d,%d,%d,%.1f\n" % (gx * 4096 + s * 128, gy * 4096 + r * 128, c - s, h)); runs += 1
        print("water_quads.csv: %d runs (%d cells had LAND)" % (runs, sum(1 for k in cells if k in land)))
        print("wrote %d water cells to area2/water_wide.csv; heights:" % len(cells),
              Counter(round(h) for h in cells.values()).most_common(8))
        return
    model_of, refs, worlds = {}, {}, {}
    for p in PLUGINS:
        path = os.path.join(DATA, p)
        if os.path.exists(path):
            read_plugin(path, model_of, refs, worlds)
            print("read", p, len(refs), "refs")
    out, kinds, folders = [], Counter(), Counter()
    for fid, r in refs.items():
        if worlds.get(r.get("world")) != WORLD or "data" not in r or r.get("parent"):
            continue
        m = model_of.get(r.get("base"))
        if not m or not m.endswith(".nif"):
            continue
        d = r["data"]
        dist = math.hypot(d[0] - CENTER[0], d[1] - CENTER[1])
        if dist < 420000.0:
            folders[m.rsplit("/", 1)[0]] += 1
        c = classify(m)
        if not c or dist > c[1]:
            continue
        kinds[c[0]] += 1
        out.append({"id": fid, "model": m[:-4].replace("/", "_"), "nif": m, "pos": list(d[:3]),
                    "rot": rot_from_angles(*d[3:]), "scale": r["scale"], "kind": c[0], "dist": round(dist)})
    out.sort(key=lambda it: (it["kind"] not in ("mountain", "cliff"), it["dist"]))   # horizon first
    if "--stats" in sys.argv:
        for f, n in folders.most_common(40): print("%6d %s" % (n, f))
    print("kinds:", dict(kinds), "unique models:", len({it["model"] for it in out}))
    json.dump(out, open(os.path.join(ROOT, "area2", "distant_refs.json"), "w"))
    print("wrote %d refs to area2/distant_refs.json" % len(out))


if __name__ == "__main__":
    main()
