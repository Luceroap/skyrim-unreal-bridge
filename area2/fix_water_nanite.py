Live = type(live)
old = Live.water_slots


def water_slots(comp, model):
    old(comp, model)
    for m in comp.get_materials():
        if m is not None and m.get_name() == "M_SkyWater":
            comp.set_editor_property("disallow_nanite", True)
            break


Live.water_slots = staticmethod(water_slots)

n = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor):
        continue
    c = a.static_mesh_component
    for m in c.get_materials():
        if m is not None and m.get_name() == "M_SkyWater":
            if not c.get_editor_property("disallow_nanite"):
                c.set_editor_property("disallow_nanite", True)
                n += 1
            break
print("water components switched off Nanite:", n)
