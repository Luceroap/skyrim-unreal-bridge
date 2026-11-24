"""Horizon object LOD from Skyrim's own LOD data (DynDOLOD/xLODGen loose output in Data\\ wins over the BSAs):
  * objects: meshes\\terrain\\tamriel\\objects\\tamriel.<lvl>.<x>.<y>.bto (merged LOD meshes per block, absolute Skyrim
    units). Level 4 near Whiterun, 8 farther, 16 beyond (like tools/lod_terrain.py). Every disconnected piece of a block is
    one object; pieces are dropped when they lie in the detailed-terrain cells (area2/terrain_obj/terrain.obj) or when they
    are the LOD copy of a mountain/cliff/rock/tree the distant layer (area2/distant_refs.json) already draws in full.
  * trees: meshes\\terrain\\tamriel\\trees\\tamriel.lst (billboard types: size + atlas UV rect) + tamriel.4.<x>.<y>.btt
    (instances: x, y, z, rotation, scale, ref form id) with atlas textures\\terrain\\tamriel\\trees\\tamrieltreelod.dds.
    Instances whose form id the distant layer draws as a full tree are skipped.

Outputs (area2/lodobj/):
  obj/lodobj_<lvl>_<x>_<y>.obj/.mtl  one mesh per block, Skyrim units, slots named lodobj_<texture stem>
  obj/lodtree_card.obj               crossed card, 100 x 100 cm in Unreal, pivot at the bottom centre
  export/*.fbx                       blender_export.py (one Blender process, incremental)
  tex/<key>.png                      colour maps (atlases), <= --texmax
  manifest.json                      blocks (bounds, triangles, slots), textures (masked or not)
  trees.json                         {atlas, types: {idx: [w, h, u0, v0, u1, v1]}, instances: [[x, y, z, rot, scale, type]]}
Usage: python tools/lod_objects.py [--radius 700000] [--l4 60000] [--l8 150000] [--texmax 2048] [--no-blender]
                                   [--trees-only | --objects-only] [--keep-near]"""
import argparse, glob, io, json, math, os, re, struct, subprocess, sys, tempfile
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bsa import Bsa
import nif2obj
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
OUT = os.path.join(AREA, "lodobj")
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
BLENDER = r"D:\blender.exe"
CENTER = (23000.0, -6000.0)                 # Whiterun area, same as the terrain tools
CELL = 4096.0
CARD = 100.0 / 1.4287                       # card edge in Skyrim units = 100 cm in Unreal
DISTANT_KINDS = {"mountain", "cliff", "rock", "tree"}

_arcs = {}


def arc(name):
    if name not in _arcs:
        p = os.path.join(DATA, name)
        _arcs[name] = Bsa(p) if os.path.exists(p) else None
    return _arcs[name]


MESH_BSAS = ["Skyrim - Meshes1.bsa", "Skyrim - Meshes0.bsa"]
TEX_BSAS = ["Skyrim - Textures7.bsa"] + ["Skyrim - Textures%d.bsa" % i for i in (0, 1, 2, 3, 4, 5, 6, 8)]


def read_data(rel, bsas):
    """Loose file first (DynDOLOD/xLODGen output), then the archives."""
    loose = os.path.join(DATA, rel)
    if os.path.exists(loose):
        return open(loose, "rb").read()
    for n in bsas:
        a = arc(n)
        if a and rel.lower() in a.files:
            return a.read(rel)
    return None


def list_lod(sub, ext):
    """Lower-case file names under meshes\\terrain\\tamriel\\<sub> from loose files + vanilla archives."""
    names = set()
    d = os.path.join(DATA, "meshes", "terrain", "tamriel", sub)
    if os.path.isdir(d):
        names |= {f.lower() for f in os.listdir(d) if f.lower().endswith(ext)}
    pre = "meshes\\terrain\\tamriel\\%s\\" % sub
    for n in MESH_BSAS:
        a = arc(n)
        if a:
            names |= {p[len(pre):] for p in a.files if p.startswith(pre) and p.endswith(ext)}
    return names


def near_cells():
    s = set()
    p = os.path.join(AREA, "terrain_obj", "terrain.obj")
    if os.path.exists(p):
        for line in open(p):
            m = re.match(r"o terrain_tile_(-?\d+)_(-?\d+)", line)
            if m:
                s.add((int(m.group(1)), int(m.group(2))))
    return s


