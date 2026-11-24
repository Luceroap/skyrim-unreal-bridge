"""Offline check of the horizon layer: Blender render from Whiterun toward the horizon with the terrain LOD
(area2/lod_obj/lodterrain.obj + detailed area2/terrain_obj/terrain.obj + area2/lodwater_obj) and the objlod sub-agent's
object/tree LOD (area2/lodobj/: obj/lodobj_*.obj, manifest.json, trees.json, tex/). Read-only on all of those.

One Blender process per view, loading only the blocks/trees inside that view's wedge with small texture copies, so RAM
stays well under 1 GB per process (the editor + Skyrim use most of the machine). Waits for free commit before starting.
Tree billboards face the camera like Skyrim's do.

Outputs area2/lodpreview/<view>.png (with LOD) and <view>_terrain.png (terrain only, for comparison).
Usage: python tools/lod_horizon_preview.py [--views N,E,S,W] [--res 1600x640] [--fov 90] [--tex 1024] [--height 2500]
"""
import argparse, ctypes, json, math, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
LODOBJ = os.path.join(AREA, "lodobj")
OUT = os.path.join(AREA, "lodpreview")
BLENDER = r"D:\blender.exe"
CENTER = (23000.0, -6000.0)                 # Whiterun, same as the LOD tools
CELL = 4096.0
M = 0.014287                                # Skyrim unit -> metre (Blender unit)
YAW = {"N": 0.0, "E": 90.0, "S": 180.0, "W": 270.0, "NE": 45.0, "SE": 135.0, "SW": 225.0, "NW": 315.0}


def free_commit_gb():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + \
                   [(n, ctypes.c_ulonglong) for n in ("tp", "ap", "tpf", "apf", "tv", "av", "aev")]
    s = MS(); s.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
    return min(s.ap, s.apf) / 2.0 ** 30


def in_wedge(x, y, yaw, half, rmin=0.0):
    dx, dy = x - CENTER[0], y - CENTER[1]
    d = math.hypot(dx, dy)
    if d < rmin:
        return False
    a = math.degrees(math.atan2(dx, dy)) % 360.0                 # 0 = +Y (north), 90 = +X (east)
    return abs((a - yaw + 180.0) % 360.0 - 180.0) <= half


def box_in_wedge(lo, hi, yaw, half):
    return any(in_wedge(x, y, yaw, half) for x in (lo[0], hi[0], (lo[0] + hi[0]) / 2) for y in (lo[1], hi[1], (lo[1] + hi[1]) / 2))


def ground_z():
    """Highest detailed-terrain vertex within 4000 units of the centre (Whiterun's hill top)."""
    best = None
    for line in open(os.path.join(AREA, "terrain_obj", "terrain.obj")):
        if line.startswith("v "):
            x, y, z = map(float, line.split()[1:4])
            if abs(x - CENTER[0]) < 4000 and abs(y - CENTER[1]) < 4000:
                best = z if best is None else max(best, z)
    return best or 0.0


def small_tex(src, dst, size):
    from PIL import Image
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return
    im = Image.open(src)
    if max(im.size) > size:
        k = size / float(max(im.size))
        im = im.resize((max(1, int(im.size[0] * k)), max(1, int(im.size[1] * k))), Image.LANCZOS)
    im.save(dst)


