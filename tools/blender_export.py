"""Run: D:\\blender.exe -b -P blender_export.py -- <obj_dir> <out_dir>
Imports each Skyrim-derived OBJ (Z up), scales Skyrim units to metres (1 unit = 1.4287 cm), exports FBX + GLB."""
import bpy, sys, os, glob

obj_dir, out_dir = sys.argv[sys.argv.index("--") + 1:][:2]
os.makedirs(out_dir, exist_ok=True)
SCALE = 0.014287

for path in sorted(glob.glob(os.path.join(obj_dir, "*.obj"))):
    name = os.path.splitext(os.path.basename(path))[0]
    if os.path.exists(os.path.join(out_dir, name + ".fbx")) and not os.environ.get("FORCE"):
        continue                                                    # already exported (incremental)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=path, forward_axis='Y', up_axis='Z')
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for o in objs:
        o.scale = (SCALE, SCALE, SCALE)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if len(objs) > 1:
        bpy.ops.object.join()  # one mesh per building, material slots preserved
    objs = [bpy.context.view_layer.objects.active]
    objs[0].name = name
    objs[0].data.name = name
    verts = sum(len(o.data.vertices) for o in objs)
    bpy.ops.export_scene.fbx(filepath=os.path.join(out_dir, name + ".fbx"), use_selection=True,
                             axis_forward='-Y', axis_up='Z', global_scale=1.0, apply_unit_scale=True)
    pass
    print("EXPORTED", name, len(objs), "objects", verts, "verts")