def distant_refs():
    p = os.path.join(AREA, "distant_refs.json")
    return [it for it in json.load(open(p)) if it["kind"] in DISTANT_KINDS] if os.path.exists(p) else []


# ------------------------------------------------------------------ textures
def dds_to_png(raw, png, texmax, alpha):
    if raw[84:88] == b"DX10":                                    # PIL wants the non-sRGB BCn formats
        f = struct.unpack_from("<I", raw, 128)[0]
        if f in (72, 75, 78, 99):
            raw = raw[:128] + struct.pack("<I", f - 1) + raw[132:]
    im = Image.open(io.BytesIO(raw)); im.load()
    im = im.convert("RGBA" if alpha else "RGB")
    if max(im.size) > texmax:
        k = texmax / float(max(im.size))
        im = im.resize((max(1, int(im.size[0] * k)), max(1, int(im.size[1] * k))), Image.LANCZOS)
    im.save(png)


def tex_key(path):
    stem = os.path.splitext(os.path.basename(path.replace("\\", "/")))[0].lower()
    return "lodobj_" + re.sub(r"[^a-z0-9_]", "_", stem)


def make_texture(rel, key, texmax, masked_names):
    """rel = textures\\...\\x.dds. Returns {masked} or None when no colour map was found."""
    stem = os.path.splitext(os.path.basename(rel))[0].lower()
    masked = "alpha" in stem or stem in masked_names
    png = os.path.join(OUT, "tex", key + ".png")
    if os.path.exists(png):
        return {"masked": masked, "src": rel}
    raw = read_data(rel, TEX_BSAS)
    if raw is not None:
        try:
            dds_to_png(raw, png, texmax, masked)
            return {"masked": masked, "src": rel}
        except Exception as e:
            print("texture failed", rel, e)
    have = os.path.join(AREA, "tex", stem + ".png")              # colour map the asset service already converted
    if os.path.exists(have):
        im = Image.open(have); im = im.convert("RGBA" if masked else "RGB")
        if max(im.size) > texmax:
            im = im.resize((texmax, texmax), Image.LANCZOS)
        im.save(png)
        return {"masked": masked, "src": have}
    print("no texture for", rel)
    return None


