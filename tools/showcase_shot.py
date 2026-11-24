"""Showcase screenshots from the live Unreal editor: pins the viewport camera around a target, forces hour + weather (+ ground wetness/snow),
waits for the sky and exposure to settle, then saves a 4K PNG to screenshots/showcase/.   (needs play.py running; uses the exec hook)
  python tools/showcase_shot.py NAME X Y Z DIST AZIMUTH_DEG ELEV_DEG HOUR WEATHER [wet=0..1] [snow=0..1] [fov=deg] [settle=sec]
  python tools/showcase_shot.py --release          give the camera back to the game
WEATHER: clear cloud overcast fog rain storm snow.  Unreal units: cm, camera looks at (X,Y,Z)."""
import os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from start_bridge import ue_exec

OUT = os.path.join(ROOT, "screenshots", os.environ.get("SHOWCASE_DIR", "showcase"))
CAM = '''
import unreal, math
class _Proxy:
    def __init__(s, real, live): s._r, s._l = real, live
    def __getattr__(s, n): return getattr(s._r, n)
    def set_level_viewport_camera_info(s, loc, rot):
        pin = getattr(s._l, "_cam_pin", None)
        if pin: loc, rot = pin
        return s._r.set_level_viewport_camera_info(loc, rot)
if not isinstance(live.ues, _Proxy): live.ues = _Proxy(live.ues, live)
'''


def setup(x, y, z, d, az, el, hour, weather, wet, snow, fov):
    return CAM + '''
a, e = math.radians(%f), math.radians(%f)
tgt = unreal.Vector(%f, %f, %f)
cam = unreal.Vector(tgt.x + %f * math.cos(a) * math.cos(e), tgt.y + %f * math.sin(a) * math.cos(e), tgt.z + %f * math.sin(e))
live._cam_pin = (cam, unreal.MathLibrary.find_look_at_rotation(cam, tgt))
live._sky_override = (%f, %r)
live._sky_key = None
t = (%f - 5.5) / 15.0
elev = 70.0 * math.sin(math.pi * t) if 0 < t < 1 else -25.0
k = max(0.0, min(1.0, (elev - 3.0) / 40.0))           # 0 = on the horizon, 1 = high sun
warm = (1.0, 0.74, 0.58); mid = (1.0, 0.90, 0.80); white = (1.0, 0.97, 0.94)
def _mix(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))
c = _mix(warm, mid, min(1.0, k * 2.0)) if k < 0.5 else _mix(mid, white, (k - 0.5) * 2.0)
if elev > -3:
    live.sun.light_component.set_light_color(unreal.LinearColor(c[0], c[1], c[2], 1.0))
    live._sun_col = tuple(round(v, 2) for v in c)
    try:
        live.skylight.light_component.set_light_color(unreal.LinearColor(0.80, 0.90, 1.0, 1.0))   # cool blue sky fill in the shadows
    except Exception as ex:
        print("skylight", ex)
live.wx["wet"] = %f; live.wx["snow"] = %f
try:
    unreal.SystemLibrary.execute_console_command(None, "FOV %f")
except Exception as ex:
    print("fov", ex)
print("set", cam)
''' % (az, el, x, y, z, d, d, d, hour, weather, hour, wet, snow, fov)


def shoot(name, x, y, z, d, az, el, hour, weather, wet=0.0, snow=0.0, fov=60.0, settle=8.0, w=3840, h=2160, ev=None):
    os.makedirs(OUT, exist_ok=True)
    ue_exec('s = live.pp.get_editor_property("settings")\ns.set_editor_property("override_auto_exposure_bias", %s)\ns.set_editor_property("auto_exposure_bias", %f)\nlive.pp.set_editor_property("settings", s)' % (ev is not None, ev or 0.0), 30)
    path = os.path.join(OUT, name + ".png")
    if os.path.exists(path):
        os.remove(path)
    print(name, ue_exec(setup(x, y, z, d, az, el, hour, weather, wet, snow, fov), 30), flush=True)
    time.sleep(settle)                                   # sky/cloud/exposure/rain ease in over a few seconds
    ue_exec('unreal.AutomationLibrary.take_high_res_screenshot(%d, %d, r"%s")' % (w, h, path), 30)
    for _ in range(40):
        time.sleep(1)
        if os.path.exists(path) and os.path.getsize(path) > 50000:
            time.sleep(1)
            print("saved", path, os.path.getsize(path) // 1024, "KB", flush=True)
            return path
    print("NO FILE for", name)


if __name__ == "__main__":
    if sys.argv[1] == "--release":
        print(ue_exec("live._cam_pin = None; live._sky_override = None; live._sky_key = None", 30))
    else:
        a = sys.argv
        kw = dict(s.split("=") for s in a[10:])
        shoot(a[1], *[float(v) for v in a[2:9]], a[9], **{k: float(v) for k, v in kw.items()})
