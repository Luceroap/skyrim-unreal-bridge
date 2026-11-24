import sys, math, time
nl = sys.modules["npc_live"]
now = time.time()
for e in nl._state["actors"].values():
    lab = e["actor"].get_actor_label()
    print(lab[:24], "ready", e.get("ready"), "shown", bool(e.get("shown")), "hist", len(e.get("hist", [])),
          "posed_ago %.2f" % (now - e.get("posed_t", 0)), "dist", round(e.get("dist", 0)), "plan", len(e.get("plan", [])))
e = next(e for e in nl._state["actors"].values() if "Aela" in e["actor"].get_actor_label())
names = [p[0] for p in e.get("plan", [])]
print([n for n in names if "Arm" in n or "Clav" in n or "Spine" in n])
c = e["comp"]
print("bones in mesh", c.get_num_bones())
print([str(c.get_bone_name(i)) for i in range(c.get_num_bones()) if "Arm" in str(c.get_bone_name(i))])
