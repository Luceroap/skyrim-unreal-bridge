"""Offline: an animated walker records a gait cycle; a frozen walker (same pose every sample, root moving) and a bind walker play it."""
import math, sys, types
sys.modules["unreal"] = types.SimpleNamespace(log=print, SkyBridgeViewLibrary=types.SimpleNamespace())
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import npc_live as nl

def qax(ax, deg):
    s = math.sin(math.radians(deg) / 2); return (ax[0] * s, ax[1] * s, ax[2] * s, math.cos(math.radians(deg) / 2))
rest = {raw: (nl.quat_to_mat(0, 0, 0, 1), [0, 0, 0]) for raw in nl.LIMBS}
nl._state["rest"]["male"] = rest
def bones_at(phase, x, bind=False):
    b = {"NPC": ((x, 0, 0), (0, 0, 0, 1))}
    for i, raw in enumerate(nl.LIMBS):
        b[raw] = ((x, 0, 50), (0, 0, 0, 1) if bind else qax((1, 0, 0), 25 * math.sin(2 * math.pi * phase + i)))
    return b
A, F, B = {}, {}, {}
t = 0.0
for k in range(150):                       # 5 s at 30 Hz, walking 100 u/s, 1.2 s gait cycle
    t = k / 30.0
    nl._ingest(A, dict(bones=bones_at(t / 1.2, 100 * t), flags=0), t)
    nl._ingest(F, dict(bones=bones_at(0.3, 100 * t, False) if k > 0 else bones_at(0.3, 0), flags=0), t)
    nl._ingest(B, dict(bones=bones_at(0, 100 * t, True), flags=0), t)
L = nl._state["walk"]["male"]["loop"]
print("animated frozen=%s  frozen-walker frozen=%s  loop dur %.2f s (true 1.2)  speed %.0f" % (A.get("frozen"), F.get("frozen"), L["dur"], L["speed"]))
def shown(e):
    return [round(math.degrees(2 * math.acos(min(1, h["pose"][0][nl.LIMBS[0]][1][3]))), 1) for h in e["hist"][-6:]]
print("frozen walker limb angle, last samples:", shown(F))
print("bind walker limb angle, last samples:  ", shown(B))
print("animated walker, last samples:         ", shown(A))
