import importlib, sys
exec(open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\swap_npc.py").read())
import remaster_materials
importlib.reload(remaster_materials)
nl = sys.modules["npc_live"]
n = 0
for p in unreal.EditorAssetLibrary.list_assets("/Game/Npc", recursive=False, include_folder=False):
    name = p.split("/")[-1].split(".")[0]
    if not name.startswith("npc_"):
        continue
    mesh = unreal.load_asset(p)
    if not isinstance(mesh, unreal.SkeletalMesh):
        continue
    key = name[4:]
    mats = list(mesh.get_editor_property("materials"))
    for sm in mats:
        m = nl._material_for_slot(str(sm.material_slot_name), key)
        if m is not None:
            sm.set_editor_property("material_interface", m)
    mesh.set_editor_property("materials", mats)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    n += 1
for e in nl._state["actors"].values():
    m = e["comp"].get_skinned_asset()
    for i, sm in enumerate(m.get_editor_property("materials")):
        e["comp"].set_material(i, sm.get_editor_property("material_interface"))
print("meshes refreshed:", n, "hair MIs:", len([a for a in unreal.EditorAssetLibrary.list_assets("/Game/Area2Tex", recursive=False) if "MI_hair_" in a]))
