import sys, math
nl = sys.modules.get("npc_live")
print("apply_pose available:", hasattr(unreal.SkyBridgeViewLibrary, "apply_pose"))
if nl:
    for e in list(nl._state["actors"].values())[:12]:
        c = e["comp"]
        if c.get_num_bones() < 100:
            continue
        W = c.get_world_transform()
        ua = W.inverse_transform_location(c.get_socket_location(nl.ue_bone("NPC L UpperArm [LUar]")))
        fa = W.inverse_transform_location(c.get_socket_location(nl.ue_bone("NPC L Forearm [LLar]")))
        v = fa - ua
        n = math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z) or 1
        print("%-26s rendered upper-arm angle from vertical: %.1f deg" % (e["actor"].get_actor_label()[:26], math.degrees(math.acos(max(-1, min(1, -v.z / n))))))
