"""Blender side of tools/grass_placement.py.
  D:\\blender.exe -b --factory-startup -P grass_blender.py -- export <obj_dir> <fbx_dir>
      each grass OBJ (Skyrim units) -> FBX in metres (forward -Y, up Z, like tools/blender_export.py), origin kept at the
      model's root (the base of the grass), one mesh with the material slots of the nif shapes.
  D:\\blender.exe -b --factory-startup -P grass_blender.py -- preview <preview_dir> <obj_dir> <out.png>
      terrain.npz + instances.npz (written by grass_placement.preview) -> rendered PNGs (<out>.png ground level,
      <out>_high.png from above). Instances via geometry nodes; alpha cut-out from the texture alpha."""
import bpy, math, os, sys
import numpy as np

SCALE = 0.014287
argv = sys.argv[sys.argv.index("--") + 1:]


def import_obj(path):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=path, forward_axis='Y', up_axis='Z')
    objs = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def export(obj_dir, fbx_dir):
    os.makedirs(fbx_dir, exist_ok=True)
    for f in sorted(os.listdir(obj_dir)):
        if not f.endswith(".obj"):
            continue
        name = f[:-4]
        dst = os.path.join(fbx_dir, name + ".fbx")
        if os.path.exists(dst) and not os.environ.get("FORCE"):
            continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        o = import_obj(os.path.join(obj_dir, f))
        o.scale = (SCALE, SCALE, SCALE)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        o.name = o.data.name = name
        bpy.ops.export_scene.fbx(filepath=dst, use_selection=True, axis_forward='-Y', axis_up='Z', global_scale=1.0,
                                 apply_unit_scale=True, mesh_smooth_type='FACE')
        print("EXPORTED", name, len(o.data.vertices), "verts", len(o.data.polygons), "faces", len(o.material_slots), "slots")


def grass_material(mat, thr=0.5):
    """Texture colour x instance shade, alpha cut-out, light transmission for the thin blades."""
    nt = mat.node_tree
    img = next((n for n in nt.nodes if n.type == 'TEX_IMAGE'), None)
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if img is None or bsdf is None:
        return
    shade = nt.nodes.new("ShaderNodeAttribute"); shade.attribute_type = 'INSTANCER'; shade.attribute_name = "shade"
    mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
    mul.inputs[0].default_value = 1.0
    nt.links.new(img.outputs["Color"], mul.inputs[6]); nt.links.new(shade.outputs["Fac"], mul.inputs[7])
    nt.links.new(mul.outputs[2], bsdf.inputs["Base Color"])
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = thr
    nt.links.new(img.outputs["Alpha"], gt.inputs[0]); nt.links.new(gt.outputs[0], bsdf.inputs["Alpha"])
    for k, v in (("Roughness", 0.8), ("Specular IOR Level", 0.2)):
        if k in bsdf.inputs: bsdf.inputs[k].default_value = v
    for k in ("Transmission Weight", "Subsurface Weight"):
        if k in bsdf.inputs: bsdf.inputs[k].default_value = 0.15
    try: mat.surface_render_method = 'DITHERED'
    except Exception: pass
    try: mat.blend_method = 'CLIP'
    except Exception: pass


def rotations(n, yaw):
    """XYZ Euler of Align(+Z -> n) @ Rz(yaw), vectorized."""
    nz = np.clip(n[:, 2], -1, 1)
    ax = np.stack([-n[:, 1], n[:, 0], np.zeros(len(n))], 1)
    s = np.linalg.norm(ax, axis=1)
    ax = np.where(s[:, None] > 1e-6, ax / np.maximum(s, 1e-9)[:, None], np.array([1.0, 0, 0]))
    ang = np.arccos(nz)
    K = np.zeros((len(n), 3, 3))
    K[:, 0, 1], K[:, 0, 2], K[:, 1, 0], K[:, 1, 2], K[:, 2, 0], K[:, 2, 1] = -ax[:, 2], ax[:, 1], ax[:, 2], -ax[:, 0], -ax[:, 1], ax[:, 0]
    A = np.eye(3)[None] + np.sin(ang)[:, None, None] * K + (1 - np.cos(ang))[:, None, None] * (K @ K)
    c, sn = np.cos(yaw), np.sin(yaw)
    Z = np.zeros((len(n), 3, 3)); Z[:, 0, 0], Z[:, 0, 1], Z[:, 1, 0], Z[:, 1, 1], Z[:, 2, 2] = c, -sn, sn, c, 1
    R = A @ Z
    return np.stack([np.arctan2(R[:, 2, 1], R[:, 2, 2]), np.arcsin(np.clip(-R[:, 2, 0], -1, 1)),
                     np.arctan2(R[:, 1, 0], R[:, 0, 0])], 1)


