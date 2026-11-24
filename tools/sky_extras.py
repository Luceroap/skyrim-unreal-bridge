"""Mountain haze/cloud band, moons, planets and aurora for the live Unreal view.
  python tools/sky_extras.py on [strength]     haze + mountain cloud band (strength 0-2, default 1) and, if it is night, moons/planets/aurora
  python tools/sky_extras.py night             force the night extras on (e.g. while an hour override is active)
  python tools/sky_extras.py off
Session-only (restart the editor to reset)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from start_bridge import ue_exec

mode = sys.argv[1] if len(sys.argv) > 1 else "on"
strength = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
SB = os.path.join(ROOT, "unreal", "SkyBridge")
code = f'''
import sys, importlib
sys.path.insert(0, r"{SB}")
import mountain_mist, night_sky
for m in (mountain_mist, night_sky): importlib.reload(m)
mode = {mode!r}
if mode == "off":
    print(mountain_mist.off(live)); night_sky.apply(live, night=False); print(night_sky.remove(), "bodies removed")
else:
    print(mountain_mist.apply(live, {strength}))
    night = mode == "night" or (getattr(live, "_sky_override", None) and (live._sky_override[0] < 5.5 or live._sky_override[0] > 20.5))
    print(night_sky.apply(live, night=bool(night)))
'''
print(ue_exec(code, 90))
