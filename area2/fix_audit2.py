import ue_assets
n = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.static_mesh
        if not m or m.get_name() != "clutter_common_commonchair02":
            continue
        for i, sm in enumerate(m.static_materials):
            mat = ue_assets.slot_material(str(sm.material_slot_name))
            if mat:
                c.set_material(i, mat)
        n += 1
        print([c.get_material(i).get_name() for i in range(len(m.static_materials))])
fs = type(live).__dict__["fix_slots"].__func__.__globals__.get("Live")
cache = fs.__dict__.get("_slot_fix", {}) if fs else {}
for k in [k for k, v in cache.items() if not v]:
    cache.pop(k)
print("chairs", n, "cleared stale cache misses")