def instancer(name, model, data):
    """Point cloud object whose geometry nodes put `model` on every point (rot/scl/shade attributes)."""
    me = bpy.data.meshes.new(name + "_pts")
    me.vertices.add(len(data)); me.vertices.foreach_set("co", data[:, 0:3].ravel())
    nxy = data[:, 6:8].astype(np.float64)
    n = np.concatenate([nxy, np.sqrt(np.clip(1 - (nxy ** 2).sum(1), 0, 1))[:, None]], 1)
    rot = rotations(n, np.radians(data[:, 3].astype(np.float64)))
    scl = np.stack([data[:, 4], data[:, 4], data[:, 5]], 1)
    for an, typ, vals in (("rot", 'FLOAT_VECTOR', rot), ("scl", 'FLOAT_VECTOR', scl), ("shade", 'FLOAT', data[:, 8])):
        at = me.attributes.new(an, typ, 'POINT')
        at.data.foreach_set("vector" if typ == 'FLOAT_VECTOR' else "value", np.asarray(vals, np.float32).ravel())
    ob = bpy.data.objects.new(name + "_pts", me)
    bpy.context.scene.collection.objects.link(ob)
    ng = bpy.data.node_groups.new(name + "_gn", 'GeometryNodeTree')
    ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    inst = N.new("GeometryNodeInstanceOnPoints")
    info = N.new("GeometryNodeObjectInfo"); info.inputs["Object"].default_value = model
    ra = N.new("GeometryNodeInputNamedAttribute"); ra.data_type = 'FLOAT_VECTOR'; ra.inputs["Name"].default_value = "rot"
    sa = N.new("GeometryNodeInputNamedAttribute"); sa.data_type = 'FLOAT_VECTOR'; sa.inputs["Name"].default_value = "scl"
    L.new(gi.outputs[0], inst.inputs["Points"]); L.new(info.outputs["Geometry"], inst.inputs["Instance"])
    if hasattr(bpy.types, "FunctionNodeEulerToRotation"):
        e2r = N.new("FunctionNodeEulerToRotation")
        L.new(ra.outputs["Attribute"], e2r.inputs[0]); L.new(e2r.outputs[0], inst.inputs["Rotation"])
    else:
        L.new(ra.outputs["Attribute"], inst.inputs["Rotation"])
    L.new(sa.outputs["Attribute"], inst.inputs["Scale"])
    L.new(inst.outputs["Instances"], go.inputs[0])
    mod = ob.modifiers.new("grass", 'NODES'); mod.node_group = ng
    return ob


def preview(pdir, obj_dir, out_png):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    t = np.load(os.path.join(pdir, "terrain.npz"))
    me = bpy.data.meshes.new("terrain"); me.from_pydata(t["v"].tolist(), [], t["f"].tolist()); me.update()
    terrain = bpy.data.objects.new("terrain", me); sc.collection.objects.link(terrain)
    tm = bpy.data.materials.new("ground"); tm.use_nodes = True
    nt = tm.node_tree; bsdf = nt.nodes["Principled BSDF"]
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 0.004
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.16, 0.14, 0.08, 1); ramp.color_ramp.elements[1].color = (0.30, 0.26, 0.15, 1)
    nt.links.new(noise.outputs["Fac"], ramp.inputs[0]); nt.links.new(ramp.outputs[0], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.95
    me.materials.append(tm)
    hidden = bpy.data.collections.new("models"); sc.collection.children.link(hidden)
    data = np.load(os.path.join(pdir, "instances.npz"))
    total = 0
    for name in data.files:
        objp = os.path.join(obj_dir, name + ".obj")
        if not os.path.exists(objp):
            print("ERROR no obj for", name); continue
        m = import_obj(objp)
        for c in list(m.users_collection): c.objects.unlink(m)
        hidden.objects.link(m); m.hide_render = True; m.hide_viewport = True
        for slot in m.material_slots:
            if slot.material: grass_material(slot.material)
        instancer(name, m, data[name]); total += len(data[name])
    # camera: 2 m above the terrain at the patch edge, looking across it
    deps = bpy.context.evaluated_depsgraph_get()
    def ground(x, y):
        hit = sc.ray_cast(deps, (x, y, 1e5), (0, 0, -1))
        return hit[1][2] if hit[0] else 0.0
    world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
    sky = world.node_tree.nodes.new("ShaderNodeTexSky")
    try: sky.sky_type = 'NISHITA'
    except Exception: pass
    world.node_tree.links.new(sky.outputs[0], world.node_tree.nodes["Background"].inputs[0])
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.25
    sun = bpy.data.lights.new("sun", 'SUN'); sun.energy = 4.0; sun.angle = math.radians(1.0)
    so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), 0, math.radians(140))
    cam = bpy.data.cameras.new("cam"); cam.lens = 28; cam.clip_start = 5; cam.clip_end = 1e5
    co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try: sc.render.engine = eng; break
        except Exception: pass
    try: sc.eevee.taa_render_samples = 32
    except Exception: pass
    try: sc.view_settings.view_transform = 'AgX'
    except Exception: pass
    shots = [(out_png, (-1300.0, -1300.0), 150.0, (300.0, 300.0), 25.0),
             (out_png[:-4] + "_high.png", (-1700.0, -1700.0), 1300.0, (0.0, 0.0), 0.0)]
    for path, (cx, cy), up, (tx, ty), tup in shots:
        cz = ground(cx, cy) + up; tz = ground(tx, ty) + tup
        co.location = (cx, cy, cz)
        d = np.array([tx - cx, ty - cy, tz - cz]); d /= np.linalg.norm(d)
        co.rotation_euler = (math.pi / 2 + math.asin(d[2]), 0, math.atan2(d[1], d[0]) - math.pi / 2)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("PREVIEW", path, total, "instances,", len(data.files), "models, engine", sc.render.engine)


if argv[0] == "export":
    export(argv[1], argv[2])
elif argv[0] == "preview":
    preview(argv[1], argv[2], argv[3])
