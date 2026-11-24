import unreal, glob, os, re

SRC = r"C:\Users\Aidan\SkyrimUnrealBridge\area"
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary

# 1. meshes
tasks = []
for f in sorted(glob.glob(os.path.join(SRC, "export", "*.fbx"))):
    t = unreal.AssetImportTask()
    t.filename = f; t.destination_path = "/Game/Area"; t.automated = True; t.replace_existing = True; t.save = True
    tasks.append(t)
at.import_asset_tasks(tasks)
unreal.log("IMPORTED %d fbx" % len(tasks))

# 2. textures
tasks = []
for f in glob.glob(os.path.join(SRC, "tex", "*.png")):
    t = unreal.AssetImportTask()
    t.filename = f; t.destination_path = "/Game/AreaTex"; t.automated = True; t.replace_existing = True; t.save = True
    tasks.append(t)
at.import_asset_tasks(tasks)

MASKED = set(open(os.path.join(SRC, "tex", "alpha_masked.txt")).read().split())
# 3. one material per texture
mats = {}
for f in glob.glob(os.path.join(SRC, "tex", "*.png")):
    key = os.path.splitext(os.path.basename(f))[0]
    tex = unreal.load_asset("/Game/AreaTex/%s" % key)
    if not tex:
        continue
    m = at.create_asset("M_" + key, "/Game/AreaTex", unreal.Material, unreal.MaterialFactoryNew()) or unreal.load_asset("/Game/AreaTex/M_" + key)
    m.set_editor_property("two_sided", True)
    node = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -400, 0)
    node.set_editor_property("texture", tex)
    mel.connect_material_property(node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    if key.lower() in MASKED:
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        mel.connect_material_property(node, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_loaded_asset(m)
    mats[key.lower()] = m
unreal.log("MATERIALS %d" % len(mats))

# 4. assign by slot name
tot = hit_tot = 0
for mp in sorted(glob.glob(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Content\Area\*.uasset")):
    n = os.path.splitext(os.path.basename(mp))[0]
    mesh = unreal.load_asset("/Game/Area/" + n)
    if not isinstance(mesh, unreal.StaticMesh):
        continue
    for i, sm in enumerate(mesh.static_materials):
        slot = str(sm.material_slot_name).lower()
        tot += 1
        for key, m in mats.items():
            if slot.endswith("_" + key + "_dds"):
                mesh.set_material(i, m); hit_tot += 1; break
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
unreal.log("TEXTURED %d/%d slots" % (hit_tot, tot))

