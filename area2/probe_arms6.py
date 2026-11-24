import sys
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Aela" in e["actor"].get_actor_label())
c = e["comp"]
W = c.get_world_transform()
CS = unreal.BoneSpaces.COMPONENT_SPACE
print("lods", c.get_num_lods(), "pred", c.get_predicted_lod_level(), "forced", c.get_forced_lod())
for nm in ("NPC L Clavicle [LClv]", "CME L UpperArm [LUar]", "NPC L UpperArm [LUar]", "CME L Forearm [LLar]", "NPC L Forearm [LLar]", "NPC L Hand [LHnd]"):
    un = nl.ue_bone(nm)
    s = W.inverse_transform_location(c.get_socket_location(un))
    g = c.get_bone_transform_by_name(un, CS).translation
    r = e["rest0q"][un][1]
    print("%-22s parent %-24s render (%.1f %.1f %.1f)  set (%.1f %.1f %.1f)  ref (%.1f %.1f %.1f)" % (
        nm, c.get_parent_bone(un), s.x, s.y, s.z, g.x, g.y, g.z, r[0], r[1], r[2]))
