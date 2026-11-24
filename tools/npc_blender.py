"""Build a skinned character FBX (armature + joined body/hands/feet mesh) from npc_skin.py output.
Run: D:\\blender.exe -b -P npc_blender.py -- <skin_dir> <male|female> <out.fbx>
Same conventions as blender_export.py (Skyrim units * 0.014287 m, axis_forward -Y, up Z). Bones: every 'NPC ...' node + its ancestors."""
import bpy, json, os, sys
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
skin_dir, sex, out = args[:3]
omit = set()
creature = False                  # --creature: `sex` is a skeleton key (skeleton_<key>.json), the parts are only the listed jsons, bones = every skinned bone + ancestors
extra_parts = []                  # additional skin json file names (face_<id>.json: head, hair, eyes, brows, beard; gear_<id>_<n>.json: armor)
for a in args[3:]:
    if a.startswith("--omit="):
        omit = set(x for x in a[7:].split(",") if x)       # base parts replaced by worn armor: body, hands, feet
    elif a == "--creature":
        creature = True
    else:
        extra_parts.append(a)
SCALE = 0.014287

bpy.ops.wm.read_factory_settings(use_empty=True)
skel = json.load(open(os.path.join(skin_dir, "skeleton_%s.json" % sex)))

# kept bones: NPC* nodes and every ancestor (creatures: every bone a mesh is skinned to, and every ancestor)
keep = set()
used = set()
if creature:
    for pf in extra_parts:
        for sh in json.load(open(os.path.join(skin_dir, pf))):
            used.update(n for n in sh["bones"] if n)
for i, b in enumerate(skel):
    if (b["name"] in used) if creature else b["name"].startswith("NPC"):
        j = i
        while j >= 0 and j not in keep:
            keep.add(j); j = skel[j]["parent"]
order = sorted(keep)

arm_data = bpy.data.armatures.new("Armature")
arm = bpy.data.objects.new("Armature", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
eb = {}
for i in order:
    b = skel[i]
    e = arm_data.edit_bones.new(b["name"])
    R = Matrix([b["rot"][0:3], b["rot"][3:6], b["rot"][6:9]]).to_4x4()
    m = Matrix.Translation(Vector(b["pos"]) * SCALE) @ R
    e.head = (0, 0, 0); e.tail = (0, 0.02, 0)
    e.matrix = m
    eb[i] = e
for i in order:
    p = skel[i]["parent"]
    while p >= 0 and p not in eb:
        p = skel[p]["parent"]
    if p >= 0:
        eb[i].parent = eb[p]
bpy.ops.object.mode_set(mode="OBJECT")

part_files = extra_parts if creature else ["%s%s_1.json" % (sex, part) for part in ("body", "hands", "feet") if part not in omit] + extra_parts
mesh_objs = []
for pf in part_files:
    for sh in json.load(open(os.path.join(skin_dir, pf))):
        me = bpy.data.meshes.new(sh["name"])
        verts = [tuple(c * SCALE for c in v) for v in sh["verts"]]
        me.from_pydata(verts, [], [tuple(t) for t in sh["tris"]])
        me.update()
        uv = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for li in poly.loop_indices:
                uv.data[li].uv = sh["uvs"][me.loops[li].vertex_index]
        tex = sh["texture"] or "none"
        slot = tex.lower().replace("\\", "_").replace(".", "_")        # same naming as the static pipeline: textures_..._<key>_dds
        mat = bpy.data.materials.get(slot) or bpy.data.materials.new(slot)
        me.materials.append(mat)
        ob = bpy.data.objects.new(sh["name"], me)
        bpy.context.scene.collection.objects.link(ob)
        groups = {}
        for vi, (bi, wt) in enumerate(zip(sh["bone_idx"], sh["weights"])):
            for k in range(4):
                if wt[k] > 1e-4 and bi[k] < len(sh["bones"]) and sh["bones"][bi[k]]:
                    bn = sh["bones"][bi[k]]
                    if bn not in groups:                                    # (setdefault would create a new group per vertex)
                        groups[bn] = ob.vertex_groups.new(name=bn)
                    groups[bn].add([vi], wt[k], "ADD")
        for p in me.polygons:
            p.use_smooth = True
        mesh_objs.append(ob)

bpy.ops.object.select_all(action="DESELECT")
for ob in mesh_objs:
    ob.select_set(True)
bpy.context.view_layer.objects.active = mesh_objs[0]
bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
body.name = "npc_%s" % sex
mod = body.modifiers.new("Armature", "ARMATURE")
mod.object = arm
body.parent = arm
arm.name = "npc_%s_skeleton" % sex

bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True); body.select_set(True)
bpy.context.view_layer.objects.active = arm
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, axis_forward="-Y", axis_up="Z", global_scale=1.0, apply_unit_scale=True,
                         object_types={"ARMATURE", "MESH"}, add_leaf_bones=False, bake_anim=False, use_armature_deform_only=False)
print("EXPORTED", out, len(order), "bones", len(body.data.vertices), "verts", len(body.material_slots), "materials")
