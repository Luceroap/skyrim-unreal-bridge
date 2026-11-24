import sys, math
nl = sys.modules["npc_live"]
st = nl._state
print("npcs", len(st["actors"]), "budget", st.get("pose_budget"), "seq", st.get("seq"))
for aid, e in list(st["actors"].items())[:6]:
    comp = e["comp"]
    s = e.get("shown")
    plan = e.get("plan") or []
    arm = "NPC-L-UpperArm-_LUar_"
    t = comp.get_bone_transform_by_name(arm, unreal.BoneSpaces.COMPONENT_SPACE) if arm in e.get("names", ()) else None
    r0 = e.get("rest0", {}).get(arm)
    diff = None
    if t and r0:
        q = t.rotation; q0 = nl.mat_to_quat(r0[0])
        d = abs(q.x * q0[0] + q.y * q0[1] + q.z * q0[2] + q.w * q0[3])
        diff = math.degrees(2 * math.acos(min(1, d)))
    print("%-26s ready %s plan %d hist %d shown %s posed_t %.1f  L-upperarm deg from bind %s  bones %d" % (
        e["actor"].get_actor_label(), e.get("ready"), len(plan), len(e.get("hist", [])), s is not None,
        e.get("posed_t", 0) % 1000, None if diff is None else round(diff, 1), comp.get_num_bones()))
