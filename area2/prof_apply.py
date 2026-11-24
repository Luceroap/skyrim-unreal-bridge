import sys, time
nl = sys.modules["npc_live"]
es = [e for e in nl._state["actors"].values() if e.get("shown")]
t = time.perf_counter()
for e in es:
    s = e["shown"]
    nl._apply_pose(e, s["pose"], s["sex"], False)
dt = time.perf_counter() - t
print("%d poses in %.1f ms (%.2f ms each)" % (len(es), dt * 1000, dt * 1000 / max(1, len(es))))
