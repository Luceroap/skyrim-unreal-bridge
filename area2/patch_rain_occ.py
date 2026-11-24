import importlib
p = r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py"
src = open(p, encoding="utf-8").read().rstrip()
assert src.endswith("start()")
ns = {"__name__": "live_bridge_patch", "__file__": p}
exec(compile(src[:-len("start()")], p, "exec"), ns)
import remaster_materials
importlib.reload(remaster_materials)
m = remaster_materials.rain_drops_material(rebuild=True)
print("material", m.get_name())
L = type(live)
for n in ("rain_occ_spawn", "rain_occ_update", "update_sky", "water_slots"):
    setattr(L, n, ns["Live"].__dict__[n])
if getattr(live, "rain_occ", None) is None and live.rain_field:
    live.rain_occ_spawn()
print("capture", live.rain_occ)
print("rain now", live.wx.get("rain"))
