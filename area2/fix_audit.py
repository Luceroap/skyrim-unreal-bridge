import importlib, sys
importlib.reload(sys.modules["ue_assets"])
src = open(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py").read().replace("\nstart()\n", "\n")
ns = {"__name__": "lb_patch"}
exec(src, ns)
setattr(type(live), "spawn_some", ns["Live"].__dict__["spawn_some"])
cache = type(live).__dict__.get("_slot_fix", {})
for k in [k for k, v in cache.items() if not v]:
    cache.pop(k)
n = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not str(a.get_folder_path()).startswith("SkyBridge"):
        continue
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.static_mesh
        if m and ("commonchair02" in m.get_name() or "wrtrelliscomplete01destroyed" in m.get_name()):
            type(live).fix_slots(c, m)
            n += 1
            print(m.get_name(), [c.get_material(i).get_name() if c.get_material(i) else None
                                 for i in range(len(m.static_materials))])
print("fixed", n)
