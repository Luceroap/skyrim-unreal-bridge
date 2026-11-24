"""Sample the actor stream for ~40 s and report characters that move: are their limbs animated or at bind pose?"""
import math, subprocess, sys, time, types, os
sys.modules.setdefault("unreal", types.ModuleType("unreal"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import walk_check_lib as w   # noqa

seen = {}
t_end = time.time() + 40
prev = w.snap()
while time.time() < t_end:
    time.sleep(1.0)
    cur = w.snap()
    for i, a in cur.items():
        if i in prev and not (a["flags"] & 1):
            sp = math.dist(prev[i]["pos"], a["pos"])
            if sp > 25:                                   # > 25 units/s = walking
                ang = w.limb_angles(a)
                if ang:
                    spread = max(ang.values()) - min(ang.values())
                    seen.setdefault(a["name"], []).append((round(sp), "BIND" if spread < 6 else "animated", round(spread, 1)))
    prev = cur
if not seen:
    print("nobody walked in 40 s")
for n, l in seen.items():
    print(n, l[:8])
