import unreal, glob, os
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
SRC = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"


def task(f, dest):
    t = unreal.AssetImportTask()
    t.filename = f; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
    return t


tiles = sorted(glob.glob(os.path.join(SRC, "tex", "terrain_tile_*.png")))
at.import_asset_tasks([task(f, "/Game/Area2Tex") for f in tiles])
at.import_asset_tasks([task(os.path.join(SRC, "export", "terrain.fbx"), "/Game/Area2")])
mesh = unreal.load_asset("/Game/Area2/terrain")
hit = 0
for i, sm in enumerate(mesh.static_materials):
    slot = str(sm.material_slot_name)
    tex = unreal.load_asset("/Game/Area2Tex/" + slot)
    if not tex:
        continue
    mp = "/Game/Area2Tex/M_" + slot
    m = unreal.load_asset(mp) if eal.does_asset_exist(mp) else at.create_asset("M_" + slot, "/Game/Area2Tex", unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(m)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -500, 0)
    t.set_editor_property("texture", tex)
    mel.connect_material_property(t, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    c = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -300, 200)
    c.set_editor_property("r", 0.9)
    mel.connect_material_property(c, "", unreal.MaterialProperty.MP_ROUGHNESS)
    m.set_editor_property("two_sided", True)
    mel.recompile_material(m); eal.save_loaded_asset(m)
    mesh.set_material(i, m); hit += 1
eal.save_loaded_asset(mesh)
b = mesh.get_bounds()
unreal.log("TERRAIN3 materials %d/%d ext=(%.0f,%.0f,%.0f)" % (hit, len(mesh.static_materials), b.box_extent.x, b.box_extent.y, b.box_extent.z))
