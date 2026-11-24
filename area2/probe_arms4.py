import sys
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Aela" in e["actor"].get_actor_label())
c = e["comp"]
W = c.get_world_transform()
print("comp world", W.translation, W.rotation.rotator(), W.scale3d)
print("comp rel", c.get_relative_transform().scale3d, "actor", e["actor"].get_actor_transform().scale3d, e["actor"].get_actor_rotation())
CS = unreal.BoneSpaces.COMPONENT_SPACE
for nm in ("NPC Head [Head]", "NPC L Clavicle [LClv]", "NPC L UpperArm [LUar]", "NPC L Forearm [LLar]", "NPC L Hand [LHnd]", "NPC L Calf [LClf]"):
    un = nl.ue_bone(nm)
    t = c.get_bone_transform_by_name(un, CS)
    w = W.transform_location(t.translation)
    s = c.get_socket_location(un)
    print("%-24s cs->world (%.1f %.1f %.1f)  socket (%.1f %.1f %.1f)" % (nm, w.x, w.y, w.z, s.x, s.y, s.z))
