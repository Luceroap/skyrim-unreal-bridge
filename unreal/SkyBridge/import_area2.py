# Incremental importer: meshes (FBX), textures (PNG) and one material per texture; only new assets are imported.
import unreal, glob, os

SRC = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary


def task(f, dest):
    t = unreal.AssetImportTask()
    t.filename = f; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
    return t


# 1. meshes
new_meshes = []
tasks = []
for f in sorted(glob.glob(os.path.join(SRC, "export", "*.fbx"))):
    n = os.path.splitext(os.path.basename(f))[0]
    if not eal.does_asset_exist("/Game/Area2/" + n):
        tasks.append(task(f, "/Game/Area2")); new_meshes.append(n)
if tasks: at.import_asset_tasks(tasks)
unreal.log("IMPORTED %d new fbx" % len(tasks))

# 2. textures
tasks = []
for f in glob.glob(os.path.join(SRC, "tex", "*.png")):
    n = os.path.splitext(os.path.basename(f))[0]
    if not eal.does_asset_exist("/Game/Area2Tex/" + n):
        tasks.append(task(f, "/Game/Area2Tex"))
if tasks: at.import_asset_tasks(tasks)

# 3. materials (new textures only)
alpha = os.path.join(SRC, "tex", "alpha_masked.txt")
MASKED = set(open(alpha).read().split()) if os.path.exists(alpha) else set()
mats = {}
for f in glob.glob(os.path.join(SRC, "tex", "*.png")):
    key = os.path.splitext(os.path.basename(f))[0]
    path = "/Game/Area2Tex/M_" + key
    if eal.does_asset_exist(path):
        mats[key.lower()] = unreal.load_asset(path); continue
    tex = unreal.load_asset("/Game/Area2Tex/%s" % key)
    if not tex or key == "terrain_detail":
        continue
    m = at.create_asset("M_" + key, "/Game/Area2Tex", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("two_sided", True)
    node = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -400, 0)
    node.set_editor_property("texture", tex)
    mel.connect_material_property(node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    if key.lower() in MASKED:
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        mel.connect_material_property(node, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    mats[key.lower()] = m

# 4. assign materials by slot name (newly imported meshes only)
tot = hit = 0
for n in new_meshes:
    mesh = unreal.load_asset("/Game/Area2/" + n)
    if not isinstance(mesh, unreal.StaticMesh) or n == "terrain":
        continue
    for i, sm in enumerate(mesh.static_materials):
        slot = str(sm.material_slot_name).lower(); tot += 1
        for key, m in mats.items():
            if slot.endswith("_" + key + "_dds"):
                mesh.set_material(i, m); hit += 1; break
    eal.save_loaded_asset(mesh)
unreal.log("TEXTURED %d/%d slots on %d new meshes" % (hit, tot, len(new_meshes)))
