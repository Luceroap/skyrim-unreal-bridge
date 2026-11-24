exec(open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\swap_npc.py").read())
import sys
nl = sys.modules["npc_live"]
for e in nl._state["actors"].values():
    for k in ("rest0v", "refcs", "rest0s"):
        e.pop(k, None)
print("reset", len(nl._state["actors"]))
