import sys, math, time
nl = sys.modules.get("npc_live")
now = time.time()
print("apply_pose:", hasattr(unreal.SkyBridgeViewLibrary, "apply_pose"), "templates:", list(nl._state["template"].keys()), "seq", nl._state.get("seq"))
def ang(c, W, a, b):
    pa = W.inverse_transform_location(c.get_socket_location(nl.ue_bone(a)))
    pb = W.inverse_transform_location(c.get_socket_location(nl.ue_bone(b)))
    v = pb - pa; n = math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z) or 1
    return math.degrees(math.acos(max(-1, min(1, -v.z / n))))
for e in list(nl._state["actors"].values()):
    c = e["comp"]
    if c.get_num_bones() < 60:
        continue
    W = c.get_world_transform()
    try:
        r = ang(c, W, "NPC L UpperArm [LUar]", "NPC L Forearm [LLar]")
    except Exception as ex:
        r = -1
    s = e.get("shown")
    print("%-24s d%5.0f ready %d plan %3s hist %2d posed %.2fs ago shown_bind %s armFromVertical %.1f nb %d" % (
        e["actor"].get_actor_label()[:24], e.get("dist", 0), e["ready"], len(e.get("plan", [])), len(e.get("hist", [])),
        now - e.get("posed_t", 0), None if s is None else nl._is_bind(s["pose"][0], nl.rest_pose(s["sex"]), s["pose"][1]), r, c.get_num_bones()))
