import sys, time
P = sys.modules["_sbperf"]
el = time.perf_counter() - P.t0
fr = P.frames
if fr:
    dts = sorted(d for d, b in fr)
    py = sum(b for d, b in fr)
    print("window %.1fs  ticks %d  fps %.1f  frame dt avg %.1f ms  p50 %.1f  p95 %.1f  max %.1f" % (
        el, len(fr), len(fr) / el, 1000 * sum(dts) / len(dts), 1000 * dts[len(dts) // 2], 1000 * dts[int(len(dts) * .95)], 1000 * dts[-1]))
    print("python tick_body: %.1f ms/frame avg (%.0f%% of frame time)" % (1000 * py / len(fr), 100 * py / max(1e-9, sum(dts))))
for k in sorted(P.t, key=lambda k: -P.t[k]):
    print("  %-22s %7.1f ms/s  %6.2f ms/call  %d calls" % (k, 1000 * P.t[k] / el, 1000 * P.t[k] / P.n[k], P.n[k]))
if "stop" in globals().get("ARGS", "stop"):
    P.restore()
    print("restored")
