import sys
nl = sys.modules["npc_live"]
for e in nl._state["actors"].values():
    lab = e["actor"].get_actor_label()
    if not any(n in lab for n in ("Carlotta", "Jenassa")):
        continue
    comp = e["comp"]
    mesh = comp.get_skinned_asset()
    print("==", lab, mesh.get_name())
    for sm in mesh.get_editor_property("materials"):
        mi = sm.get_editor_property("material_interface")
        info = ""
        if isinstance(mi, unreal.MaterialInstanceConstant):
            t = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mi, "BaseColor")
            bm = mi.get_editor_property("base_property_overrides")
            info = "base=%s blend_override=%s/%s" % (t.get_name() if t else None, bm.get_editor_property("override_blend_mode"), bm.get_editor_property("blend_mode"))
        print("   %-60s -> %s %s" % (str(sm.get_editor_property("material_slot_name"))[:60], mi.get_name() if mi else None, info))
