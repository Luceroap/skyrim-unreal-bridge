"""Project startup: start the Skyrim live bridge once the editor is fully up (avoids -ExecutePythonScript, which closed the editor)."""
import os, sys
import unreal

DISABLE = r"C:\Users\Aidan\SkyrimUnrealBridge\area2\no_autostart.txt"
_state = {"n": 0, "h": None}


def _boot(dt):
    _state["n"] += 1
    if _state["n"] < 240:                       # ~ a few seconds of ticks so the editor finishes loading
        return
    unreal.unregister_slate_post_tick_callback(_state["h"])
    if os.path.exists(DISABLE):
        return
    d = r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge"
    if d not in sys.path:
        sys.path.insert(0, d)
    try:
        import live_bridge          # noqa: F401  (module start() runs on import)
    except Exception as e:
        unreal.log_error("[SkyBridgeLive] boot failed: %s" % e)


_state["h"] = unreal.register_slate_post_tick_callback(_boot)
