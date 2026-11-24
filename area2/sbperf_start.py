"""Stability session profiler: wraps the main per-tick functions of `live` (instance attributes, no file edits) and
records time per call. Read + restore with sbperf_read.py."""
import sys, time
P = sys.modules.setdefault("_sbperf", type(sys)("_sbperf"))
if getattr(P, "restore", None):
    P.restore()
P.t = {}; P.n = {}; P.frames = []; P.t0 = time.perf_counter(); P.saved = []

def wrap(obj, name, key):
    orig = getattr(obj, name)
    def w(*a, **k):
        t = time.perf_counter()
        try:
            return orig(*a, **k)
        finally:
            d = time.perf_counter() - t
            P.t[key] = P.t.get(key, 0.0) + d; P.n[key] = P.n.get(key, 0) + 1
    setattr(obj, name, w)
    P.saved.append((obj, name, orig, obj is live))

orig_body = live.tick_body
def body(dt):
    t = time.perf_counter()
    try:
        return orig_body(dt)
    finally:
        P.frames.append((dt, time.perf_counter() - t))
live.tick_body = body
P.saved.append((live, "tick_body", orig_body, True))
for n in ("import_ready", "read_world", "apply_world", "spawn_some", "distant_some", "update_sky", "addons_tick"):
    if hasattr(live, n):
        wrap(live, n, n)
import atmosphere
wrap(atmosphere, "flicker", "atmosphere.flicker")
for m in ("npc_live", "tamriel_live"):
    if m in sys.modules:
        wrap(sys.modules[m], "tick", m + ".tick")
def restore():
    for obj, name, orig, inst in reversed(P.saved):
        if inst:
            try: delattr(obj, name)
            except AttributeError: pass
        else:
            setattr(obj, name, orig)
    P.saved = []
P.restore = restore
print("profiling on")
