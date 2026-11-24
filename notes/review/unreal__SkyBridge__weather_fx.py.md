# Review leads for unreal/SkyBridge/weather_fx.py (UNVERIFIED)
L295 | bug | `except Exception as e: log(...)` | Effect may break silently without user notice | Log as error and fail fast instead of swallowing | medium
