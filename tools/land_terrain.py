"""Full-resolution Tamriel terrain with per-layer landscape textures (replaces the baked-tile terrain + covers water cells).

Reads LAND (VHGT heights, VNML normals, VCLR vertex colours, BTXT/ATXT/VTXT texture layers) from Skyrim.esm + Update.esm
for every Tamriel cell within --radius of Whiterun, every water cell of area2/water_wide.csv within --water-radius (plus
--water-ring neighbour cells) and every cell of the old baked terrain (area2/terrain_obj/terrain.obj). LTEX -> TXST
diffuse/normal textures (loose Data files win over BSAs) are converted to PNG.

Per tile of --tile x --tile cells (default 4x4 = 129x129 vertices):
  area2/landterrain/tiles/LT_<tx>_<ty>.npz   mesh arrays (absolute Skyrim units, same convention as terrain.obj)
  area2/landterrain/tex/LTW_<tx>_<ty>_0.png  layer weights 0-3 (RGBA), _1.png layers 4-7; one pixel per LAND vertex
  area2/landterrain/tiles.json               per tile: cells, layer texture keys (weight channel order), origin
  area2/landterrain/tex/<key>.png            layer colour, A = height (diffuse alpha, CS parallax alpha or luminance)
  area2/landterrain/tex/<key>_n.png          layer normal map
  area2/landterrain/fbx/LT_<tx>_<ty>.fbx     Blender export (metres, forward -Y, up Z like tools/blender_export.py)
UV0 = tile-local Skyrim units / 512 (one texture repeat; 0..32 for a 4x4 tile, exact in half floats),
UV1 = weight texture coordinate (pixel centres), vertex colour = VCLR.
Weights follow Skyrim's blending: per quadrant the base layer, then each ATXT layer alpha-composited in layer order.

Usage: python tools/land_terrain.py [--radius 32768] [--water-radius 1e9] [--water-ring 1] [--tile 4] [--center x,y]
                                    [--no-tex] [--no-fbx] [--only LT_5_-1,LT_6_-1] [--lod]
       --lod also writes area2/landterrain/lod/landlod.obj (+fbx): Skyrim's LOD terrain (area2/lod_obj/lodterrain.obj)
       without the triangles over the cells this terrain covers.
(Blender side, run by this script: D:\\blender.exe -b -P tools/land_terrain.py -- --blender <npz...>)"""
import glob, io, json, math, os, struct, subprocess, sys, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
OUT = os.path.join(AREA, "landterrain")
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
BLENDER = r"D:\blender.exe"
PLUGINS = ["Skyrim.esm", "Update.esm"]
WORLD = "tamriel"
SCALE = 0.014287                       # Skyrim unit -> metre (blender_export.py)
TEX_UNITS = 512.0                      # one landscape texture repeat in Skyrim units (material parameter LayerTiling scales it)
MAX_LAYERS = 16
TEXMAX = 2048
DEFAULT_TEX = "landscape\\dirt02.dds"  # quadrants without a BTXT use the game's default dirt


# ----------------------------------------------------------------------------------------------------------------- Blender
def blender_main(paths):
    import bpy
    import numpy as np
    out_dir = os.path.join(OUT, "fbx")
    os.makedirs(out_dir, exist_ok=True)
    for p in paths:
        name = os.path.splitext(os.path.basename(p))[0]
        dst = os.path.join(out_dir, name + ".fbx")
        if os.path.exists(dst) and os.path.getmtime(dst) > os.path.getmtime(p) and not os.environ.get("FORCE"):
            continue
        d = np.load(p)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        pos, tris = d["pos"].astype(np.float64) * SCALE, d["tris"]
        me = bpy.data.meshes.new(name)
        me.from_pydata(pos.tolist(), [], tris.tolist())
        li = np.zeros(len(me.loops), dtype=np.int32)
        me.loops.foreach_get("vertex_index", li)
        for uvname, arr in (("UV0", d["uv0"]), ("UV1", d["uv1"])):
            uv = me.uv_layers.new(name=uvname)
            uv.data.foreach_set("uv", arr[li].astype(np.float32).ravel())
        col = me.color_attributes.new("Col", 'BYTE_COLOR', 'POINT')
        rgba = np.concatenate([d["col"].astype(np.float32) / 255.0, np.ones((len(pos), 1), np.float32)], axis=1)
        col.data.foreach_set("color_srgb", rgba.ravel())
        me.update()
        try:
            me.normals_split_custom_set_from_vertices(d["nrm"].astype(np.float64).tolist())
        except Exception as e:
            print("custom normals skipped", e)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True); bpy.context.view_layer.objects.active = ob
        bpy.ops.export_scene.fbx(filepath=dst, use_selection=True, axis_forward='-Y', axis_up='Z', global_scale=1.0,
                                 apply_unit_scale=True, mesh_smooth_type='OFF', colors_type='SRGB', use_tspace=False)
        print("EXPORTED", name, len(pos), "verts", len(tris), "tris")


