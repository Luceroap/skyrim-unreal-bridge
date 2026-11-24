import sys, time, cProfile, pstats, io
nl = sys.modules["npc_live"]
if "cprof" not in nl._state:
    pr = cProfile.Profile()
    orig = nl.tick
    def timed(live, _o=orig, _pr=pr):
        _pr.enable(); _o(live); _pr.disable()
    nl._state["cprof"] = (pr, orig)
    nl.tick = timed
    print("cprofile started")
else:
    pr, orig = nl._state.pop("cprof"); nl.tick = orig
    s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(18); print(s.getvalue()[:4000])
