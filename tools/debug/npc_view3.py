import sys
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live, unreal
acts = npc_live._state["actors"]
best = None
for k, v in acts.items():
    if v.get("speed", 0) > 25:
        best = v
if best is None:
    print("no walking npc; actors:", [(v["actor"].get_actor_label(), round(v.get("speed", 0))) for v in acts.values()])
else:
    target = best["actor"]
    loc = target.get_actor_location()
    print("target (walking)", target.get_actor_label(), "speed", round(best["speed"]), loc)
    c = unreal.Vector(loc.x + 300, loc.y + 150, loc.z + 140)
    look = unreal.Vector(loc.x, loc.y, loc.z + 100)
    live.ues.set_level_viewport_camera_info(c, unreal.MathLibrary.find_look_at_rotation(c, look))
