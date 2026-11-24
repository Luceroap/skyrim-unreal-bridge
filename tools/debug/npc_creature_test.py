import sys, time, unreal
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live, live_bridge as lb
old = npc_live.MAX_NPCS
npc_live.MAX_NPCS = 60                      # temporary: let creatures past the 12-nearest cap
for i in range(10):                         # one slow import per call
    npc_live._read_and_spawn(live, lb, time.time())
acts = npc_live._state["actors"]
print("spawned", len(acts), "(cap was %d)" % old)
for aid, e in acts.items():
    lab = e["actor"].get_actor_label()
    if not any(k in lab for k in ("Aela", "Adrianne", "Guard", "Sigurd", "Brenuin", "Jenassa", "Carlotta", "Ysolda", "Mila", "Gerda", "Lillith")):
        comp = e["comp"]
        loc = e["actor"].get_actor_location()
        print("  OTHER", lab, "| ready", e.get("ready"), "| mesh bones", comp.get_num_bones(), "| scale", round(e["actor"].get_actor_scale3d().x, 2), "| pose samples", len(e.get("hist", [])), "| at", round(loc.x), round(loc.y), round(loc.z))
npc_live.MAX_NPCS = old