def prepare(view, args, man, trees, gz):
    yaw, half = YAW[view], args.fov / 2.0 + 8.0
    tdir = os.path.join(OUT, "tex"); os.makedirs(tdir, exist_ok=True)
    blocks = [b for b in man.get("blocks", []) if box_in_wedge(b["min"], b["max"], yaw, half)
              and os.path.exists(os.path.join(LODOBJ, "obj", b["name"] + ".obj"))]
    tex, masked = {}, {}
    for b in blocks:
        for k in b["slots"]:
            src = os.path.join(LODOBJ, "tex", k + ".png")
            if os.path.exists(src):
                small_tex(src, os.path.join(tdir, k + ".png"), args.tex); tex[k] = os.path.join(tdir, k + ".png")
                masked[k] = bool(man.get("textures", {}).get(k, {}).get("masked"))
    for line in open(os.path.join(AREA, "lod_obj", "lodterrain.mtl")):
        if line.startswith("newmtl "):
            k = line.split()[1]; src = os.path.join(AREA, "tex", k + ".png")
            if os.path.exists(src):
                small_tex(src, os.path.join(tdir, k + ".png"), args.tex); tex[k] = os.path.join(tdir, k + ".png")
    for line in open(os.path.join(AREA, "terrain_obj", "terrain.mtl")):
        if line.startswith("newmtl "):
            k = line.split()[1]; src = os.path.join(AREA, "tex", k + ".png")
            if os.path.exists(src):
                small_tex(src, os.path.join(tdir, k + ".png"), 512); tex[k] = os.path.join(tdir, k + ".png")
    tr = None
    if trees and os.path.exists(os.path.join(LODOBJ, "tex", trees["atlas"] + ".png")):
        a = trees["atlas"]
        small_tex(os.path.join(LODOBJ, "tex", a + ".png"), os.path.join(tdir, a + ".png"), max(args.tex, 2048))
        tex[a] = os.path.join(tdir, a + ".png"); masked[a] = True
        inst = [i for i in trees["instances"] if in_wedge(i[0], i[1], yaw, half)]
        tr = {"atlas": a, "types": trees["types"], "instances": inst}
    job = {
        "view": view, "yaw": yaw, "fov": args.fov, "res": args.res, "m": M,
        "cam": [CENTER[0] * M, CENTER[1] * M, (gz + args.height) * M], "pitch": args.pitch,
        "terrain": [os.path.join(AREA, "lod_obj", "lodterrain.obj"), os.path.join(AREA, "terrain_obj", "terrain.obj")],
        "water": os.path.join(AREA, "lodwater_obj", "lodwater.obj"),
        "objects": [os.path.join(LODOBJ, "obj", b["name"] + ".obj") for b in blocks],
        "trees": tr, "tex": tex, "masked": masked,
        "out": os.path.join(OUT, view + ".png"), "out_terrain": os.path.join(OUT, view + "_terrain.png"),
    }
    p = os.path.join(OUT, "job_%s.json" % view)
    json.dump(job, open(p, "w"))
    ntri = sum(b["tris"] for b in blocks)
    print("%s: %d blocks (%d tris), %d trees" % (view, len(blocks), ntri, len(tr["instances"]) if tr else 0))
    return p


def run_outside():
    ap = argparse.ArgumentParser()
    ap.add_argument("--views", default="N,E,S,W")
    ap.add_argument("--res", default="1600x640")
    ap.add_argument("--fov", type=float, default=90.0, help="horizontal, degrees")
    ap.add_argument("--tex", type=int, default=1024)
    ap.add_argument("--height", type=float, default=1500.0, help="camera above Whiterun's hill top, Skyrim units")
    ap.add_argument("--pitch", type=float, default=-2.0)
    ap.add_argument("--min-commit", type=float, default=1.5, help="GB of free commit needed before each Blender run")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    man = json.load(open(os.path.join(LODOBJ, "manifest.json"))) if os.path.exists(os.path.join(LODOBJ, "manifest.json")) else {}
    trees = json.load(open(os.path.join(LODOBJ, "trees.json"))) if os.path.exists(os.path.join(LODOBJ, "trees.json")) else None
    gz = ground_z()
    print("camera ground z %.0f" % gz)
    for view in args.views.split(","):
        job = prepare(view.strip().upper(), args, man, trees, gz)
        t0 = time.time()
        while free_commit_gb() < args.min_commit:
            if time.time() - t0 > 900:
                sys.exit("not enough free memory (%.1f GB commit free); try later" % free_commit_gb())
            print("waiting for memory: %.2f GB commit free" % free_commit_gb()); time.sleep(20)
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.abspath(__file__), "--", job],
                           capture_output=True, text=True)
        for line in (r.stdout + r.stderr).splitlines():
            if line.startswith(("PREVIEW", "Error", "Traceback")) or "Error:" in line:
                print("  " + line)


# ------------------------------------------------------------------ inside Blender
def tex_material(bpy, name, path, masked):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Roughness"].default_value = 0.9
    if "Specular IOR Level" in bs.inputs:
        bs.inputs["Specular IOR Level"].default_value = 0.2
    nt.links.new(bs.outputs[0], out.inputs[0])
    if path:
        im = nt.nodes.new("ShaderNodeTexImage")
        im.image = bpy.data.images.load(path, check_existing=True)
        nt.links.new(im.outputs["Color"], bs.inputs["Base Color"])
        if masked:
            mt = nt.nodes.new("ShaderNodeMath"); mt.operation = "GREATER_THAN"; mt.inputs[1].default_value = 0.4
            nt.links.new(im.outputs["Alpha"], mt.inputs[0]); nt.links.new(mt.outputs[0], bs.inputs["Alpha"])
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = "DITHERED"
    return mat


