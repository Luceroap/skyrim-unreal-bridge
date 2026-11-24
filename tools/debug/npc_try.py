import sys, time, importlib, traceback
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live
importlib.reload(npc_live)
try:
    for i in range(6):
        npc_live._state["last"] = 0
        npc_live.tick(live)
    s = npc_live._state
    print("meshes", list(s["meshes"]), "actors", [(k, v["actor"].get_actor_label()) for k, v in s["actors"].items()], "failed", s["failed"])
    acts = npc_live.read_actors()
    print("stream actors:", [(a["name"], "%08x" % a["base"], len(a["bones"])) for a in (acts or [])][:12])
except Exception:
    traceback.print_exc()
