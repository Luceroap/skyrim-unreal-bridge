import sys
nl = sys.modules["npc_live"]
CS = unreal.BoneSpaces.COMPONENT_SPACE
for e in list(nl._state["actors"].values())[:4]:
    a = e["actor"]; c = e["comp"]
    o, ext = a.get_actor_bounds(False)
    print(a.get_actor_label()[:24], "loc", a.get_actor_location(), "bounds origin", o, "extent", ext)
    for n in ("npc_female_skeleton", "npc_male_skeleton", "skeleton_female_nif", "NPC", "NPC-Pelvis-_Pelv_", "NPC-Head-_Head_"):
        if c.get_bone_index(n) >= 0:
            t = c.get_bone_transform_by_name(n, CS)
            r = c.get_ref_pose_transform(c.get_bone_index(n))
            print("   %-22s cs t=%s q=%s s=%s | ref local t=%s s=%s" % (n, t.translation, t.rotation, t.scale3d, r.translation, r.scale3d))
