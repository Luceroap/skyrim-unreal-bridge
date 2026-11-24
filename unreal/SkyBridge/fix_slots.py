import unreal, glob, os
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary

# fully transparent material for shapes that have no shader in the game (never drawn by Skyrim)
path = "/Game/Area2Tex/M_Hidden"
hid = unreal.load_asset(path) if eal.does_asset_exist(path) else at.create_asset("M_Hidden", "/Game/Area2Tex", unreal.Material, unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(hid)
hid.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
z = mel.create_material_expression(hid, unreal.MaterialExpressionConstant, -300, 0)
z.set_editor_property("r", 0.0)
mel.connect_material_property(z, "", unreal.MaterialProperty.MP_OPACITY_MASK)
mel.recompile_material(hid); eal.save_loaded_asset(hid)

mats = {}
for p in glob.glob(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Content\Area2Tex\M_*.uasset"):
    n = os.path.splitext(os.path.basename(p))[0]
    mats[n[2:].lower()] = unreal.load_asset("/Game/Area2Tex/" + n)

hidden = fixed = 0
for p in sorted(glob.glob(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Content\Area2\*.uasset")):
    n = os.path.splitext(os.path.basename(p))[0]
    mesh = unreal.load_asset("/Game/Area2/" + n)
    if not isinstance(mesh, unreal.StaticMesh) or n == "terrain":
        continue
    changed = False
    for i, sm in enumerate(mesh.static_materials):
        mi = sm.material_interface
        if mi and "/Game/Area2Tex/M_" in mi.get_path_name():
            continue
        slot = str(sm.material_slot_name).lower()
        if slot in ("null", "none"):
            mesh.set_material(i, hid); hidden += 1; changed = True; continue
        base = slot.split("_ncl_")[0]                      # Blender duplicate-name suffix
        for key, m in mats.items():
            if base.endswith("_" + key + "_dds"):
                mesh.set_material(i, m); fixed += 1; changed = True; break
    if changed: eal.save_loaded_asset(mesh)
unreal.log("FIXSLOTS hidden=%d renamed-fixed=%d" % (hidden, fixed))
