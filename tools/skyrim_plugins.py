"""Turn off Skyrim SKSE plugins the bridge does not need (physics + visual-only), by MOVING the DLLs into Plugins\\_disabled_for_bridge.
  python tools/skyrim_plugins.py            disable   (Skyrim must be closed: DLLs are locked while it runs)
  python tools/skyrim_plugins.py --restore  put every moved DLL back
Nothing is deleted; the list of moved files is kept in _disabled_for_bridge\\moved.json."""
import json, os, shutil, subprocess, sys

PLUGINS = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\SKSE\Plugins"
PARK = os.path.join(PLUGINS, "_disabled_for_bridge")
LOG = os.path.join(PARK, "moved.json")
# Unreal draws everything and only reads positions/poses; these cost CPU/GPU in Skyrim and change nothing the bridge streams.
DISABLE = [   # hdtSMP64 / SMP-NPC crash fix / cbp must STAY enabled: meshes carry HDT physics extra data and Skyrim crashes at load without the plugin
    "ImmersiveEquipmentDisplays.dll", "OpenAnimationReplacer-IEDConditionExtensions.dll",
    "ShadowBoost.dll", "ENBHelperSE.dll", "WadeInWater.dll",
]

if "SkyrimSE.exe" in subprocess.run(["tasklist", "/FI", "IMAGENAME eq SkyrimSE.exe"], capture_output=True, text=True).stdout:
    sys.exit("Skyrim is running; close it first")
os.makedirs(PARK, exist_ok=True)
moved = json.load(open(LOG)) if os.path.exists(LOG) else []
if "--restore" in sys.argv:
    for n in moved:
        if os.path.exists(os.path.join(PARK, n)):
            shutil.move(os.path.join(PARK, n), os.path.join(PLUGINS, n)); print("restored", n)
    json.dump([], open(LOG, "w")); sys.exit()
for n in DISABLE:
    src = os.path.join(PLUGINS, n)
    if os.path.exists(src):
        shutil.move(src, os.path.join(PARK, n)); moved.append(n); print("disabled", n)
    else:
        print("not present / already off:", n)
json.dump(sorted(set(moved)), open(LOG, "w"))

