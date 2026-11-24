import json, os, shutil, sys, time
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge")
import start_bridge as sb
path, values = sb.DISPLAY_TWEAKS, sb.REMASTER_PROFILE[sb.DISPLAY_TWEAKS]
original = json.load(open(sb.PROFILE_BACKUP))
new = {k: v for k, v in values.items() if k not in original.get(path, {})}
print("to apply:", new)
if new:
    shutil.copy2(path, os.path.join(os.path.dirname(sb.PROFILE_BACKUP), "SSEDisplayTweaks.ini." + time.strftime("%Y%m%d-%H%M%S")))
    original.setdefault(path, {}).update(sb.set_ini(path, new))
    json.dump(original, open(sb.PROFILE_BACKUP, "w"), indent=1)
print([l for l in open(path) if l.startswith(("MinimumFramerate", "FramerateLimit=", "DynamicMaxTimeScaling"))])
