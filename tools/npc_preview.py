"""Render a quick preview PNG of a character FBX (Blender, workbench).  D:\\blender.exe -b -P npc_preview.py -- in.fbx out.png"""
import bpy, sys, math, os
from mathutils import Vector

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
ctr = (lo + hi) / 2
size = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z)
print("bbox", tuple(round(v, 2) for v in lo), tuple(round(v, 2) for v in hi))

# load the converted textures onto materials by slot name (…_<key>_dds)
tex_dir = r"C:\Users\Aidan\SkyrimUnrealBridge\area2\tex"
npc_tex = r"C:\Users\Aidan\SkyrimUnrealBridge\area2\npc\tex"
for o in meshes:
    for slot in o.material_slots:
        m = slot.material
        if not m:
            continue
        nm = m.name.lower().split(".0")[0]                      # strip Blender's .001 suffixes
        png = None
        for d in (npc_tex, tex_dir):
            for f in sorted(os.listdir(d), key=len, reverse=True):          # longest stem wins: slot name ends with "_<stem>_dds"
                stem = f[:-4].lower()
                if f.endswith(".png") and not stem.endswith(("_n", "_s", "_rmaos")) and nm.endswith("_" + stem + "_dds"):
                    png = os.path.join(d, f); break
            if png: break
        if png:
            m.use_nodes = True
            nt = m.node_tree
            tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(png)
            bsdf = nt.nodes.get("Principled BSDF")
            if bsdf:
                nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])

cam_data = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_data)
bpy.context.scene.collection.objects.link(cam)
cam.location = ctr + Vector((0, -size * 2.2, size * 0.1))
cam.rotation_euler = (math.radians(90), 0, 0)
cam_data.lens = 50
bpy.context.scene.camera = cam
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(20)); sun.data.energy = 3
bpy.context.scene.render.engine = "BLENDER_WORKBENCH"
bpy.context.scene.display.shading.light = "STUDIO"
bpy.context.scene.display.shading.color_type = "TEXTURE"
bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 600, 900
bpy.context.scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("RENDERED", out)
