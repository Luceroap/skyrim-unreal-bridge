import sys, time, math
nl = sys.modules["npc_live"]
st = nl._state
if "trace" not in st:
    orig = nl.tick
    def traced(live, _o=orig):
        _o(live)
        for aid, e in st["actors"].items():
            if e.get("speed", 0) > 25:
                l = e["actor"].get_actor_location()
                st["trace"].setdefault(aid, []).append((time.time(), l.x, l.y))
    st["trace"] = {}; st["trace_orig"] = orig; nl.tick = traced
    print("tracing walkers")
else:
    nl.tick = st.pop("trace_orig"); tr_ = st.pop("trace")
    for aid, pts in tr_.items():
        if len(pts) < 20: continue
        steps = [math.hypot(b[1] - a[1], b[2] - a[2]) for a, b in zip(pts, pts[1:])]
        still = sum(1 for s in steps if s < 0.05)
        mean = sum(steps) / len(steps)
        jerk = sum(abs(b - a) for a, b in zip(steps, steps[1:])) / max(1, len(steps) - 1)
        print("%s: %d frames, frames without motion %d%%, mean step %.1f cm, step variation %.1f cm" %
              (st["actors"][aid]["actor"].get_actor_label() if aid in st["actors"] else aid, len(pts), 100 * still // len(steps), mean, jerk))
        print("   steps:", " ".join("%.1f" % s for s in steps[:60]))
        print("   dts  :", " ".join("%.0f" % ((b[0] - a[0]) * 1000) for a, b in zip(pts[:30], pts[1:31])))
