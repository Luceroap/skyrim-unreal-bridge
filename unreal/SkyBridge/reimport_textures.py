"""Re-import the textures that tools/upscale_textures.py replaced (names in area2/tex/upscaled.txt), keeping the assets
and their settings. Run with the editor closed:
  UnrealEditor-Cmd.exe SkyBridge.uproject -run=pythonscript -script=<this file>
"""
import os
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
DONE = os.path.join(AREA, "tex", "upscaled.txt")
STAMP = os.path.join(AREA, "tex", "upscaled_imported.txt")

at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
done = open(DONE).read().split() if os.path.exists(DONE) else []
imported = set(open(STAMP).read().split()) if os.path.exists(STAMP) else set()
tasks, keys = [], []
for key in done:
    if key in imported or not eal.does_asset_exist("/Game/Area2Tex/" + key):
        continue
    t = unreal.AssetImportTask()
    t.filename = os.path.join(AREA, "tex", key + ".png"); t.destination_path = "/Game/Area2Tex"
    t.automated = True; t.replace_existing = True; t.replace_existing_settings = False; t.save = True
    tasks.append(t); keys.append(key)
if tasks:
    at.import_asset_tasks(tasks)
    with open(STAMP, "a") as f:
        f.write("".join(k + "\n" for k in keys))
unreal.log("[SkyMaterials] re-imported %d upscaled textures" % len(tasks))
