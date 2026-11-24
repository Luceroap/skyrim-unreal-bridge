import sys, time
nl = sys.modules["npc_live"]
for e in list(nl._state["actors"].values())[:6]:
    s = e.get("shown")
    if not s:
        continue
    t0 = time.perf_counter()
    for _ in range(5):
        nl._apply_pose(e, s["pose"], s["sex"], False)
    t1 = time.perf_counter()
    for _ in range(5):
        nl._apply_pose(e, s["pose"], s["sex"], True)
    t2 = time.perf_counter()
    print("%-24s near %.2f ms  far %.2f ms" % (e["actor"].get_actor_label()[:24], (t1 - t0) / 5 * 1e3, (t2 - t1) / 5 * 1e3))
