import sys
mode = open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\night_mode.txt").read().strip()
m = live.night_mid
if mode == "on":
    m.set_scalar_parameter_value("Night", 1.0); m.set_scalar_parameter_value("Aurora", 1.0)
    m.set_scalar_parameter_value("Intensity", 400.0)
    live._night_test = True
    open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\shot_request.txt", "w").close()
else:
    m.set_scalar_parameter_value("Intensity", 6.0)
    live._sky_key = None
print("night test", mode)
