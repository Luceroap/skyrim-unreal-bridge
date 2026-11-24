import sys, time, math
nl = sys.modules["npc_live"]
st = nl._state
if "htrace" not in st:
    orig = nl._ingest
    def ing(entry, a, now, _o=orig):
        r = _o(entry, a, now)
        if entry.get("speed", 0) > 25 and entry.get("hist"):
            h = entry["hist"][-1]
            st["htrace"].setdefault(entry["actor"].get_actor_label(), []).append((now, h["rp"]))
        return r
    st["htrace"] = {}; st["hing"] = orig; nl._ingest = ing
    print("tracing samples")
else:
    nl._ingest = st.pop("hing"); t = st.pop("htrace")
    for k, pts in t.items():
        dts = [b[0] - a[0] for a, b in zip(pts, pts[1:])]
        same = sum(1 for a, b in zip(pts, pts[1:]) if math.dist(a[1], b[1]) < 0.01)
        print("%s: %d samples, identical-to-previous %d, dt min %.3f max %.3f mean %.3f" % (k, len(pts), same, min(dts), max(dts), sum(dts) / len(dts)))
        print("   moves:", ["%.1f" % math.dist(a[1], b[1]) for a, b in zip(pts[:25], pts[1:26])])
