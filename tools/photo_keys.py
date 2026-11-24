"""Photo hotkeys while you fly around in Skyrim (works with Skyrim focused). Run by Photo_Shoot.bat; saves to screenshots/photos/.
  F8  4K photo (3840x2160)         F9  8K photo (7680x4320)       a short beep confirms, the file appears a few seconds later
  F5  time of day +1.5 h           F6  next weather (clear, cloud, overcast, fog, rain, storm, snow)      F7  give sky back to the game
Tip: Skyrim free camera: open the console with ~ and type tfc (again to leave). 'tcl' = walk through walls. Everything is local."""
import ctypes, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from start_bridge import ue_exec

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "screenshots", "photos")
SKY = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\SKSE\Plugins\SkyrimUnrealBridge.sky"
WEATHERS = ["clear", "cloud", "overcast", "fog", "rain", "storm", "snow"]
VK = {"F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77, "F9": 0x78}
user32 = ctypes.windll.user32
try:
    import winsound
    beep = lambda f, d=120: winsound.Beep(f, d)
except Exception:
    beep = lambda f, d=120: None

SKY_CODE = '''
import math, unreal
hour, weather, wet, snow = %f, %r, %f, %f
live._sky_override = (hour, weather); live._sky_key = None
live.wx["wet"] = wet; live.wx["snow"] = snow
t = (hour - 5.5) / 15.0
elev = 70.0 * math.sin(math.pi * t) if 0 < t < 1 else -25.0
k = max(0.0, min(1.0, (elev - 3.0) / 40.0))
warm = (1.0, 0.74, 0.58); mid = (1.0, 0.90, 0.80); white = (1.0, 0.97, 0.94)
mix = lambda a, b, u: tuple(a[i] + (b[i] - a[i]) * u for i in range(3))
c = mix(warm, mid, min(1.0, k * 2.0)) if k < 0.5 else mix(mid, white, (k - 0.5) * 2.0)
if elev > -3:
    live.sun.light_component.set_light_color(unreal.LinearColor(c[0], c[1], c[2], 1.0))
'''
state = dict(hour=12.0, wx=0, override=False)


def apply_sky():
    w = WEATHERS[state["wx"]]
    ue_exec(SKY_CODE % (state["hour"], w, 1.0 if w in ("rain", "storm") else 0.0, 1.0 if w == "snow" else 0.0), 30)
    with open(SKY, "w") as f:                       # the game clock too, so its torches/lights follow
        f.write("hour %.2f\n" % state["hour"])
    state["override"] = True


def photo(w, h):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "photo_%s_%dx%d.png" % (time.strftime("%H%M%S"), w, h))
    ue_exec('unreal.AutomationLibrary.take_high_res_screenshot(%d, %d, r"%s")' % (w, h, path), 30)
    print("photo ->", path, flush=True)


down = {k: False for k in VK}
print(__doc__, flush=True)
while True:
    for name, code in VK.items():
        pressed = bool(user32.GetAsyncKeyState(code) & 0x8000)
        if pressed and not down[name]:
            try:
                if name == "F8": beep(900); photo(3840, 2160)
                elif name == "F9": beep(1200); photo(7680, 4320)
                elif name == "F5": state["hour"] = (state["hour"] + 1.5) % 24; apply_sky(); beep(600)
                elif name == "F6": state["wx"] = (state["wx"] + 1) % len(WEATHERS); apply_sky(); beep(700)
                elif name == "F7":
                    ue_exec("live._sky_override = None; live._sky_key = None", 30); state["override"] = False; beep(500)
            except Exception as e:
                print("error", name, e, flush=True)
        down[name] = pressed
    time.sleep(0.05)