def blender_obj(obj_dir, out_dir):
    """OBJ -> FBX with the converter's conventions (used for the trimmed LOD terrain)."""
    import bpy
    for path in sorted(glob.glob(os.path.join(obj_dir, "*.obj"))):
        name = os.path.splitext(os.path.basename(path))[0]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.obj_import(filepath=path, forward_axis='Y', up_axis='Z')
        objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        for o in objs:
            o.scale = (SCALE, SCALE, SCALE)
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs: o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if len(objs) > 1: bpy.ops.object.join()
        o = bpy.context.view_layer.objects.active; o.name = name; o.data.name = name
        bpy.ops.export_scene.fbx(filepath=os.path.join(out_dir, name + ".fbx"), use_selection=True, axis_forward='-Y',
                                 axis_up='Z', global_scale=1.0, apply_unit_scale=True)
        print("EXPORTED", name)


if "--blender" in sys.argv or "--blender-obj" in sys.argv:
    args = sys.argv[sys.argv.index("--") + 1:]
    if args[0] == "--blender":
        blender_main(args[1:])
    else:
        blender_obj(args[1], args[2])
    raise SystemExit(0)

# ------------------------------------------------------------------------------------------------------------------ ESM side
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bsa import Bsa


def arg(name, default, conv=float):
    return conv(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def subs(buf):
    p, ext = 0, None
    while p + 6 <= len(buf):
        t = buf[p:p + 4]; sz, = struct.unpack_from("<H", buf, p + 4); p += 6
        if t == b"XXXX":
            ext, = struct.unpack_from("<I", buf, p); p += 4; continue
        if ext is not None: sz, ext = ext, None
        yield t, buf[p:p + sz]; p += sz


def read_plugin(path, want, worlds, ltex, txst, land, wlist, prio):
    """LTEX/TXST everywhere; LAND of cells of the worldspaces in wlist (first wins: Whiterun's city worldspace has its own
    ground under the city) for which want((gx, gy)) is true (later plugins override the same worldspace)."""
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
            if t in (b"WRLD", b"CELL", b"LTEX", b"TXST") or (t == b"LAND" and cur[0] is not None and want(cur[0])
                                                              and worlds.get(world) in wlist):
                body = data[p + 24:p + 24 + sz]
                if flags & 0x40000: body = zlib.decompress(body[4:])
                if t == b"WRLD":
                    for st, sd in subs(body):
                        if st == b"EDID": worlds[fid] = sd.split(b"\0")[0].decode().lower()
                elif t == b"CELL":
                    cur[0] = None
                    if worlds.get(world) in wlist:
                        for st, sd in subs(body):
                            if st == b"XCLC": cur[0] = struct.unpack("<ii", sd[:8])
                elif t == b"LTEX":
                    for st, sd in subs(body):
                        if st == b"TNAM": ltex[fid] = struct.unpack("<I", sd[:4])[0]
                elif t == b"TXST":
                    r = {}
                    for st, sd in subs(body):
                        if st in (b"TX00", b"TX01"): r[st] = sd.split(b"\0")[0].decode("cp1252").lower().replace("/", "\\")
                    txst[fid] = r
                elif t == b"LAND":
                    pr = wlist.index(worlds.get(world))
                    if pr <= prio.get(cur[0], 99):
                        rec = parse_land(body)
                        if rec: land[cur[0]] = rec; prio[cur[0]] = pr
            p += 24 + sz

    walk(0, len(data), None)


def parse_land(body):
    h = nrm = col = None
    base, layers, cur = {}, [], None
    for st, sd in subs(body):
        if st == b"VHGT":
            off, = struct.unpack_from("<f", sd, 0)
            d = np.frombuffer(sd, dtype=np.int8, count=1089, offset=4).astype(np.float64).reshape(33, 33)
            col0 = np.cumsum(d[:, 0]) + off                      # first column runs down the rows, then each row along x
            row = np.cumsum(np.concatenate([col0[:, None], d[:, 1:]], axis=1), axis=1)
            h = row * 8.0
        elif st == b"VNML" and len(sd) >= 3267:
            nrm = np.frombuffer(sd, dtype=np.uint8, count=3267).reshape(33, 33, 3)
        elif st == b"VCLR" and len(sd) >= 3267:
            col = np.frombuffer(sd, dtype=np.uint8, count=3267).reshape(33, 33, 3)
        elif st == b"BTXT":
            f, q = struct.unpack("<IB", sd[:5]); base[q] = f
        elif st == b"ATXT":
            f, q, _u, lay = struct.unpack("<IBBh", sd[:8])
            cur = {"ltex": f, "q": q, "layer": lay, "op": np.zeros((17, 17))}; layers.append(cur)
        elif st == b"VTXT" and cur is not None:
            for i in range(len(sd) // 8):
                pos, _u, op = struct.unpack_from("<HHf", sd, i * 8)
                if pos < 289: cur["op"][pos // 17, pos % 17] = op
    if h is None:
        return None
    return {"h": h, "nrm": nrm, "col": col, "base": base, "layers": layers}


def cell_normals(h, vnml):
    """Normals from the heights; VNML is used when it agrees (its byte encoding varies between tools)."""
    gy, gx = np.gradient(h, 128.0)
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    if vnml is not None:
        for v in (vnml.view(np.int8).astype(np.float64), vnml.astype(np.float64) - 127.5):
            v = v / np.maximum(np.linalg.norm(v, axis=2, keepdims=True), 1e-6)
            if (v * n).sum(axis=2).mean() > 0.95:
                return v
    return n


def cell_weights(rec):
    """ltex fid (0 = default dirt) -> 33x33 weight (sum 1 per vertex; quadrant seams averaged)."""
    acc, cnt = {}, np.zeros((33, 33))
    for q in range(4):
        ws = {rec["base"].get(q, 0): np.ones((17, 17))}
        for l in sorted((l for l in rec["layers"] if l["q"] == q), key=lambda l: l["layer"]):
            a = np.clip(l["op"], 0.0, 1.0)
            for k in ws: ws[k] = ws[k] * (1.0 - a)
            ws[l["ltex"]] = ws.get(l["ltex"], 0.0) + a
        oy, ox = (q // 2) * 16, (q % 2) * 16
        for k, w in ws.items():
            acc.setdefault(k, np.zeros((33, 33)))[oy:oy + 17, ox:ox + 17] += w
        cnt[oy:oy + 17, ox:ox + 17] += 1
    return {k: v / cnt for k, v in acc.items()}


# ---------------------------------------------------------------------------------------------------------------- textures
class TexSource:
    def __init__(self):
        self.loose = {}
        root = os.path.join(DATA, "textures")
        for p in glob.glob(os.path.join(root, "landscape", "**", "*.dds"), recursive=True):
            self.loose[os.path.relpath(p, DATA).lower()] = p
        self.archives = []
        names = sorted(glob.glob(os.path.join(DATA, "*.bsa")))
        vanilla = [p for p in names if os.path.basename(p).lower().startswith("skyrim - textures")]
        for p in vanilla + [p for p in names if p not in vanilla]:   # later archives win (searched last-first)
            try:
                self.archives.append(Bsa(p))
            except Exception:
                pass

    def raw(self, rel):
        key = ("textures\\" + rel).lower()
        if key in self.loose:
            return open(self.loose[key], "rb").read()
        loose = os.path.join(DATA, key)
        if os.path.exists(loose):
            return open(loose, "rb").read()
        for a in reversed(self.archives):
            if key in a.files:
                return a.read(key)
        return None

    @staticmethod
    def decode(raw):
        if raw[84:88] == b"DX10":
            f = struct.unpack_from("<I", raw, 128)[0]
            if f in (72, 75, 78, 99):
                raw = raw[:128] + struct.pack("<I", f - 1) + raw[132:]
        im = Image.open(io.BytesIO(raw)); im.load()
        return im


def tex_key(rel):
    stem = os.path.splitext(rel)[0]
    stem = stem[len("landscape\\"):] if stem.startswith("landscape\\") else stem
    return "lt_" + "".join(c if c.isalnum() else "_" for c in stem)


def convert_layer(src, key, diff, norm):
    """<key>.png (RGB + height in A) and <key>_n.png; returns True when the colour map exists."""
    tdir = os.path.join(OUT, "tex")
    cpath, npath = os.path.join(tdir, key + ".png"), os.path.join(tdir, key + "_n.png")
    if not os.path.exists(cpath):
        raw = src.raw(diff)
        if raw is None:
            print("missing colour map", diff); return False
        im = src.decode(raw).convert("RGBA")
        if max(im.size) > TEXMAX: im = im.resize((TEXMAX, TEXMAX), Image.LANCZOS)
        a = np.asarray(im.getchannel("A"), dtype=np.float32) / 255.0
        height = None
        if a.std() > 0.04:
            height = im.getchannel("A")
        else:
            pr = src.raw("landscape\\parallax\\" + os.path.basename(diff))
            if pr:
                try:
                    pim = src.decode(pr).convert("RGBA").resize(im.size, Image.BILINEAR)
                    if np.asarray(pim.getchannel("A"), dtype=np.float32).std() / 255.0 > 0.04:
                        height = pim.getchannel("A")
                except Exception as e:
                    print("parallax decode failed", diff, e)
        if height is None:                                      # luminance, stretched to 0..1
            l = np.asarray(im.convert("L"), dtype=np.float32)
            lo, hi = np.percentile(l, 2), np.percentile(l, 98)
            height = Image.fromarray(np.clip((l - lo) / max(hi - lo, 1.0) * 255.0, 0, 255).astype(np.uint8))
        im.putalpha(height)
        im.save(cpath)
    if not os.path.exists(npath):
        raw = src.raw(norm) if norm else None
        if raw is None:
            raw = src.raw(os.path.splitext(diff)[0] + "_n.dds")
        if raw is not None:
            try:
                im = src.decode(raw).convert("RGB")
                if max(im.size) > TEXMAX: im = im.resize((TEXMAX, TEXMAX), Image.LANCZOS)
                im.save(npath)
            except Exception as e:
                print("normal decode failed", norm, e)
    return True


# -------------------------------------------------------------------------------------------------------------------- main
def selected_cells(center, radius, wradius, ring):
    cells = set()
    r = int(radius // 4096) + 2
    c0 = (int(center[0] // 4096), int(center[1] // 4096))
    for gx in range(c0[0] - r, c0[0] + r + 1):
        for gy in range(c0[1] - r, c0[1] + r + 1):
            if math.hypot((gx + .5) * 4096 - center[0], (gy + .5) * 4096 - center[1]) <= radius:
                cells.add((gx, gy))
    water = set()
    wpath = os.path.join(AREA, "water_wide.csv")
    if os.path.exists(wpath):
        for line in open(wpath).read().split():
            gx, gy, _h = line.split(",")
            gx, gy = int(gx), int(gy)
            if math.hypot((gx + .5) * 4096 - center[0], (gy + .5) * 4096 - center[1]) <= wradius:
                for dx in range(-ring, ring + 1):
                    for dy in range(-ring, ring + 1):
                        water.add((gx + dx, gy + dy))
    old = set()
    tpath = os.path.join(AREA, "terrain_obj", "terrain.obj")
    if os.path.exists(tpath):
        for line in open(tpath):
            if line.startswith("o terrain_tile_"):
                gx, gy = line.split()[1][len("terrain_tile_"):].split("_")
                old.add((int(gx), int(gy)))
    return cells | water | old, len(cells), len(water), len(old)


def main():
    center = tuple(map(float, arg("--center", "23000,-6000", str).split(",")))
    radius = arg("--radius", 32768.0)
    wradius = arg("--water-radius", 1e9)
    ring = int(arg("--water-ring", 1.0))
    T = int(arg("--tile", 4.0))
    max_layers = int(arg("--layers", MAX_LAYERS))
    only = set(arg("--only", "", str).split(",")) - {""}
    want, n_near, n_water, n_old = selected_cells(center, radius, wradius, ring)
    print("cells wanted: %d (radius %d, water+ring %d, old terrain %d)" % (len(want), n_near, n_water, n_old))
    wlist = arg("--worlds", "whiterunworld," + WORLD, str).lower().split(",")
    worlds, ltex, txst, land, prio = {}, {}, {}, {}, {}
    for p in PLUGINS:
        read_plugin(os.path.join(DATA, p), lambda c: c in want, worlds, ltex, txst, land, wlist, prio)
        print("read", p, len(land), "LAND", {w: sum(1 for v in prio.values() if v == i) for i, w in enumerate(wlist)})
    os.makedirs(os.path.join(OUT, "tiles"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "tex"), exist_ok=True)

    def paths_of(fid):
        if fid == 0:
            return DEFAULT_TEX, None
        t = txst.get(ltex.get(fid))
        return (t.get(b"TX00"), t.get(b"TX01")) if t and t.get(b"TX00") else (None, None)

    tiles = {}
    for c in land:
        tiles.setdefault((c[0] // T, c[1] // T), []).append(c)
    N = T * 32 + 1
    src = None if "--no-tex" in sys.argv else TexSource()
    tex_ok, meta, used_keys = {}, {}, set()
    jpath = os.path.join(OUT, "tiles.json")
    if os.path.exists(jpath):
        meta = json.load(open(jpath))
    written = []
    for (tx, ty), cells in sorted(tiles.items()):
        name = "LT_%d_%d" % (tx, ty)
        if only and name not in only:
            continue
        H = np.zeros((N, N)); NR = np.zeros((N, N, 3)); CL = np.zeros((N, N, 3)); CNT = np.zeros((N, N))
        present = np.zeros((T, T), bool)
        W = {}
        for gx, gy in cells:
            rec = land[(gx, gy)]
            ix, iy = (gx - tx * T) * 32, (gy - ty * T) * 32
            present[gy - ty * T, gx - tx * T] = True
            sl = (slice(iy, iy + 33), slice(ix, ix + 33))
            H[sl] += rec["h"]; NR[sl] += cell_normals(rec["h"], rec["nrm"])
            CL[sl] += rec["col"] if rec["col"] is not None else 255.0
            CNT[sl] += 1
            for fid, w in cell_weights(rec).items():
                path = paths_of(fid)[0]
                if path is None:                      # LTEX without a texture set: the default dirt
                    fid = 0
                W.setdefault(fid, np.zeros((N, N)))[sl] += w
        m = CNT > 0
        H[m] /= CNT[m]; CL[m] /= CNT[m][:, None]; NR[m] /= CNT[m][:, None]
        NR[m] /= np.linalg.norm(NR[m], axis=1, keepdims=True)
        for k in W: W[k][m] /= CNT[m]
        # layer textures: drop layers whose colour map is missing, keep the MAX_LAYERS heaviest
        order = sorted(W, key=lambda k: -W[k].sum())
        total_w = sum(W[f].sum() for f in W)
        keys, chosen = [], []
        for fid in order:
            if keys and W[fid].sum() < 2e-4 * N * N:            # negligible remainder
                break
            diff, norm = paths_of(fid)
            key = tex_key(diff)
            if key not in tex_ok:
                tex_ok[key] = True if src is None else convert_layer(src, key, diff, norm)
            if tex_ok[key] and key not in keys:
                keys.append(key); chosen.append(fid)
            elif tex_ok[key]:                          # two LTEX with the same texture: merge weights
                W[chosen[keys.index(key)]] = W[chosen[keys.index(key)]] + W[fid]
            if len(keys) == max_layers:
                break
        stack = np.stack([W[f] for f in chosen])
        tot = stack.sum(axis=0)
        stack[0][tot <= 1e-6] = 1.0; tot[tot <= 1e-6] = 1.0
        stack /= tot
        lost = 1.0 - sum(W[f].sum() for f in chosen) / max(total_w, 1e-6)
        used_keys.update(keys)
        for i in range((len(chosen) + 3) // 4):
            img = np.zeros((N, N, 4))
            for c in range(4):
                if i * 4 + c < len(chosen): img[:, :, c] = stack[i * 4 + c]
            px = np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)
            px[:, :, 3] = np.maximum(px[:, :, 3], 1)    # alpha 0 makes Unreal's PNG infill overwrite RGB (layers 0-2)
            Image.fromarray(np.flipud(px), "RGBA").save(os.path.join(OUT, "tex", "LTW_%d_%d_%d.png" % (tx, ty, i)))
        # mesh: vertices of present cells only, triangles per present cell (same diagonal as terrain.obj)
        idx = -np.ones((N, N), np.int64)
        vy, vx = np.nonzero(m)
        idx[vy, vx] = np.arange(len(vy))
        pos = np.stack([tx * T * 4096 + vx * 128.0, ty * T * 4096 + vy * 128.0, H[vy, vx]], axis=1)
        uv0 = np.stack([vx * 128.0 / TEX_UNITS, vy * 128.0 / TEX_UNITS], axis=1)
        uv1 = np.stack([(vx + 0.5) / N, (vy + 0.5) / N], axis=1)
        tris = []
        for cy in range(T):
            for cx in range(T):
                if not present[cy, cx]: continue
                yy, xx = np.meshgrid(np.arange(cy * 32, cy * 32 + 32), np.arange(cx * 32, cx * 32 + 32), indexing="ij")
                a, b, c, d = idx[yy, xx], idx[yy, xx + 1], idx[yy + 1, xx], idx[yy + 1, xx + 1]
                tris.append(np.stack([a, b, d], -1).reshape(-1, 3)); tris.append(np.stack([a, d, c], -1).reshape(-1, 3))
        tris = np.concatenate(tris)
        np.savez(os.path.join(OUT, "tiles", name + ".npz"), pos=pos.astype(np.float64), nrm=NR[vy, vx].astype(np.float32),
                 col=CL[vy, vx].astype(np.uint8), uv0=uv0.astype(np.float32), uv1=uv1.astype(np.float32),
                 tris=tris.astype(np.int32))
        meta[name] = {"cells": sorted([list(c) for c in cells]), "layers": keys, "origin": [tx * T * 4096, ty * T * 4096],
                      "verts": int(len(pos)), "tris": int(len(tris)), "lost_weight": round(float(lost), 4),
                      "zmin": float(H[m].min()), "zmax": float(H[m].max())}
        written.append(os.path.join(OUT, "tiles", name + ".npz"))
        print("%s: %d cells, %d verts, layers %d/%d (%.1f%% weight dropped)" % (name, len(cells), len(pos), len(keys), len(W), lost * 100))
    json.dump(meta, open(jpath, "w"), indent=1)
    missing = sorted(want - set(land))
    print("tiles written %d; cells with LAND %d; wanted cells without LAND %d; layer textures %d (%d missing)"
          % (len(written), len(land), len(missing), len(used_keys), sum(1 for v in tex_ok.values() if not v)))
    if "--lod" in sys.argv:
        trim_lod(set(land))
    if "--no-fbx" not in sys.argv and written:
        for i in range(0, len(written), 40):                     # one Blender at a time, short command lines
            subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.abspath(__file__), "--", "--blender"] + written[i:i + 40],
                           check=False, stdout=subprocess.DEVNULL if "--quiet" in sys.argv else None)
        if "--lod" in sys.argv:
            ld = os.path.join(OUT, "lod")
            subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.abspath(__file__), "--", "--blender-obj", ld, ld], check=False)


def trim_lod(covered):
    """Copy of area2/lod_obj/lodterrain.obj without triangles whose centre lies in a covered cell (lod_terrain.py
    already drops the old terrain's cells; this also drops the water cells the full-resolution terrain now covers)."""
    src = os.path.join(AREA, "lod_obj", "lodterrain.obj")
    ld = os.path.join(OUT, "lod")
    os.makedirs(ld, exist_ok=True)
    verts, uvs, out, kept, dropped = [], [], [], 0, 0
    obj = open(os.path.join(ld, "landlod.obj"), "w")
    obj.write("mtllib landlod.mtl\n")
    for line in open(src):
        if line.startswith("v "):
            v = line.split(); verts.append((float(v[1]), float(v[2]))); obj.write(line)
        elif line.startswith("f "):
            ids = [int(t.split("/")[0]) - 1 for t in line.split()[1:4]]
            mx = sum(verts[i][0] for i in ids) / 3.0; my = sum(verts[i][1] for i in ids) / 3.0
            if (math.floor(mx / 4096), math.floor(my / 4096)) in covered:
                dropped += 1; continue
            kept += 1; obj.write(line)
        elif line.startswith("mtllib"):
            continue
        else:
            obj.write(line)
    obj.close()
    mt = os.path.join(AREA, "lod_obj", "lodterrain.mtl")
    if os.path.exists(mt):
        open(os.path.join(ld, "landlod.mtl"), "w").write(open(mt).read())
    print("landlod.obj: kept %d, dropped %d LOD triangles over full-resolution cells" % (kept, dropped))


if __name__ == "__main__":
    main()
