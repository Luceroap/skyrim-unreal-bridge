import sys, unreal
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live
acts = npc_live._state["actors"]
print("spawned:", len(acts))
for aid, e in acts.items():
    lab = e["actor"].get_actor_label()
    sc = e["actor"].get_actor_scale3d()
    print("  %-30s ready=%s bones=%d scale=%.2f loc=%s" % (lab, e.get("ready"), len(e.get("names", ())), sc.x, [round(v) for v in (e["actor"].get_actor_location().x, e["actor"].get_actor_location().y, e["actor"].get_actor_location().z)]))
