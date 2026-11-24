"""Blender side of tools/land_textures.py (run by it, or by hand):
  D:\\blender.exe -b --factory-startup -P tools/land_textures_blender.py -- export <tile.npz ...>
  D:\\blender.exe -b --factory-startup -P tools/land_textures_blender.py -- lod <lodterrain_trim.obj> <out_dir>
  D:\\blender.exe -b --factory-startup -P tools/land_textures_blender.py -- preview <out.png> <view> <variant>
     view: overview | ground | river; variant: new (baked LX textures + trimmed LOD) | old (old baked tiles + LOD)
Same conventions as tools/blender_export.py: Skyrim units x 0.014287 = metres, FBX forward -Y, up Z."""
import glob, json, math, os, sys

import bpy
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
OUT = os.path.join(AREA, "landtex")
SCALE = 0.014287


def mesh_from_npz(path, with_images=None):
    d = np.load(path)
    name = os.path.splitext(os.path.basename(path))[0]
    pos, tris = d["pos"].astype(np.float64) * SCALE, d["tris"]
    me = bpy.data.meshes.new(name)
    me.from_pydata(pos.tolist(), [], tris.tolist())
    li = np.zeros(len(me.loops), dtype=np.int32)
    me.loops.foreach_get("vertex_index", li)
    uv = me.uv_layers.new(name="UV0")
    uv.data.foreach_set("uv", d["uv"][li].astype(np.float32).ravel())
    for n in d["names"]:
        me.materials.append(material(str(n), with_images(str(n)) if with_images else None))
    me.polygons.foreach_set("material_index", d["mat"].astype(np.int32))
    me.update()
    try:
        me.normals_split_custom_set_from_vertices(d["nrm"].astype(np.float64).tolist())
    except Exception as e:
        print("custom normals skipped", e)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def material(name, image=None, color=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if image or color:
        m.use_nodes = True
        bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        if image and os.path.exists(image):
            tex = m.node_tree.nodes.new("ShaderNodeTexImage")
            tex.image = bpy.data.images.load(image, check_existing=True)
            tex.interpolation = 'Cubic'
            m.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            m.node_tree.nodes.active = tex
        elif color:
            bsdf.inputs["Base Color"].default_value = color
            m.diffuse_color = color
    return m


def export(paths):
    out_dir = os.path.join(OUT, "fbx")
    os.makedirs(out_dir, exist_ok=True)
    for p in paths:
        name = os.path.splitext(os.path.basename(p))[0]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        ob = mesh_from_npz(p)
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True); bpy.context.view_layer.objects.active = ob
        bpy.ops.export_scene.fbx(filepath=os.path.join(out_dir, name + ".fbx"), use_selection=True, axis_forward='-Y',
                                 axis_up='Z', global_scale=1.0, apply_unit_scale=True, mesh_smooth_type='OFF',
                                 use_tspace=False)
        print("EXPORTED", name, len(ob.data.vertices), "verts", len(ob.data.materials), "materials")


def lod(obj_path, out_dir):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=obj_path, forward_axis='Y', up_axis='Z')
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for o in objs:
        o.scale = (SCALE, SCALE, SCALE)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if len(objs) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    name = os.path.splitext(os.path.basename(obj_path))[0]
    o.name = name; o.data.name = name
    bpy.ops.export_scene.fbx(filepath=os.path.join(out_dir, name + ".fbx"), use_selection=True, axis_forward='-Y',
                             axis_up='Z', global_scale=1.0, apply_unit_scale=True)
    print("EXPORTED", name, len(o.data.polygons), "faces")


# ------------------------------------------------------------------------------------------------------------- preview
VIEWS = {   # (cell rect gx0, gy0, gx1, gy1), camera position / target in Skyrim units (z relative to terrain below)
    "overview": ((0, -6, 10, 2), (2000.0, -30000.0, 16000.0), (24000.0, -5000.0, 0.0)),
    "ground": ((2, -4, 8, 0), (17500.0, -9200.0, 700.0), (24500.0, -5200.0, 0.0)),
    "river": ((2, -7, 9, -2), (14000.0, -24000.0, 6000.0), (22000.0, -15000.0, 0.0)),
}


def lod_region(rect, sink_tex=True, trimmed=False):
    """LOD terrain triangles inside the rect (from the original or the trimmed obj), with its lodtex_* textures."""
    src = os.path.join(OUT, "lod", "lodterrain_trim.obj") if trimmed else os.path.join(AREA, "lod_obj", "lodterrain.obj")
    x0, y0, x1, y1 = rect[0] * 4096, rect[1] * 4096, (rect[2] + 1) * 4096, (rect[3] + 1) * 4096
    v, vt, faces, mat, cur = [], [], {}, None, None
    for line in open(src):
        if line.startswith("v "):
            a = line.split(); v.append((float(a[1]), float(a[2]), float(a[3])))
        elif line.startswith("vt "):
            a = line.split(); vt.append((float(a[1]), float(a[2])))
        elif line.startswith("usemtl"):
            cur = line.split()[1]
        elif line.startswith("f "):
            ids = [tuple(int(x) - 1 for x in t.split("/")[:2]) for t in line.split()[1:4]]
            mx = sum(v[i][0] for i, _ in ids) / 3; my = sum(v[i][1] for i, _ in ids) / 3
            if x0 - 8192 <= mx <= x1 + 8192 and y0 - 8192 <= my <= y1 + 8192:
                faces.setdefault(cur, []).append(ids)
    for key, fl in faces.items():
        used = sorted({i for f in fl for i, _ in f})
        remap = {i: n for n, i in enumerate(used)}
        me = bpy.data.meshes.new(key)
        me.from_pydata([tuple(c * SCALE for c in v[i]) for i in used], [], [[remap[i] for i, _ in f] for f in fl])
        uv = me.uv_layers.new(name="UV0")
        k = 0
        for f in fl:
            for _i, t in f:
                uv.data[k].uv = vt[t]; k += 1
        me.materials.append(material("lod_" + key, os.path.join(AREA, "tex", key + ".png")))
        ob = bpy.data.objects.new("lod_" + key, me)
        bpy.context.scene.collection.objects.link(ob)


