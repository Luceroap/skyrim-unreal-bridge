"""Grass around the camera from area2/grass (tools/grass_world.py): Skyrim's GRAS scatter on the LAND texture layers.

update(live, cam_loc=None) every tick: tiles (1024 Skyrim units) within RADIUS of the camera are drawn, one actor per grass
model with two InstancedStaticMeshComponents: 'near' (tiles within NEAR_SHADOW, casts shadows) and 'far' (no shadows), both
with per-instance cull distances, no collision, out of ray tracing / distance fields. The packet's worldspace picks the
data (WORLDS: Tamriel = 'Skyrim', city worldspaces with their own LAND); interiors and other worldspaces clear the layer.
Missing models are requested through live.request (live_bridge.import_ready imports them, then they are built). Cheap while the camera stays inside the same tile: one tuple
compare. When the tile set changes the affected components are rebuilt, at most REBUILDS_PER_CALL per call.
clear(live) removes everything. State lives on the Live instance (live._grass), so reloading this module keeps track."""
import ctypes, json, math, os, time
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
GRASS = os.path.join(AREA, "grass")
U = 1.4287
RADIUS = 5600.0                 # Skyrim units (~80 m)
NEAR_SHADOW = 1500.0            # tiles closer than this (~21 m) cast shadows
CULL = (6500, 8200)             # cm: per-instance fade start / end
REBUILDS_PER_CALL = 6
# packet worldspace FULL name -> data folder under area2/grass ('' = Tamriel; others: grass_world.py --world <edid>)
WORLDS = {"skyrim": "", "tamriel": "", "whiterun": "whiterunworld", "solitude": "solitudeworld",
          "windhelm": "windhelmworld", "markarth": "markarthworld", "riften": "riftenworld"}
WS_OFFSET = 236                 # packet: struct.calcsize("<4I21f2I64s64s") -> worldspaceName[64]


def _log(msg):
    unreal.log("[SkyBridgeGrass] " + msg)


def _state(live):
    st = live.__dict__.get("_grass")
    if st is None:
        st = live._grass = {"index": None, "cells": {}, "key": None, "tiles": {}, "actors": {}, "built": {},
                            "dirty": set(), "missing": set(), "t_missing": 0.0, "t_ws": 0.0, "ds": None,
                            "mat_done": set(), "err": None}
    return st


def _dir(st):
    return os.path.join(GRASS, st["ds"]) if st["ds"] else GRASS


def _index(st):
    if st["index"] is None:
        p = os.path.join(_dir(st), "index.json")
        st["index"] = json.load(open(p)) if os.path.exists(p) else {}
    return st["index"]


def _dataset(live, st):
    """Grass data folder for the packet's worldspace (None: no grass there), re-read every 0.5 s. A change of worldspace
    clears the layer and loads that world's data."""
    now = time.time()
    if now - st["t_ws"] > 0.5:
        st["t_ws"] = now
        try:
            name = ctypes.string_at(live.pkt + WS_OFFSET, 64).split(b"\0")[0].decode("latin1").lower() if live.pkt else ""
        except Exception:
            name = ""
        ds = WORLDS.get(name)
        if ds != st["ds"]:
            clear(live)
            st.update(ds=ds, index=None, cells={})
    return st["ds"]


def _cell(st, gx, gy):
    k = (gx, gy)
    if k not in st["cells"]:
        p = os.path.join(_dir(st), "cell_%d_%d.json" % k)
        st["cells"][k] = json.load(open(p)) if os.path.exists(p) else {}
    return st["cells"][k]


def _foliage(st, comp):
    """Grass cards: two-sided, alpha-masked, two-sided-foliage shading (remaster_materials.npc_hair does exactly that)."""
    import remaster_materials
    for i in range(comp.get_num_materials()):
        mi = comp.get_material(i)
        if not isinstance(mi, unreal.MaterialInstanceConstant) or not mi.get_name().startswith("MI_"):
            continue
        if mi.get_name() in st["mat_done"]:
            continue
        st["mat_done"].add(mi.get_name())
        o = mi.get_editor_property("base_property_overrides")
        if o.get_editor_property("override_two_sided") and o.get_editor_property("override_shading_model") and \
                o.get_editor_property("override_blend_mode"):
            continue
        remaster_materials.npc_hair(mi)


def _actor(live, st, name, mesh):
    a = st["actors"].get(name)
    if a is not None:
        return a
    act = live.spawn(unreal.Actor)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root = sds.k2_gather_subobject_data_for_instance(act)[0]
    for _ in range(2):
        sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.InstancedStaticMeshComponent))
    comps = act.get_components_by_class(unreal.InstancedStaticMeshComponent)
    for i, c in enumerate(comps[:2]):
        c.set_static_mesh(mesh)
        live.fix_slots(c, mesh)
        _foliage(st, c)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_cull_distances(CULL[0], CULL[1])
        c.set_cast_shadow(i == 0)
        for prop, val in (("visible_in_ray_tracing", False), ("affect_distance_field_lighting", False),
                          ("affect_dynamic_indirect_lighting", False)):
            try:
                c.set_editor_property(prop, val)
            except Exception:
                pass
    act.set_actor_label("Grass_" + name[:60])
    act.set_folder_path("SkyBridge/Grass")
    st["actors"][name] = a = (act, comps[0], comps[1])
    return a


