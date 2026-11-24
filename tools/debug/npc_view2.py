import sys
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live, unreal
acts = npc_live._state["actors"]
target = None
for k, v in acts.items():
    if "Aela" in v["actor"].get_actor_label():
        target = v["actor"]
target = target or (list(acts.values())[0]["actor"] if acts else None)
if target:
    loc = target.get_actor_location()
    print("target", target.get_actor_label(), loc)
    c = unreal.Vector(loc.x, loc.y + 330, loc.z + 140)
    look = unreal.Vector(loc.x, loc.y, loc.z + 110)
    live.ues.set_level_viewport_camera_info(c, unreal.MathLibrary.find_look_at_rotation(c, look))
