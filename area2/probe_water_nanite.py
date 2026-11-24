water = 0
nanite = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor):
        continue
    c = a.static_mesh_component
    for m in c.get_materials():
        if m is not None and m.get_name() == "M_SkyWater":
            water += 1
            if not c.get_editor_property("disallow_nanite"):
                nanite += 1
            break
print("water components", water, "still nanite", nanite)
