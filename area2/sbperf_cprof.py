"""cProfile live.tick_body for N frames, then write the top functions to area2/sbperf_cprof.txt and restore."""
import sys, time, cProfile, pstats, io
P = sys.modules.setdefault("_sbperf2", type(sys)("_sbperf2"))
P.prof = cProfile.Profile(); P.left = 40; P.t0 = time.perf_counter(); P.walls = []
orig = live.tick_body
def body(dt):
    t = time.perf_counter()
    P.prof.enable()
    try:
        return orig(dt)
    finally:
        P.prof.disable()
        P.walls.append((dt, time.perf_counter() - t))
        P.left -= 1
        if P.left <= 0:
            try: del live.tick_body
            except AttributeError: pass
            s = io.StringIO()
            el = time.perf_counter() - P.t0
            s.write("frames %d in %.1fs; body avg %.1f ms; dt avg %.1f ms\n" % (len(P.walls), el,
                    1000 * sum(b for d, b in P.walls) / len(P.walls), 1000 * sum(d for d, b in P.walls) / len(P.walls)))
            s.write("bodies ms: %s\n" % " ".join("%.0f" % (1000 * b) for d, b in P.walls))
            pstats.Stats(P.prof, stream=s).sort_stats("cumulative").print_stats(45)
            pstats.Stats(P.prof, stream=s).sort_stats("tottime").print_stats(30)
            open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\sbperf_cprof.txt", "w").write(s.getvalue())
live.tick_body = body
print("cprofile armed")
