import sys
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live, unreal
t = None
for k, v in npc_live._state["actors"].items():
    if "Cow" in v["actor"].get_actor_label():
        t = v["actor"]
if t:
    loc = t.get_actor_location()
    print("cow at", round(loc.x), round(loc.y), round(loc.z), "scale", t.get_actor_scale3d().x)
    c = unreal.Vector(loc.x + 420, loc.y + 250, loc.z + 170)
    look = unreal.Vector(loc.x, loc.y, loc.z + 90)
    live.ues.set_level_viewport_camera_info(c, unreal.MathLibrary.find_look_at_rotation(c, look))
else:
    print("no cow spawned (it left the range or the cap dropped it)")