def water_region(rect):
    x0, y0, x1, y1 = rect[0] * 4096, rect[1] * 4096, (rect[2] + 1) * 4096, (rect[3] + 1) * 4096
    verts, faces = [], []
    for line in open(os.path.join(AREA, "water_quads.csv")).read().split():
        a, b, n, h = line.split(",")
        a, b, n, h = int(a), int(b), int(n), float(h)
        if not (x0 <= a <= x1 and y0 <= b <= y1):
            continue
        k = len(verts)
        verts += [(a * SCALE, b * SCALE, h * SCALE), ((a + n * 128) * SCALE, b * SCALE, h * SCALE),
                  ((a + n * 128) * SCALE, (b + 128) * SCALE, h * SCALE), (a * SCALE, (b + 128) * SCALE, h * SCALE)]
        faces.append((k, k + 1, k + 2, k + 3))
    if not faces:
        return
    me = bpy.data.meshes.new("water")
    me.from_pydata(verts, [], faces)
    me.materials.append(material("water", color=(0.10, 0.25, 0.45, 1.0)))
    ob = bpy.data.objects.new("water", me)
    bpy.context.scene.collection.objects.link(ob)


def old_tiles(rect):
    """The current Unreal terrain (esm_land_tex.py bake): one 33x33 grid per cell with area2/tex/terrain_tile_* textures
    (512 px thumbnails written by land_textures.py --old-thumbs)."""
    import re
    v, vt, ob_faces, cur = [], [], {}, None
    for line in open(os.path.join(AREA, "terrain_obj", "terrain.obj")):
        if line.startswith("v "):
            a = line.split(); v.append((float(a[1]), float(a[2]), float(a[3])))
        elif line.startswith("vt "):
            a = line.split(); vt.append((float(a[1]), float(a[2])))
        elif line.startswith("o "):
            cur = line.split()[1]
        elif line.startswith("f "):
            ob_faces.setdefault(cur, []).append([tuple(int(x) - 1 for x in t.split("/")[:2]) for t in line.split()[1:4]])
    for name, fl in ob_faces.items():
        m = re.match(r"terrain_tile_(-?\d+)_(-?\d+)", name)
        gx, gy = int(m.group(1)), int(m.group(2))
        if not (rect[0] <= gx <= rect[2] and rect[1] <= gy <= rect[3]):
            continue
        used = sorted({i for f in fl for i, _ in f}); remap = {i: n for n, i in enumerate(used)}
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(c * SCALE for c in v[i]) for i in used], [], [[remap[i] for i, _ in f] for f in fl])
        uv = me.uv_layers.new(name="UV0")
        k = 0
        for f in fl:
            for _i, t in f:
                uv.data[k].uv = vt[t]; k += 1
        for p in me.polygons: p.use_smooth = True
        me.materials.append(material(name, os.path.join(OUT, "preview_old", name + ".jpg")))
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)


def ground_z(x, y):
    for p in glob.glob(os.path.join(OUT, "tiles", "*.npz")):
        d = np.load(p)
        pos = d["pos"]
        dist = (pos[:, 0] - x) ** 2 + (pos[:, 1] - y) ** 2
        i = int(np.argmin(dist))
        if dist[i] < 200 ** 2:
            return float(pos[i, 2])
    return -3000.0


def preview(out, view, variant):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rect, cam_p, cam_t = VIEWS[view]
    meta = json.load(open(os.path.join(OUT, "tiles.json")))
    core = {tuple(c["cell"]) for c in json.load(open(os.path.join(OUT, "cells.json"))).values() if c["core"]}
    if variant == "new":
        prev = lambda n: os.path.join(OUT, "preview", n + ".jpg")
        for name, t in meta.items():
            if any(rect[0] <= c[0] <= rect[2] and rect[1] <= c[1] <= rect[3] for c in t["cells"]):
                mesh_from_npz(os.path.join(OUT, "tiles", name + ".npz"), prev)
        lod_region(rect, trimmed=True)
    else:
        old_tiles(rect)
        lod_region(rect, trimmed=False)
    water_region(rect)
    gz = ground_z(cam_t[0], cam_t[1])
    cz = ground_z(cam_p[0], cam_p[1])
    sc = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    from mathutils import Vector
    cam.location = Vector((cam_p[0], cam_p[1], cz + cam_p[2])) * SCALE
    d = Vector((cam_t[0], cam_t[1], gz)) * SCALE - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 24 if view == "ground" else 35
    cam.data.clip_start = 0.5; cam.data.clip_end = 20000
    sc.camera = cam
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'TEXTURE'
    sc.display.shading.show_shadows = True
    sc.display.shading.show_cavity = False
    sc.render.resolution_x, sc.render.resolution_y = 1400, 800
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("PREVIEW", out)


args = sys.argv[sys.argv.index("--") + 1:]
if args[0] == "export":
    export(args[1:])
elif args[0] == "lod":
    lod(args[1], args[2])
elif args[0] == "preview":
    preview(args[1], args[2], args[3])
