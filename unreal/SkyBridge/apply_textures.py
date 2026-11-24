import unreal, glob, os, re

TEXDIR = r"C:\Users\Aidan\SkyrimUnrealBridge\whiterun\tex"
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary

# 1. import PNGs as textures
tasks = []
for f in glob.glob(os.path.join(TEXDIR, "*.png")):
    t = unreal.AssetImportTask()
    t.filename = f; t.destination_path = "/Game/WhiterunTex"; t.automated = True; t.replace_existing = True; t.save = True
    tasks.append(t)
at.import_asset_tasks(tasks)

# 2. one material per texture
mats = {}
for f in glob.glob(os.path.join(TEXDIR, "*.png")):
    key = os.path.splitext(os.path.basename(f))[0]            # e.g. wrslate01
    tex = unreal.load_asset("/Game/WhiterunTex/%s" % key)
    if not tex:
        unreal.log_warning("no texture for " + key); continue
    name = "M_" + key
    m = at.create_asset(name, "/Game/WhiterunTex", unreal.Material, unreal.MaterialFactoryNew())
    if not m:
        m = unreal.load_asset("/Game/WhiterunTex/" + name)
    m.set_editor_property("two_sided", True)
    node = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -400, 0)
    node.set_editor_property("texture", tex)
    mel.connect_material_property(node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_loaded_asset(m)
    mats[key.lower()] = m

# 3. assign by slot name
for mp in sorted(glob.glob(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Content\WhiterunMeshes\wr*.uasset")):
    n = os.path.splitext(os.path.basename(mp))[0]
    mesh = unreal.load_asset("/Game/WhiterunMeshes/" + n)
    if not mesh: continue
    hit = 0
    for i, sm in enumerate(mesh.static_materials):
        slot = str(sm.material_slot_name).lower()
        for key, m in mats.items():
            if slot.endswith(key + "_dds") or slot.endswith(key) or ("_" + key + "_") in slot or slot.startswith("textures_architecture_whiterun_" + key):
                mesh.set_material(i, m); hit += 1; break
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    unreal.log("TEXTURED %s: %d/%d slots" % (n, hit, len(mesh.static_materials)))
