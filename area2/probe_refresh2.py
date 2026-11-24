import sys
nl = sys.modules["npc_live"]
CS = unreal.BoneSpaces.COMPONENT_SPACE
for e in nl._state["actors"].values():
    c = e["comp"]
    un = nl.ue_bone("NPC L Hand [LHnd]")
    s = c.get_world_transform().inverse_transform_location(c.get_socket_location(un))
    g = c.get_bone_transform_by_name(un, CS).translation
    print("%-26s render (%.1f %.1f %.1f) set (%.1f %.1f %.1f) vis=%s" % (e["actor"].get_actor_label()[:26], s.x, s.y, s.z, g.x, g.y, g.z,
          c.get_editor_property("visibility_based_anim_tick_option")))
