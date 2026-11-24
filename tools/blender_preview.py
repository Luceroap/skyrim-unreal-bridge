"""D:\\blender.exe -b -P blender_preview.py -- <model.glb> <out.png>"""
import bpy, sys, math
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
c, size = (lo + hi) / 2, max((hi - lo).length, 1)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); bpy.context.scene.collection.objects.link(cam)
cam.location = c + Vector((size * 0.8, -size * 0.8, size * 0.5))
d = c - cam.location; cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
cam.data.clip_end = size * 10
bpy.context.scene.camera = cam
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'SINGLE'; sc.display.shading.single_color = (0.75, 0.7, 0.6)
sc.render.resolution_x, sc.render.resolution_y = 900, 600
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("PREVIEW", out, [round(v, 1) for v in (hi - lo)])