def run_inside(job_path):
    import bpy
    job = json.load(open(job_path))
    m = job["m"]
    sc = bpy.context.scene
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    cols = {}
    for cn in ("terrain", "lod"):
        c = bpy.data.collections.new(cn); sc.collection.children.link(c); cols[cn] = c

    def imp(path, col):
        before = set(bpy.data.objects)
        try:
            bpy.ops.wm.obj_import(filepath=path, global_scale=m, forward_axis="Y", up_axis="Z")
        except RuntimeError as e:
            print("PREVIEW skipped", path, str(e)[:80])
            return
        for o in set(bpy.data.objects) - before:
            for c in o.users_collection: c.objects.unlink(o)
            col.objects.link(o)
    for p in job["terrain"]:
        if os.path.exists(p): imp(p, cols["terrain"])
    if os.path.exists(job["water"]):
        imp(job["water"], cols["terrain"])
    for p in job["objects"]:
        imp(p, cols["lod"])
    for mat in list(bpy.data.materials):
        if mat.name.startswith("skywater"):
            mat.use_nodes = True; bs = mat.node_tree.nodes.get("Principled BSDF")
            if bs:
                bs.inputs["Base Color"].default_value = (0.05, 0.12, 0.16, 1); bs.inputs["Roughness"].default_value = 0.1
            continue
        key = mat.name.split(".")[0]
        tex_material(bpy, mat.name, job["tex"].get(key), job["masked"].get(key, False))

    cx, cy, cz = job["cam"]
    tr = job["trees"]
    if tr and tr["instances"]:
        verts, faces, uvs = [], [], []
        for x, y, z, rot, s, ti in tr["instances"]:
            w, h, u0, v0, u1, v1 = tr["types"][str(ti)]
            x, y, z = x * m, y * m, z * m
            w, h = w * s * m, h * s * m
            dx, dy = cx - x, cy - y; d = math.hypot(dx, dy) or 1.0
            ex, ey = -dy / d * w / 2, dx / d * w / 2                 # card faces the camera
            k = len(verts)
            verts += [(x - ex, y - ey, z), (x + ex, y + ey, z), (x + ex, y + ey, z + h), (x - ex, y - ey, z + h)]
            faces.append((k, k + 1, k + 2, k + 3))
            uvs += [(u0, 1 - v1), (u1, 1 - v1), (u1, 1 - v0), (u0, 1 - v0)]
        me = bpy.data.meshes.new("lodtrees"); me.from_pydata(verts, [], faces)
        uvl = me.uv_layers.new(name="UVMap")
        for i, uv in enumerate(uvs):
            uvl.data[i].uv = uv
        ob = bpy.data.objects.new("lodtrees", me); cols["lod"].objects.link(ob)
        me.materials.append(tex_material(bpy, "lodtrees", job["tex"].get(tr["atlas"]), True))

    cam = bpy.data.cameras.new("cam"); cam.lens_unit = "FOV"; cam.sensor_fit = "HORIZONTAL"
    cam.angle = math.radians(job["fov"]); cam.clip_start = 1.0; cam.clip_end = 15000.0
    co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
    co.location = (cx, cy, cz)
    co.rotation_euler = (math.radians(90 + job["pitch"]), 0.0, math.radians(-job["yaw"]))
    sc.camera = co
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.0; sun.angle = math.radians(0.53)
    so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(55), 0.0, math.radians(-job["yaw"] + 140))
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.42, 0.58, 0.82, 1); bg.inputs[1].default_value = 1.0
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng; break
        except TypeError:
            pass
    rx, ry = map(int, job["res"].lower().split("x"))
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = rx, ry, 100
    try:
        sc.eevee.taa_render_samples = 16
    except AttributeError:
        pass
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = job["out"]
    bpy.ops.render.render(write_still=True)
    print("PREVIEW", job["out"], "objects:", len(cols["lod"].objects))
    cols["lod"].hide_render = True
    sc.render.filepath = job["out_terrain"]
    bpy.ops.render.render(write_still=True)
    print("PREVIEW", job["out_terrain"])


if __name__ == "__main__":
    if "bpy" in sys.modules or os.path.basename(sys.executable).lower().startswith("blender"):
        run_inside(sys.argv[sys.argv.index("--") + 1])
    else:
        run_outside()
