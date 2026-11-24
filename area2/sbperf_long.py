"""30 s window: cProfile the whole tick_body, list frames whose body took > 40 ms, write area2/sbperf_long.txt."""
import sys, time, cProfile, pstats, io
P = sys.modules.setdefault("_sbperf3", type(sys)("_sbperf3"))
P.prof = cProfile.Profile(); P.t0 = time.perf_counter(); P.walls = []; P.spikes = []
DUR = float(globals().get("DUR", 30))
orig = live.tick_body
def body(dt):
    t = time.perf_counter()
    sp = cProfile.Profile()
    sp.enable()
    try:
        return orig(dt)
    finally:
        sp.disable()
        b = time.perf_counter() - t
        P.walls.append((dt, b))
        P.prof.add = None
        st = pstats.Stats(sp)
        if b > 0.04:
            s = io.StringIO(); pstats.Stats(sp, stream=s).sort_stats("cumulative").print_stats(12)
            P.spikes.append((round(b * 1000), s.getvalue()[-2500:]))
        P.stats = st if not hasattr(P, "stats") else (P.stats.add(sp) or P.stats)
        if time.perf_counter() - P.t0 > DUR:
            try: del live.tick_body
            except AttributeError: pass
            el = time.perf_counter() - P.t0
            s = io.StringIO()
            bs = sorted(b for d, b in P.walls)
            s.write("window %.1fs ticks %d fps %.1f | body avg %.1f p50 %.1f p95 %.1f max %.0f ms | sum body %.1fs\n" % (
                el, len(P.walls), len(P.walls) / el, 1000 * sum(bs) / len(bs), 1000 * bs[len(bs) // 2],
                1000 * bs[int(len(bs) * .95)], 1000 * bs[-1], sum(bs)))
            s.write("spikes >40ms: %d  (%s)\n" % (len(P.spikes), " ".join(str(x[0]) for x in P.spikes)))
            P.stats.stream = s
            P.stats.sort_stats("cumulative").print_stats(35)
            for ms, txt in sorted(P.spikes, key=lambda x: -x[0])[:4]:
                s.write("\n===== spike %d ms\n%s" % (ms, txt))
            open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\sbperf_long.txt", "w").write(s.getvalue())
live.tick_body = body
print("long profile armed for %.0fs" % DUR)
