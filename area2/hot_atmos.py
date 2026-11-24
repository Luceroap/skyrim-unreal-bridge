"""Hot-patch the running live_bridge with the current atmosphere.py / live_bridge.py (no editor restart)."""
import importlib, sys
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import atmosphere
importlib.reload(atmosphere)
src = open(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py").read()
src = src[:src.rindex("\nstart()")]
ns = {"__name__": "live_bridge_hot"}
exec(compile(src, "live_bridge.py", "exec"), ns)
for name in ("apply_lights", "update_sky", "tick_body"):
    setattr(type(live), name, getattr(ns["Live"], name))
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if isinstance(a, unreal.SkyAtmosphere):
        live.atmosphere = a.get_component_by_class(unreal.SkyAtmosphereComponent)
if not hasattr(live, "light_base"):
    live.light_base = {i: (a.light_component.intensity, tuple(live.light_vals[i][3:6])) for i, a in enumerate(live.light_actors) if i in live.light_vals}
atmosphere.sweep_captures(live)
tier = open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\hot_tier.txt").read().strip() if __import__("os").path.exists(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\hot_tier.txt") else None
print("tier", atmosphere.apply_quality(live, tier), atmosphere.detect_gpu())
print("night_mid", live.night_mid, "lights", len(live.light_actors), "base", len(live.light_base))
