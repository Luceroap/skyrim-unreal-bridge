import sys, time
nl = sys.modules["npc_live"]
if "prof" not in nl._state:
    orig = nl.tick
    def timed(live, _o=orig):
        t0 = time.perf_counter(); _o(live); p = nl._state["prof"]
        p["t"] += time.perf_counter() - t0; p["n"] += 1
    nl._state["prof"] = dict(t=0.0, n=0, start=time.time(), orig=orig)
    nl.tick = timed
    print("profiling started")
else:
    p = nl._state["prof"]; el = time.time() - p["start"]
    nl.tick = p["orig"]; del nl._state["prof"]
    print("npc tick: %.1f ms per second of wall time, %d calls/s, avg %.2f ms/call" % (p["t"] * 1000 / el, p["n"] / el, p["t"] * 1000 / max(1, p["n"])))
    for e in list(nl._state["actors"].values())[:12]:
        print("  %-28s dist %5.0f  stream dt %.3f  hist %d" % (e["actor"].get_actor_label(), e.get("dist", 0), e.get("dt", 0), len(e.get("hist", []))))
