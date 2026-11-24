"""All of Tamriel for Unreal: every placed reference with a model in the Tamriel worldspace (forts, castles, farms, villages,
ruins, bridges, trees, rocks, plants...) from the official masters, split into tiles that live_bridge streams around the player
(unreal/SkyBridge/tamriel_live.py).

Form ids are remapped to the runtime load order of the official masters (Skyrim.esm 00, Update.esm 01, Dawnguard.esm 02,
HearthFires.esm 03, Dragonborn.esm 04), so they match the ids the plugin streams.

Output (area2/tamriel/):
  models.json          [[asset name, nif path], ...]
  mountains.json       mountains/cliffs of the whole map (always drawn)
  f_<tx>_<ty>.json     'far' kinds (architecture, dungeons exteriors, trees, big rocks) in 16x16-cell tiles
  n_<tx>_<ty>.json     everything else (clutter, fences, plants, small rocks...) in 4x4-cell tiles
     item = [form id, model index, x, y, z, rx, ry, rz, scale]   (Skyrim units / radians)
  index.json           {"far": [[tx, ty, count], ...], "near": [...], "mountains": n}
  worlds.json          {edid: full name} of every worldspace
  city_cells.json      {city worldspace edid: ["gx,gy", ...]} cells the city worldspaces cover (Tamriel copies are hidden there)
Usage: python tools/tamriel_world.py [--stats]"""
import json, math, os, struct, sys, zlib
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from distant_world import subs, MODEL_TYPES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
OUT = os.path.join(ROOT, "area2", "tamriel")
MASTERS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
TAMRIEL = 0x0000003C
CITY_WORLDS = ("whiterunworld", "solitudeworld", "windhelmworld", "markarthworld", "riftenworld")
NEAR_TILE, FAR_TILE = 4, 16                        # cells per tile side (a cell is 4096 units)

MOUNTAIN = ("landscape/mountains/", "landscape/cliffs/", "landscape/dirtcliffs/", "landscape/rocks/rockcliff",
            "landscape/ice/", "landscape/glacier")
FAR = ("architecture/", "dungeons/", "landscape/trees/", "landscape/treessnow/", "landscape/rocks/rockl",
       "landscape/rocks/rockpilel", "landscape/tundra/", "landscape/waterfalls/", "dlc01/landscape/trees",
       "dlc02/landscape/trees", "dlc01/architecture", "dlc02/architecture", "dlc01/dungeons", "dlc02/dungeons")
LOOSE_ITEMS = {"ALCH", "BOOK", "INGR", "MISC", "WEAP", "ARMO", "KEYM", "SLGM", "AMMO", "SCRL"}
REAL_MARKERS = ("forge", "tanningrack", "smelter", "grindstone", "anvil", "workbench", "enchant", "alchemy",
                "cookingpot", "cookingspit")


def keep(m, typ):
    """Same rules as Live.city_keep: loose items, effects and editor markers stay with the live stream."""
    if typ in LOOSE_ITEMS or " " in m or not m.endswith(".nif"):
        return False
    if m.startswith(("effects/", "fx", "markers/")) or "/fx" in m or "lod" in m.rsplit("/", 1)[-1]:
        return False
    return "marker" not in m or any(k in m for k in REAL_MARKERS)


def kind(m):
    if m.startswith(MOUNTAIN):
        return "mtn"
    if m.startswith(FAR):
        return "far"
    return "near"


def read_masters(data):
    """TES4 header MAST list of a plugin."""
    sz, = struct.unpack_from("<I", data, 4)
    body = data[24:24 + sz]
    return [sd.split(b"\0")[0].decode("latin1").lower() for st, sd in subs(body) if st == b"MAST"]


class Remap:
    """Plugin-local form id -> runtime form id (official masters only)."""
    def __init__(self, name, data):
        order = [m.lower() for m in MASTERS]
        self.idx = [order.index(m) if m in order else 0xFF for m in read_masters(data)] + [order.index(name.lower())]

    def __call__(self, fid):
        hi = fid >> 24
        return ((self.idx[hi] if hi < len(self.idx) else self.idx[-1]) << 24) | (fid & 0xFFFFFF)


def scan(want_world=None, on_record=None):
    """Walk every official master; on_record(plugin, remap, type, flags, fid, body, world, cell_xy) for WRLD/CELL/REFR/LAND/
    LTEX/TXST and model base records. `cell_xy` is the exterior cell grid of the enclosing CELL (or None)."""
    for name in MASTERS:
        path = os.path.join(DATA, name)
        if not os.path.exists(path):
            continue
        data = open(path, "rb").read()
        rm = Remap(name, data)
        state = {"xy": None}
        wanted = (b"WRLD", b"CELL", b"REFR", b"LAND", b"LTEX", b"TXST") + MODEL_TYPES

        def walk(s, e, world):
            q = s
            while q < e:
                t = data[q:q + 4]; sz, = struct.unpack_from("<I", data, q + 4)
                if t == b"GRUP":
                    label, gtype = struct.unpack_from("<II", data, q + 8)
                    if gtype == 1:
                        w = rm(label)
                        if want_world is None or w == want_world:
                            walk(q + 24, q + sz, w)
                    elif gtype == 0 and data[q + 8:q + 12] in (b"CELL", b"DIAL", b"QUST", b"NPC_", b"PACK", b"IDLE"):
                        pass                                              # interior cells / quest data: not needed
                    else:
                        walk(q + 24, q + sz, world)
                    q += sz; continue
                flags, fid = struct.unpack_from("<II", data, q + 8)
                if t in wanted:
                    body = data[q + 24:q + 24 + sz]
                    if flags & 0x40000:
                        body = zlib.decompress(body[4:])
                    if t == b"CELL":
                        state["xy"] = None
                        for st, sd in subs(body):
                            if st == b"XCLC": state["xy"] = struct.unpack("<ii", sd[:8])
                    on_record(name, rm, t, flags, rm(fid), body, world, state["xy"])
                q += 24 + sz

        walk(0, len(data), None)
        print("scanned", name)


