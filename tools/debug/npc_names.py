import sys, unreal
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live
e = list(npc_live._state["actors"].values())[0]
comp = e["comp"]
names = [str(comp.get_bone_name(i)) for i in range(comp.get_num_bones())]
print(len(names), names[:14])
print([n for n in names if "UpperArm" in n or "Thigh" in n][:6])
