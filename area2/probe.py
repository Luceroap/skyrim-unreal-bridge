import json, collections
A = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
rep = []
# 1. game refs in Whiterun not drawn
d = json.load(open(A + r"\world_whiterunworld.json"))
drawn_ids = set(live.actors) | set(live.preview) | set(live.city) | set(getattr(live, "distant_built", ()))
pos_by_model = collections.defaultdict(list)
for x in live.actors.values(): pos_by_model[x["model"]].append(x["pos"])
fx = lambda m: m.startswith(("effects/", "fx")) or "/fx" in m
reasons = collections.defaultdict(list)
for x in d:
    if x["id"] in drawn_ids: continue
    m = x["nif"]
    if x["disabled"]: r = "disabled in game data"
    elif x["parent"]: r = "enable-parented (quest/state)"
    elif fx(m): r = "effect"
    elif "marker" in m and not any(k in m for k in live.REAL_MARKERS): r = "invisible marker"
    elif x["type"] in live.LOOSE_ITEMS: r = "loose item (stream only)"
    elif any(live.near(p, x["pos"]) for p in pos_by_model.get(m, [])): r = "moved by mod (stream has it)"
    elif not unreal.EditorAssetLibrary.does_asset_exist("/Game/Area2/" + x["model"]): r = "NO MESH"
    else: r = "MISSING (mesh exists)"
    reasons[r].append(m)
rep.append("== Whiterun game refs not drawn ==")
for r, l in sorted(reasons.items(), key=lambda kv: -len(kv[1])):
    rep.append("%-32s %4d  %s" % (r, len(l), collections.Counter(l).most_common(6) if r in ("NO MESH", "MISSING (mesh exists)", "loose item (stream only)") else ""))
# 2. stream refs stuck
rep.append("== stream queue: %d ==" % len(live.spawn_queue))
rep.append(str(collections.Counter(q[1] for q in live.spawn_queue)))
# 3. untextured slots on drawn actors
bad = collections.Counter()
for a in [x["actor"] for x in live.actors.values()] + list(live.city.values()) + list(live.preview.values()):
    c = a.static_mesh_component
    for i in range(c.get_num_materials()):
        mt = c.get_material(i)
        n = mt.get_name() if mt else "None"
        if not n.startswith(("MI_", "M_Hidden", "M_SkyWater")):
            bad[(c.static_mesh.get_name() if c.static_mesh else "?", n)] += 1
rep.append("== untextured slots: %d distinct ==" % len(bad))
for k, v in bad.most_common(25): rep.append("   %3d %s" % (v, k))
# 4. MIs with missing base colour
mis = unreal.EditorAssetLibrary.list_assets("/Game/Area2Tex", recursive=False)
nobase = []
for p in mis:
    if "/MI_" not in p: continue
    mi = unreal.load_asset(p.split(".")[0])
    t = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mi, "BaseColor")
    if not t or "Default" in t.get_name(): nobase.append(p.split("/")[-1].split(".")[0])
rep.append("== MIs without a colour map: %d %s" % (len(nobase), nobase[:30]))
# 5. distant + lights
rep.append("== distant models left to build: %d %s" % (len(getattr(live, "distant_todo", [])), list(getattr(live, "distant_todo", []))[:10]))
r = live.read_world()
rep.append("== lights streamed %s drawn %d" % (r[1][6] if r else "?", len(live.light_actors)))
open(A + r"\audit.txt", "w").write("\n".join(rep)); print("\n".join(rep))
