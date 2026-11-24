"""Apply the character detail settings to already imported NPC material instances."""
import os
import sys
import unreal

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import remaster_materials

area = remaster_materials.AREA
npc_dir = os.path.join(area, "npc", "tex")
keys = {os.path.splitext(x)[0].lower() for x in os.listdir(npc_dir) if x.endswith(".png")}
count = 0
for path in unreal.EditorAssetLibrary.list_assets("/Game/Area2Tex", recursive=False, include_folder=False):
    asset = unreal.load_asset(path)
    if not isinstance(asset, unreal.MaterialInstanceConstant):
        continue
    key = str(asset.get_name())[3:].lower() if str(asset.get_name()).startswith("MI_") else ""
    if key not in keys:
        continue
    remaster_materials.configure(asset, key)
    count += 1
unreal.log("[SkyBridge] boosted %d NPC material instances" % count)
