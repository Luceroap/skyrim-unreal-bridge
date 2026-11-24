src = open(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py").read().replace("\nstart()\n", "\n")
ns = {"__name__": "lb_patch"}
exec(src, ns)
for name in ("spawn_some", "city_some"):
    setattr(type(live), name, ns["Live"].__dict__[name])
L = type(live)
seen, n = [], 0
for rid in list(live.actors):
    d = live.actors[rid]
    if any(e["model"] == d["model"] and L.near(e["pos"], d["pos"], 3.0) and
           all(abs(x - y) < 0.01 for x, y in zip(e["rot"], d["rot"])) for e in seen):
        live.actors.pop(rid)["actor"].destroy_actor(); n += 1
    else:
        seen.append(d)
meta, kept, m = live.city_meta, [], 0
for rid in list(live.city):
    k = meta.get(rid)
    if k and any(k[0] == q[0] and L.near(k[1], q[1], 3.0) for q in kept):
        live.city.pop(rid).destroy_actor(); m += 1
    elif k:
        kept.append(k)
print("removed stream twins", n, "city twins", m)