# ------------------------------------------------------------------ objects
def pieces(verts, tris):
    """Split triangles into connected pieces (shared vertex indices). Returns lists of triangle indices."""
    parent = list(range(len(verts)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for a, b, c in tris:
        ra, rb, rc = find(a), find(b), find(c)
        if ra != rb: parent[rb] = ra
        if ra != rc: parent[find(rc)] = find(ra)
    groups = defaultdict(list)
    for i, (a, _, _) in enumerate(tris):
        groups[find(a)].append(i)
    return list(groups.values())


def choose_blocks(l4, l8, radius):
    have = list_lod("objects", ".bto")
    avail = defaultdict(set)
    for f in have:
        p = f.split(".")
        if len(p) == 5:
            avail[int(p[1])].add((int(p[2]), int(p[3])))
    out = []

    def dist(lvl, x, y):                                         # Whiterun centre to the nearest point of the block
        x0, y0 = x * CELL, y * CELL; s = lvl * CELL
        dx = max(x0 - CENTER[0], 0, CENTER[0] - (x0 + s)); dy = max(y0 - CENTER[1], 0, CENTER[1] - (y0 + s))
        return math.hypot(dx, dy)

    def visit(lvl, x, y):
        if dist(lvl, x, y) > radius:
            return
        cx, cy = (x + lvl / 2.0) * CELL, (y + lvl / 2.0) * CELL
        d = math.hypot(cx - CENTER[0], cy - CENTER[1])
        sub = lvl // 2
        if lvl > 4 and d < (l8 if lvl == 16 else l4) and any((x + dx, y + dy) in avail[sub] for dx in (0, sub) for dy in (0, sub)):
            for dx in (0, sub):
                for dy in (0, sub):
                    visit(sub, x + dx, y + dy)
        elif (x, y) in avail[lvl]:
            out.append((lvl, x, y))
    for x, y in sorted(avail[16]):
        visit(16, x, y)
    return out


class DistantSurface:
    """Surface samples (vertices, triangle centroids, edge midpoints) of every model the distant layer draws, from the
    asset service's OBJs (area2/obj/<model>.obj, model space). A LOD piece whose vertices mostly fall into voxels these
    samples occupy (VOX units, dilated by one voxel) is the LOD copy of a full model that is already drawn."""
    VOX = 128.0

    def __init__(self, refs):
        self.geo, self.refs = {}, []
        for m in {it["model"] for it in refs}:
            p = os.path.join(AREA, "obj", m + ".obj")
            if not os.path.exists(p):
                continue
            vs, fs = [], []
            for line in open(p):
                if line.startswith("v "):
                    vs.append([float(t) for t in line.split()[1:4]])
                elif line.startswith("f "):
                    fs.append([int(t.split("/")[0]) - 1 for t in line.split()[1:4]])
            if not vs:
                continue
            V = np.array(vs)
            S = [V]
            if fs:
                F = np.array(fs); a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
                S += [(a + b + c) / 3, (a + b) / 2, (b + c) / 2, (a + c) / 2]
            S = np.concatenate(S)
            self.geo[m] = (S, float(np.sqrt((S ** 2).sum(1)).max()))
        for it in refs:
            if it["model"] in self.geo:
                self.refs.append((it, self.geo[it["model"]][1] * it["scale"]))

    @staticmethod
    def enc(k):
        k = k + (1 << 20)
        return (k[:, 0] << 42) | (k[:, 1] << 21) | k[:, 2]

    def occupied(self, x0, y0, x1, y1):
        keys = []
        for it, rad in self.refs:
            px, py, _ = it["pos"]
            if px + rad < x0 or px - rad > x1 or py + rad < y0 or py - rad > y1:
                continue
            S = self.geo[it["model"]][0]
            W = S @ np.array(it["rot"]).reshape(3, 3).T * it["scale"] + np.array(it["pos"])
            m = (W[:, 0] > x0) & (W[:, 0] < x1) & (W[:, 1] > y0) & (W[:, 1] < y1)
            if m.any():
                keys.append(np.unique(np.floor(W[m] / self.VOX).astype(np.int64), axis=0))
        if not keys:
            return np.zeros(0, np.int64)
        K = np.unique(np.concatenate(keys), axis=0)
        return np.unique(np.concatenate([self.enc(K + np.array([dx, dy, dz]))
                                         for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)]))

    def inside(self, occ, verts):
        if not len(occ):
            return np.zeros(len(verts), bool)
        return np.isin(self.enc(np.floor(np.array(verts) / self.VOX).astype(np.int64)), occ)


def convert_objects(args, near, refs, masked_names):
    os.makedirs(os.path.join(OUT, "obj"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "tex"), exist_ok=True)
    surf = DistantSurface(refs)
    print("distant-layer surfaces: %d models, %d refs" % (len(surf.geo), len(surf.refs)))
    blocks = choose_blocks(args.l4, args.l8, args.radius)
    print("blocks:", Counter(b[0] for b in blocks))
    tmp = os.path.join(tempfile.gettempdir(), "lodobj_block.bto")
    manifest, textures = [], {}
    st = Counter()
    for lvl, x, y in blocks:
        raw = read_data("meshes\\terrain\\tamriel\\objects\\tamriel.%d.%d.%d.bto" % (lvl, x, y), MESH_BSAS)
        if raw is None:
            continue
        open(tmp, "wb").write(raw)
        try:
            shapes = nif2obj.extract(tmp)
        except Exception as e:
            print("skip block", lvl, x, y, e); continue
        occ = surf.occupied(x * CELL - 2048, y * CELL - 2048, (x + lvl) * CELL + 2048, (y + lvl) * CELL + 2048)
        keep = defaultdict(list)                                 # shape -> triangle ids
        for si, (_, verts, _, tris, tex) in enumerate(shapes):
            if tex and "\\roads\\" in tex.lower():
                continue                                         # road strips: baked into the terrain LOD textures already
            hit = surf.inside(occ, verts)
            for g in pieces(verts, tris):
                st["pieces"] += 1
                vs = sorted({i for t in g for i in tris[t]})
                cx = sum(verts[i][0] for i in vs) / len(vs); cy = sum(verts[i][1] for i in vs) / len(vs)
                if not args.keep_near and (math.floor(cx / CELL), math.floor(cy / CELL)) in near:
                    st["near"] += 1; continue                    # detailed cells: real objects / city layer there
                if hit[vs].mean() > 0.8:
                    st["distant"] += 1; st["distant_tris"] += len(g); continue
                keep[si] += g
        name = "lodobj_%d_%d_%d" % (lvl, x, y)
        objp = os.path.join(OUT, "obj", name + ".obj")
        if not keep:
            for ext in (".obj", ".mtl"):
                if os.path.exists(objp[:-4] + ext): os.remove(objp[:-4] + ext)
            continue
        slots, ntri, off = set(), 0, 1
        lo, hi = [1e18] * 3, [-1e18] * 3
        with open(objp, "w") as f, open(objp[:-4] + ".mtl", "w") as m:
            f.write("mtllib %s.mtl\n" % name)
            for si, tids in sorted(keep.items()):
                sname, verts, uvs, tris, tex = shapes[si]
                rel = re.sub(r"^data\\", "", (tex or "").replace("/", "\\").lower())
                key = tex_key(rel) if rel else "lodobj_none"
                if key not in textures and rel:
                    t = make_texture(rel, key, args.texmax, masked_names)
                    textures[key] = t
                if not textures.get(key):
                    key = "lodobj_none"
                if key not in slots:
                    m.write("newmtl %s\nKd 0.6 0.6 0.6\n" % key); slots.add(key)
                used = sorted({i for t in tids for i in tris[t]})
                remap = {v: k for k, v in enumerate(used)}
                f.write("o %s_%d\nusemtl %s\n" % (sname or "obj", si, key))
                for i in used:
                    v = verts[i]
                    for k in range(3):
                        lo[k] = min(lo[k], v[k]); hi[k] = max(hi[k], v[k])
                    f.write("v %.1f %.1f %.1f\n" % v)
                for i in used: f.write("vt %.5f %.5f\n" % uvs[i])
                for t in tids:
                    a, b, c = (remap[i] + off for i in tris[t])
                    f.write("f %d/%d %d/%d %d/%d\n" % (a, a, b, b, c, c))
                off += len(used); ntri += len(tids)
        manifest.append({"name": name, "lvl": lvl, "x": x, "y": y, "min": [round(v) for v in lo], "max": [round(v) for v in hi],
                         "tris": ntri, "slots": sorted(slots)})
        st["tris"] += ntri
        print("%s: %d tris, %d slots" % (name, ntri, len(slots)))
    tex_out = {k: v for k, v in textures.items() if v}
    print("objects: %d blocks, %d triangles kept; %d pieces, %d in detailed cells, %d (%d tris) drawn in full by the "
          "distant layer" % (len(manifest), st["tris"], st["pieces"], st["near"], st["distant"], st["distant_tris"]))
    return manifest, tex_out


# ------------------------------------------------------------------ trees
def convert_trees(args, near, refs):
    raw = read_data("meshes\\terrain\\tamriel\\trees\\tamriel.lst", MESH_BSAS)
    if raw is None:
        print("no tamriel.lst"); return None
    n, = struct.unpack_from("<i", raw)
    types = {}
    for i in range(n):
        idx, w, h, u0, v0, u1, v1, _ = struct.unpack_from("<i6fI", raw, 4 + i * 32)
        types[idx] = [round(w, 2), round(h, 2), u0, v0, u1, v1]
    full = {it["id"] for it in refs if it["kind"] == "tree"}
    inst, st = [], Counter()
    for f in sorted(list_lod("trees", ".btt")):
        b = read_data("meshes\\terrain\\tamriel\\trees\\" + f, MESH_BSAS)
        if not b:
            continue
        nt, = struct.unpack_from("<i", b); p = 4
        for _ in range(nt):
            ti, c = struct.unpack_from("<ii", b, p); p += 8
            for _ in range(c):
                x, y, z, r, s, fid = struct.unpack_from("<5fI", b, p); p += 32
                st["all"] += 1
                if fid in full:
                    st["distant"] += 1; continue
                if not args.keep_near and (math.floor(x / CELL), math.floor(y / CELL)) in near:
                    st["near"] += 1; continue
                if math.hypot(x - CENTER[0], y - CENTER[1]) > args.radius or ti not in types:
                    st["out"] += 1; continue
                inst.append([round(x, 1), round(y, 1), round(z, 1), round(r, 3), round(s, 3), ti])
    os.makedirs(os.path.join(OUT, "tex"), exist_ok=True)
    png = os.path.join(OUT, "tex", "lodtree_atlas.png")
    rel = "textures\\terrain\\tamriel\\trees\\tamrieltreelod.dds"
    if not os.path.exists(png):
        a = read_data(rel, TEX_BSAS)
        if a is None:
            print("no tree atlas"); return None
        dds_to_png(a, png, max(args.texmax, 4096), True)
    used = Counter(i[5] for i in inst)
    out = {"atlas": "lodtree_atlas", "src": rel, "types": {str(k): v for k, v in types.items() if k in used},
           "instances": inst}
    json.dump(out, open(os.path.join(OUT, "trees.json"), "w"))
    print("trees: %d billboards kept of %d (%d drawn in full by the distant layer, %d in detailed cells, %d outside radius); "
          "%d types" % (len(inst), st["all"], st["distant"], st["near"], st["out"], len(used)))
    return out


def write_card():
    """Two crossed quads, CARD units wide/high, bottom centre at the origin; OBJ v is flipped like nif2obj (v = 1 - v_dds)."""
    h, s = CARD, CARD / 2
    q = [[(-s, 0, 0), (s, 0, 0), (s, 0, h), (-s, 0, h)], [(0, -s, 0), (0, s, 0), (0, s, h), (0, -s, h)]]
    with open(os.path.join(OUT, "obj", "lodtree_card.obj"), "w") as f, open(os.path.join(OUT, "obj", "lodtree_card.mtl"), "w") as m:
        m.write("newmtl lodtree_card\nKd 0.5 0.6 0.4\n")
        f.write("mtllib lodtree_card.mtl\no lodtree_card\nusemtl lodtree_card\n")
        for quad in q:
            for v in quad: f.write("v %.4f %.4f %.4f\n" % v)
        for uv in ((0, 0), (1, 0), (1, 1), (0, 1)): f.write("vt %d %d\n" % uv)
        for k in (0, 4):
            f.write("f %d/1 %d/2 %d/3\nf %d/1 %d/3 %d/4\n" % (k + 1, k + 2, k + 3, k + 1, k + 3, k + 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--radius", type=float, default=700000.0, help="Skyrim units from Whiterun (700000 ~ 10 km)")
    ap.add_argument("--l4", type=float, default=60000.0, help="level-8 blocks whose centre is closer use level 4")
    ap.add_argument("--l8", type=float, default=150000.0, help="level-16 blocks whose centre is closer use level 8")
    ap.add_argument("--texmax", type=int, default=2048)
    ap.add_argument("--no-blender", action="store_true")
    ap.add_argument("--trees-only", action="store_true")
    ap.add_argument("--objects-only", action="store_true")
    ap.add_argument("--keep-near", action="store_true", help="keep LOD pieces inside the detailed-terrain cells")
    args = ap.parse_args()
    os.makedirs(os.path.join(OUT, "obj"), exist_ok=True)
    near, refs = near_cells(), distant_refs()
    print("detailed cells %d, distant-layer refs %d" % (len(near), len(refs)))
    masked = set()
    for fn in ("alpha_masked.txt", "alpha_masked_extra.txt"):
        p = os.path.join(AREA, "tex", fn)
        if os.path.exists(p): masked |= set(open(p).read().split())
    mpath = os.path.join(OUT, "manifest.json")
    man = json.load(open(mpath)) if os.path.exists(mpath) else {"blocks": [], "textures": {}}
    if not args.trees_only:
        blocks, tex = convert_objects(args, near, refs, masked)
        man = {"blocks": blocks, "textures": tex, "args": vars(args)}
    if not args.objects_only:
        convert_trees(args, near, refs)
        write_card()
    json.dump(man, open(mpath, "w"), indent=0)
    if not args.no_blender:
        exp = os.path.join(OUT, "export")
        stale = {os.path.splitext(f)[0] for f in os.listdir(exp)} if os.path.isdir(exp) else set()
        want = {b["name"] for b in man["blocks"]} | {"lodtree_card"}
        for n in stale - want:                                   # blocks no longer produced
            os.remove(os.path.join(exp, n + ".fbx"))
        env = dict(os.environ, FORCE="1") if not args.trees_only else dict(os.environ)
        subprocess.run([BLENDER, "-b", "-P", os.path.join(ROOT, "tools", "blender_export.py"), "--",
                        os.path.join(OUT, "obj"), exp], env=env, stdout=subprocess.DEVNULL, check=False)
        print("fbx:", len(glob.glob(os.path.join(exp, "*.fbx"))))


if __name__ == "__main__":
    main()
