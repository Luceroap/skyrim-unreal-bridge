import sys, time
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Carlotta" in e["actor"].get_actor_label())
c = e["comp"]
print("posed ago", time.time() - e.get("posed_t", 0), "has rest0v", "rest0v" in e, "n scales", len(e.get("rest0s", {})))
for n in ("NPC", "NPC-Pelvis-_Pelv_", "NPC-Head-_Head_", "NPC-L-Hand-_LHnd_"):
    t = c.get_socket_transform(n, unreal.RelativeTransformSpace.RTS_COMPONENT)
    print(n, "render scale", t.scale3d, "loc", t.translation, "ref scale", e.get("rest0s", {}).get(n))
