import sys, json, unreal
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live
e = list(npc_live._state["actors"].values())[0]
comp = e["comp"]
inv = {}
out = {"rest0": {k: [list(v[0]), list(v[1])] for k, v in e["rest0"].items() if v}}
out["label"] = e["actor"].get_actor_label()
json.dump(out, open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\npc\rest0_dump.json", "w"))
print("dumped", len(out["rest0"]), out["label"])
