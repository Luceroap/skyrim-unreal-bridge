import unreal
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
t = unreal.AssetImportTask()
t.filename = r"C:\Users\Aidan\SkyrimUnrealBridge\area2\export\terrain.fbx"
t.destination_path = "/Game/Area2"; t.automated = True; t.replace_existing = True; t.save = True
at.import_asset_tasks([t])
m = at.create_asset("M_Terrain2", "/Game/Area2", unreal.Material, unreal.MaterialFactoryNew()) or unreal.load_asset("/Game/Area2/M_Terrain2")
tex = unreal.load_asset("/Game/Area2Tex/terrain_detail")
ts = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -600, 0)
ts.set_editor_property("texture", tex)
vc = mel.create_material_expression(m, unreal.MaterialExpressionVertexColor, -600, 250)
mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, 100)
mel.connect_material_expressions(ts, "RGB", mul, "A")
mel.connect_material_expressions(vc, "RGB", mul, "B")
mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
m.set_editor_property("two_sided", True)
mel.recompile_material(m); unreal.EditorAssetLibrary.save_loaded_asset(m)
mesh = unreal.load_asset("/Game/Area2/terrain")
for i in range(len(mesh.static_materials)):
    mesh.set_material(i, m)
unreal.EditorAssetLibrary.save_loaded_asset(mesh)
b = mesh.get_bounds()
unreal.log("TERRAIN2 slots=%d ext=(%.0f,%.0f,%.0f)" % (len(mesh.static_materials), b.box_extent.x, b.box_extent.y, b.box_extent.z))

