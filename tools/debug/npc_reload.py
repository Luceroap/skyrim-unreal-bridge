import sys, importlib, unreal
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_actor_label().startswith("NPC_"):
        a.destroy_actor()
importlib.reload(npc_live)            # fresh state; live_bridge picks the new module on its next tick and respawns
print("npc_live reloaded")
