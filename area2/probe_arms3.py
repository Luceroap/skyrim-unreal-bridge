import sys, math
nl = sys.modules["npc_live"]
e = next(e for e in nl._state["actors"].values() if "Aela" in e["actor"].get_actor_label())
c = e["comp"]
plan = {p[0]: p for p in e["plan"]}
bones, rq, rp = e["shown"]["pose"]
CS = unreal.BoneSpaces.COMPONENT_SPACE
for nm in ("NPC L Clavicle [LClv]", "NPC L UpperArm [LUar]", "NPC L Forearm [LLar]", "NPC L Hand [LHnd]"):
    un = nl.ue_bone(nm)
    t = c.get_bone_transform_by_name(un, CS)
    print(nm, "in plan", nm in plan, "in stream", nm in bones, "parent", c.get_parent_bone(un),
          "cs loc", [round(x, 1) for x in (t.translation.x, t.translation.y, t.translation.z)],
          "sock", c.get_socket_location(un))
print("order:", [n for n in [p[0] for p in e["plan"]] if "L " in n and ("Arm" in n or "arm" in n or "Clav" in n or "Hand" in n)])
