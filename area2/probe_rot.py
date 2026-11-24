import sys
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Aela" in e["actor"].get_actor_label())
c = e["comp"]
CS = unreal.BoneSpaces.COMPONENT_SPACE
for i in range(0, c.get_num_bones(), 1):
    un = str(c.get_bone_name(i))
    if not any(k in un for k in ("Root", "Pelvis", "Spine-", "Head-", "L-UpperArm", "L-Thigh", "L-Calf", "NPC-")):
        continue
    t = c.get_bone_transform_by_name(un, CS)
    rq, rt = e["rest0q"].get(un, (None, None))
    q = t.rotation
    print("%3d %-28s scale (%.2f %.2f %.2f) rot (%.2f %.2f %.2f %.2f) ref (%s)" % (
        i, un[:28], t.scale3d.x, t.scale3d.y, t.scale3d.z, q.x, q.y, q.z, q.w,
        " ".join("%.2f" % v for v in rq) if rq else None))