def _wanted(idx, sx, sy):
    """{(tx, ty): near?} for tiles whose centre is within RADIUS (+ half a tile) of the camera."""
    T = idx["tile"]
    r = int(math.ceil(RADIUS / T)) + 1
    cx, cy = int(math.floor(sx / T)), int(math.floor(sy / T))
    out = {}
    for ty in range(cy - r, cy + r + 1):
        for tx in range(cx - r, cx + r + 1):
            d = math.hypot((tx + .5) * T - sx, (ty + .5) * T - sy)
            if d <= RADIUS + T * 0.5:
                out[(tx, ty)] = d <= NEAR_SHADOW + T * 0.5
    return out


def _tile_items(st, idx, t):
    T = idx["tile"]
    gx, gy = int(math.floor(t[0] * T / 4096.0)), int(math.floor(t[1] * T / 4096.0))
    return _cell(st, gx, gy).get("%d_%d" % t, ())


def update(live, cam_loc=None):
    st = _state(live)
    try:
        _update(live, st, cam_loc)
    except Exception as e:
        import traceback
        tb = traceback.extract_tb(e.__traceback__)[-1]
        if str(e) != st["err"]:
            st["err"] = str(e)
            _log("error: %s (%s line %d)" % (e, tb.name, tb.lineno))


def _update(live, st, cam_loc):
    if getattr(live, "_interior", False) or _dataset(live, st) is None:
        if st["actors"] or st["tiles"]:
            clear(live)
        return
    idx = _index(st)
    if not idx or not idx.get("models"):
        return
    if cam_loc is None:
        cam_loc = live.ues.get_level_viewport_camera_info()[0]
    sx, sy = cam_loc.y / U, cam_loc.x / U                     # UE (x, y) = Skyrim (y, x) * U
    T = idx["tile"]
    key = (int(math.floor(sx / T)), int(math.floor(sy / T)))
    now = time.time()
    if st["missing"] and now - st["t_missing"] > 3.0:          # models converted/imported since: build them
        st["t_missing"] = now
        for name in list(st["missing"]):
            if live.mesh(name) is not None:
                st["missing"].discard(name); st["dirty"].add(name)
    if key != st["key"]:
        st["key"] = key
        want = _wanted(idx, sx, sy)
        if want != st["tiles"]:
            changed = {t for t in set(want) | set(st["tiles"]) if want.get(t) != st["tiles"].get(t)}
            models = idx["models"]
            for t in changed:
                for it in _tile_items(st, idx, t):
                    st["dirty"].add(models[it[0]]["name"])
            st["tiles"] = want
    if not st["dirty"]:
        return
    models = idx["models"]
    budget = REBUILDS_PER_CALL
    for name in sorted(st["dirty"]):
        if budget <= 0:
            break
        st["dirty"].discard(name)
        mesh = live.mesh(name)
        if mesh is None:
            if live.mesh_cache.get(name) is not False:
                nif = next(m["nif"] for m in models if m["name"] == name)
                live.request(name, nif)
                st["missing"].add(name)
            continue
        near, far = [], []
        for t, is_near in st["tiles"].items():
            for m, x, y, z, yaw, s in _tile_items(st, idx, t):
                if models[m]["name"] != name:
                    continue
                (near if is_near else far).append(unreal.Transform(unreal.Vector(y * U, x * U, z * U),
                                                                   unreal.Rotator(yaw=90.0 + yaw), unreal.Vector(s, s, s)))
        if not near and not far and name not in st["actors"]:
            continue
        _act, cn, cf = _actor(live, st, name, mesh)
        for c, xs in ((cn, near), (cf, far)):
            c.clear_instances()
            if xs:
                c.add_instances(xs, False, True)
        st["built"][name] = (len(near), len(far))
        budget -= 1
    keep = {(int(math.floor(t[0] * T / 4096.0)), int(math.floor(t[1] * T / 4096.0))) for t in st["tiles"]}
    for k in [k for k in st["cells"] if k not in keep]:       # drop cell data far from the camera
        st["cells"].pop(k)


def clear(live):
    st = live.__dict__.get("_grass")
    if not st:
        return
    for act, _n, _f in st["actors"].values():
        try:
            act.destroy_actor()
        except Exception:
            pass
    st.update(actors={}, built={}, tiles={}, key=None, dirty=set(), cells={})


def stats(live):
    """(instances near, far, models built, tiles) for debugging."""
    st = live.__dict__.get("_grass") or {}
    b = st.get("built", {})
    return sum(n for n, _ in b.values()), sum(f for _, f in b.values()), len(st.get("actors", {})), len(st.get("tiles", {}))
