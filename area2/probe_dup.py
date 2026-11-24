city, prev, acts = getattr(live, "city", {}), live.preview, live.actors
print("city", len(city), "preview", len(prev), "streamed", len(acts))
print("city&preview ids", len(set(city) & set(prev)), "city&streamed", len(set(city) & set(acts)), "preview&streamed", len(set(prev) & set(acts)))
def key(a):
    p = a.get_actor_location(); m = a.static_mesh_component.static_mesh
    return (m.get_name() if m else None, round(p.x / 20), round(p.y / 20), round(p.z / 20))
groups = {}
for src, d in (("city", city), ("preview", prev)):
    for rid, a in d.items():
        groups.setdefault(key(a), []).append((src, rid))
for rid, cur in acts.items():
    groups.setdefault(key(cur["actor"]), []).append(("stream", rid))
dups = {k: v for k, v in groups.items() if len(v) > 1}
from collections import Counter
print("same mesh+spot groups", len(dups), Counter(tuple(sorted(s for s, _ in v)) for v in dups.values()))
