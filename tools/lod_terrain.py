"""Distant terrain backdrop (mountains) from Skyrim's own terrain LOD: meshes\\terrain\\tamriel\\tamriel.<lvl>.<x>.<y>.btr
+ textures\\terrain\\tamriel\\tamriel.<lvl>.<x>.<y>.dds. Level 8 near Whiterun, level 16 elsewhere. Triangles over cells
that the detailed terrain (area2/terrain_obj/terrain.obj) already covers are dropped, and the LOD sits SINK units lower
so the seam hides under the detailed terrain.
Writes area2/lod_obj/lodterrain.obj (+ .mtl) in absolute Skyrim units (same convention as terrain.obj) and
area2/tex/lodtex_<lvl>_<x>_<y>.png. Then: blender_export.py area2/lod_obj area2/export, and import in Unreal.
Usage: python tools/lod_terrain.py"""
import io, math, os, re, struct, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bsa import Bsa
import nif2obj
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
CENTER = (23000.0, -6000.0)          # Whiterun area (Skyrim units), same as the detailed terrain
NEAR_L8 = 110000.0                   # level-16 tiles whose centre is closer use their four level-8 tiles
SINK = 60.0
TEXMAX = 1024

meshes = Bsa(os.path.join(DATA, "Skyrim - Meshes1.bsa"))
texarc = [Bsa(os.path.join(DATA, "Skyrim - Textures7.bsa"))]


def read_tex(path):
    loose = os.path.join(DATA, path)
    if os.path.exists(loose):
        return open(loose, "rb").read()
    for a in texarc:
        if path in a.files:
            return a.read(path)
    return None


near_cells = set()
for line in open(os.path.join(AREA, "terrain_obj", "terrain.obj")):
    m = re.match(r"o terrain_tile_(-?\d+)_(-?\d+)", line)
    if m:
        near_cells.add((int(m.group(1)), int(m.group(2))))

tiles16 = sorted({tuple(map(int, f.split(".")[2:4])) for f in meshes.files
                  if f.startswith("meshes\\terrain\\tamriel\\tamriel.16.") and f.endswith(".btr")})
chosen = []
for x, y in tiles16:
    cx, cy = (x + 8) * 4096, (y + 8) * 4096
    if math.hypot(cx - CENTER[0], cy - CENTER[1]) < NEAR_L8:
        chosen += [(8, x + dx, y + dy) for dx in (0, 8) for dy in (0, 8)]
    else:
        chosen.append((16, x, y))

out_dir = os.path.join(AREA, "lod_obj")
os.makedirs(out_dir, exist_ok=True)
obj = open(os.path.join(out_dir, "lodterrain.obj"), "w")
mtl = open(os.path.join(out_dir, "lodterrain.mtl"), "w")
obj.write("mtllib lodterrain.mtl\n")
tmp = os.path.join(tempfile.gettempdir(), "lod_tile.btr")
off, ntile, ntri = 1, 0, 0
wdir = os.path.join(AREA, "lodwater_obj")
os.makedirs(wdir, exist_ok=True)
wobj = open(os.path.join(wdir, "lodwater.obj"), "w")
open(os.path.join(wdir, "lodwater.mtl"), "w").write("newmtl skywater\nKd 0.1 0.2 0.2\n")
wobj.write("mtllib lodwater.mtl\no lodwater\nusemtl skywater\nvt 0 0\n")
woff, wtri = 1, 0
for lvl, x, y in chosen:
    p = "meshes\\terrain\\tamriel\\tamriel.%d.%d.%d.btr" % (lvl, x, y)
    if p not in meshes.files:
        continue
    open(tmp, "wb").write(meshes.read(p))
    try:
        shapes = nif2obj.extract(tmp)
    except Exception as e:
        print("skip", p, e); continue
    land = [s for s in shapes if s[4]]                             # the textured shape; the untextured one is water
    ox, oy = x * 4096.0, y * 4096.0
    for _, wverts, _, wtris, _ in (s for s in shapes if not s[4]):   # water: whole tile, real height (rivers, lakes)
        for vx, vy, vz in wverts: wobj.write("v %.1f %.1f %.1f\n" % (vx + ox, vy + oy, vz))
        for a, b, c in wtris: wobj.write("f %d/1 %d/1 %d/1\n" % (a + woff, b + woff, c + woff))
        woff += len(wverts); wtri += len(wtris)
    if not land:
        continue
    name, verts, uvs, tris, tex = land[0]
    vw = [(vx + ox, vy + oy, vz - SINK) for vx, vy, vz in verts]
    keep = []
    for a, b, c in tris:
        mx = (vw[a][0] + vw[b][0] + vw[c][0]) / 3.0; my = (vw[a][1] + vw[b][1] + vw[c][1]) / 3.0
        if (math.floor(mx / 4096), math.floor(my / 4096)) not in near_cells:
            keep.append((a, b, c))
    if not keep:
        continue
    key = "lodtex_%d_%d_%d" % (lvl, x, y)
    png = os.path.join(AREA, "tex", key + ".png")
    if not os.path.exists(png):
        raw = read_tex("textures\\terrain\\tamriel\\tamriel.%d.%d.%d.dds" % (lvl, x, y))
        if raw is None:
            print("no texture for", key); continue
        if raw[84:88] == b"DX10":
            f = struct.unpack_from("<I", raw, 128)[0]
            if f in (72, 75, 78, 99):
                raw = raw[:128] + struct.pack("<I", f - 1) + raw[132:]
        im = Image.open(io.BytesIO(raw)); im.load()
        im = im.convert("RGB")
        if max(im.size) > TEXMAX:
            im = im.resize((TEXMAX, TEXMAX), Image.LANCZOS)
        im.save(png)
    mtl.write("newmtl %s\nKd 0.8 0.8 0.8\n" % key)
    obj.write("o %s\nusemtl %s\n" % (key, key))
    for v in vw: obj.write("v %.1f %.1f %.1f\n" % v)
    for u in uvs: obj.write("vt %.5f %.5f\n" % u)
    for a, b, c in keep:
        obj.write("f %d/%d %d/%d %d/%d\n" % (a + off, a + off, b + off, b + off, c + off, c + off))
    off += len(vw); ntile += 1; ntri += len(keep)
obj.close(); mtl.close(); wobj.close()
print("LOD terrain: %d tiles, %d triangles, %d near cells excluded; water %d triangles" % (ntile, ntri, len(near_cells), wtri))
