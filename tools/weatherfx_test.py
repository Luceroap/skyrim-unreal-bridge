# Live test driver (python tools/ue_run.py tools/weatherfx_test.py 120). Edit FORCE below; all None = Skyrim's weather.
# MODE "on": (re)load weather_fx and drive update() from a temporary slate tick; "off": weather_fx.clear() (actors gone,
# test tick removed, MPC zeroed); "rebuild": recreate both materials first.
MODE = "on"
FORCE = {"snow": 1.0, "rain": None, "wind": 0.3}

import importlib, sys, unreal
import weather_fx
if MODE in ("on", "rebuild"):
    weather_fx.clear(live)
    importlib.reload(weather_fx)
    if MODE == "rebuild":
        weather_fx.build(rebuild=True)
    weather_fx.FORCE.update(FORCE)
    weather_fx.install_test_tick(live)
    print("test tick on, FORCE", weather_fx.FORCE, "interior", getattr(live, "_interior", None))
else:
    weather_fx.clear(live)
    print("cleared")
