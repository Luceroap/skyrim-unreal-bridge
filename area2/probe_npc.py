import time, sys
nl = sys.modules.get("npc_live")
st = nl._state
print("npcs:", len(st["actors"]), [e["actor"].get_actor_label() for e in st["actors"].values()])
acts = nl.read_actors()
t0 = time.perf_counter(); nl.read_actors(); t_read = time.perf_counter() - t0
import live_bridge as lb
times = []
for a in acts:
    e = st["actors"].get(a["id"])
    if not e: continue
    t0 = time.perf_counter(); nl._pose(e, a, "female" if a["flags"] & 4 else "male", lb); times.append(time.perf_counter() - t0)
print("read_actors %.1f ms; pose per npc ms:" % (t_read * 1000), ["%.1f" % (t * 1000) for t in times])
# stream rate: sample header seq for 1 s
import ctypes, struct
p = st["map"]; seqs = set(); t0 = time.perf_counter()
while time.perf_counter() - t0 < 1.0:
    seqs.add(struct.unpack_from("<I", ctypes.string_at(p + 8, 4))[0]); time.sleep(0.002)
print("stream updates in 1 s:", len([s for s in seqs if not s & 1]))
# moving actors: speeds
for a in acts:
    e = st["actors"].get(a["id"])
    if e: print("  %-20s speed %.0f u/s" % (a["name"], e.get("speed", 0)))
print("frame dt (live):", getattr(live, "_dt", None))