def main():
    os.makedirs(OUT, exist_ok=True)
    model_of, typ, refs, worlds = {}, {}, {}, {}

    def on_record(name, rm, t, flags, fid, body, world, xy):
        if t == b"WRLD":
            w = {"edid": "", "full": ""}
            for st, sd in subs(body):
                if st == b"EDID": w["edid"] = sd.split(b"\0")[0].decode("latin1").lower()
                elif st == b"FULL" and len(sd) > 4 and sd[-1:] == b"\0": w["full"] = sd[:-1].decode("latin1")
            worlds[fid] = w
        elif t == b"REFR":
            if world is None:
                return
            if flags & 0x20:
                refs.pop(fid, None); return
            r = {"world": world, "scale": 1.0, "disabled": bool(flags & 0x800), "parent": 0}
            for st, sd in subs(body):
                if st == b"NAME": r["base"] = rm(struct.unpack("<I", sd[:4])[0])
                elif st == b"DATA" and len(sd) >= 24: r["data"] = struct.unpack("<6f", sd[:24])
                elif st == b"XSCL": r["scale"], = struct.unpack("<f", sd[:4])
                elif st == b"XESP": r["parent"] = rm(struct.unpack("<I", sd[:4])[0])
            refs[fid] = r
        elif t in MODEL_TYPES:
            for st, sd in subs(body):
                if st == b"MODL":
                    model_of[fid] = sd.split(b"\0")[0].decode("latin1").lower().replace("\\", "/")
                    typ[fid] = t.decode(); break

    scan(None, on_record)
    full = {w["edid"]: w["full"] for w in worlds.values() if w["edid"]}
    json.dump(full, open(os.path.join(OUT, "worlds.json"), "w"), indent=0)
    city_ids = {fid: w["edid"] for fid, w in worlds.items() if w["edid"] in CITY_WORLDS}

    models, mindex = [], {}
    near, far, mtn = defaultdict(list), defaultdict(list), []
    city_cells, kinds, folders = defaultdict(set), Counter(), Counter()
    for fid, r in refs.items():
        if "data" not in r:
            continue
        d = r["data"]
        if r["world"] in city_ids:
            city_cells[city_ids[r["world"]]].add("%d,%d" % (math.floor(d[0] / 4096), math.floor(d[1] / 4096)))
            continue
        if r["world"] != TAMRIEL or r["disabled"] or r["parent"]:
            continue
        m = model_of.get(r.get("base"))
        if not m or not keep(m, typ.get(r["base"])):
            continue
        name = m[:-4].replace("/", "_")
        if name not in mindex:
            mindex[name] = len(models); models.append([name, m])
        item = [fid, mindex[name], round(d[0], 1), round(d[1], 1), round(d[2], 1),
                round(d[3], 5), round(d[4], 5), round(d[5], 5), round(r["scale"], 4)]
        k = kind(m); kinds[k] += 1; folders[m.rsplit("/", 1)[0]] += 1
        gx, gy = math.floor(d[0] / 4096), math.floor(d[1] / 4096)
        if k == "mtn":
            mtn.append(item)
        elif k == "far":
            far[(math.floor(gx / FAR_TILE), math.floor(gy / FAR_TILE))].append(item)
        else:
            near[(math.floor(gx / NEAR_TILE), math.floor(gy / NEAR_TILE))].append(item)

    for f in os.listdir(OUT):
        if f[:2] in ("n_", "f_"):
            os.remove(os.path.join(OUT, f))
    for prefix, tiles in (("n", near), ("f", far)):
        for (tx, ty), items in tiles.items():
            json.dump(items, open(os.path.join(OUT, "%s_%d_%d.json" % (prefix, tx, ty)), "w"), separators=(",", ":"))
    json.dump(mtn, open(os.path.join(OUT, "mountains.json"), "w"), separators=(",", ":"))
    json.dump(models, open(os.path.join(OUT, "models.json"), "w"))
    json.dump({"near": [[x, y, len(v)] for (x, y), v in sorted(near.items())],
               "far": [[x, y, len(v)] for (x, y), v in sorted(far.items())],
               "mountains": len(mtn), "near_tile": NEAR_TILE, "far_tile": FAR_TILE},
              open(os.path.join(OUT, "index.json"), "w"))
    json.dump({k: sorted(v) for k, v in city_cells.items()}, open(os.path.join(OUT, "city_cells.json"), "w"))
    if "--stats" in sys.argv:
        for f, n in folders.most_common(60): print("%7d %s" % (n, f))
    print("Tamriel full name: %r" % worlds.get(TAMRIEL, {}).get("full"))
    print("refs:", dict(kinds), "models:", len(models), "near tiles:", len(near), "far tiles:", len(far))
    print("city cells:", {k: len(v) for k, v in city_cells.items()})


if __name__ == "__main__":
    main()
