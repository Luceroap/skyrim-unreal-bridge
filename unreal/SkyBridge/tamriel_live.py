"""All of Tamriel in the editor (called from live_bridge's tick: tamriel_live.tick(live)).

Objects: every placed reference of the Tamriel worldspace (tools/tamriel_world.py -> area2/tamriel/*.json: forts, castles,
farms, villages, ruins, bridges, trees, rocks, plants...) as one instanced-mesh actor per model (folder SkyBridge/Tamriel),
nearest models first, with per-kind cull distances. The live stream skips the form ids drawn here (live.distant_built), so
loaded cells are not drawn twice; quest-dependent (enable-parented) refs, loose items and mod-added objects stay with the stream.
Pieces inside the city worldspaces' cells are separate actors that are hidden while you are in that city (the city
worldspace has its own copies).

Terrain (tools/tamriel_terrain.py --serve): low-res group meshes over the whole map (M_TerrainFar, baked 128 px/cell atlas by
world position) and full-res 4x4-cell chunks with 1024 px/cell textures around the camera; a loaded chunk hides its low-res
section (material slot -> M_Hidden). Water: Tamriel-wide strips (area2/tamriel/water_quads.csv) as one instanced actor.
Flag 'notamriel' in area2/debug_flags.txt turns the whole layer off (restart the editor to get the old distant layer back)."""
import glob, json, math, os, time
import unreal
import live_bridge as lb

AREA = lb.AREA
TAM = os.path.join(AREA, "tamriel")
U = lb.U
V = lb.V
CHUNK_UNITS = 4 * 4096
CHUNK_LOAD, CHUNK_DROP = 26000.0, 40000.0          # full-res terrain around the camera (Skyrim units from the chunk centre)
MAX_OUTSTANDING = 12                               # keep the live conversion backlog bounded; imports are expensive
TAMRIEL_NAMES = ("Skyrim", "Tamriel")              # worldspace FULL name the plugin reports for Tamriel
CITY_WORLDS = {"Whiterun": "whiterunworld", "Solitude": "solitudeworld", "Windhelm": "windhelmworld",
               "Markarth": "markarthworld", "Riften": "riftenworld"}


def log(msg):
    unreal.log("[SkyBridgeTamriel] " + msg)


def rot_from_angles(rx, ry, rz):
    """Same as RotFromAngles in plugin/src/main.cpp (tools/distant_world.py)."""
    ax, ay, az = -rx, -ry, -rz
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    X = [1, 0, 0, 0, cx, -sx, 0, sx, cx]; Y = [cy, 0, sy, 0, 1, 0, -sy, 0, cy]; Z = [cz, -sz, 0, sz, cz, 0, 0, 0, 1]
    mul = lambda A, B: [sum(A[i * 3 + k] * B[k * 3 + j] for k in range(3)) for i in range(3) for j in range(3)]
    return mul(mul(X, Y), Z)


def cull_for(nif):
    """End cull distance (cm, 0 = never) by model folder."""
    if nif.startswith(("landscape/mountains/", "landscape/cliffs/", "landscape/dirtcliffs/", "landscape/ice/",
                       "landscape/rocks/rockcliff", "architecture/", "dungeons/", "dlc01/", "dlc02/")):
        return 0
    if "/trees" in nif or nif.startswith("landscape/trees"):
        return 300000
    if "plants/" in nif or "/grass" in nif or "shrub" in nif or "fern" in nif:
        return 25000
    if nif.startswith("landscape/"):
        return 200000
    return 60000


def instanced_actor(live, mesh, label, folder):
    a = live.spawn(unreal.Actor)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root = sds.k2_gather_subobject_data_for_instance(a)[0]
    sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.InstancedStaticMeshComponent))
    c = a.get_components_by_class(unreal.InstancedStaticMeshComponent)[0]
    c.set_static_mesh(mesh)
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    a.set_actor_label(label[:80]); a.set_folder_path(folder)
    return a, c


def import_fbx(fbx, dest):
    t = unreal.AssetImportTask()
    t.filename = fbx; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", True); ui.set_editor_property("import_as_skeletal", False)
    ui.set_editor_property("import_materials", False); ui.set_editor_property("import_textures", False)
    sd = ui.get_editor_property("static_mesh_import_data")
    for k, v in (("combine_meshes", True), ("generate_lightmap_u_vs", False), ("auto_generate_collision", False),
                 ("build_nanite", True)):
        try:
            sd.set_editor_property(k, v)
        except Exception:
            pass
    try:
        sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    except Exception:
        pass
    t.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])


FAR_HLSL = """
float sx = W.y / 1.4287; float sy = W.x / 1.4287;
return float2((sx - O.x) / 65536.0, 1.0 - (sy - O.y) / 65536.0);
"""
FAR_COLOR_HLSL = """
float up = saturate((N - 0.6) * 4.0);
float3 c = C * lerp(1.0, 0.65, Wet * up);
return lerp(c, float3(0.85, 0.87, 0.9), Snow * up);
"""


def far_material():
    """M_TerrainFar: atlas texture placed by world position (no UVs needed), wet darkening and snow cover from MPC_Weather."""
    path = "/Game/Area2Tex/M_TerrainFar"
    eal = unreal.EditorAssetLibrary
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    import remaster_materials as rm
    mel, E, MP = unreal.MaterialEditingLibrary, unreal, unreal.MaterialProperty
    m = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_TerrainFar", "/Game/Area2Tex", unreal.Material,
                                                                  unreal.MaterialFactoryNew())
    m.set_editor_property("two_sided", True)
    mpc = rm.weather_collection()
    wp = rm._e(m, E.MaterialExpressionWorldPosition, -1400, 0)
    org = rm._e(m, E.MaterialExpressionVectorParameter, -1400, 150, parameter_name="Origin")
    uv = rm._e(m, E.MaterialExpressionCustom, -1150, 50, code=FAR_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT2,
               description="AtlasUV")
    ins = []
    for n in ("W", "O"):
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    uv.set_editor_property("inputs", ins)
    mel.connect_material_expressions(wp, "", uv, "W"); mel.connect_material_expressions(org, "", uv, "O")
    tex = rm._e(m, E.MaterialExpressionTextureSampleParameter2D, -900, 0, parameter_name="Atlas",
                texture=unreal.load_asset("/Engine/EngineResources/DefaultTexture"))
    mel.connect_material_expressions(uv, "", tex, "UVs")
    vn = rm._e(m, E.MaterialExpressionVertexNormalWS, -900, 300)
    nz = rm._e(m, E.MaterialExpressionComponentMask, -750, 300, r=False, g=False, b=True, a=False)
    mel.connect_material_expressions(vn, "", nz, "")
    wet = rm._e(m, E.MaterialExpressionCollectionParameter, -750, 400, collection=mpc, parameter_name="Wetness")
    snow = rm._e(m, E.MaterialExpressionCollectionParameter, -750, 500, collection=mpc, parameter_name="Snow")
    col = rm._e(m, E.MaterialExpressionCustom, -500, 100, code=FAR_COLOR_HLSL, output_type=E.CustomMaterialOutputType.CMOT_FLOAT3,
                description="FarColor")
    ins = []
    for n in ("C", "N", "Wet", "Snow"):
        ci = E.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    col.set_editor_property("inputs", ins)
    mel.connect_material_expressions(tex, "RGB", col, "C"); mel.connect_material_expressions(nz, "", col, "N")
    mel.connect_material_expressions(wet, "", col, "Wet"); mel.connect_material_expressions(snow, "", col, "Snow")
    mel.connect_material_property(col, "", MP.MP_BASE_COLOR)
    rough = rm._e(m, E.MaterialExpressionLinearInterpolate, -500, 400, const_a=0.92, const_b=0.45)
    mel.connect_material_expressions(wet, "", rough, "Alpha")
    mel.connect_material_property(rough, "", MP.MP_ROUGHNESS)
    for flag in ("used_with_nanite", "used_with_instanced_static_meshes"):
        try: m.set_editor_property(flag, True)
        except Exception: pass
    mel.recompile_material(m); eal.save_loaded_asset(m)
    log("built M_TerrainFar")
    return m


def far_instance(GX, GY):
    import remaster_materials as rm
    key = "tatl_%d_%d" % (GX, GY)
    path = "/Game/Area2Tex/MI_" + key
    eal, mel = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
    if eal.does_asset_exist(path):
        return unreal.load_asset(path)
    tex = rm._import_tex(key, "color")
    if not tex:
        return None
    mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset("MI_" + key, "/Game/Area2Tex", unreal.MaterialInstanceConstant,
                                                                   unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, far_material())
    mel.set_material_instance_texture_parameter_value(mi, "Atlas", tex)
    mel.set_material_instance_vector_parameter_value(mi, "Origin", unreal.LinearColor(GX * 65536.0, GY * 65536.0, 0, 0))
    mel.update_material_instance(mi); eal.save_loaded_asset(mi)
    return mi


class Tamriel:
    def __init__(self, live):
        self.live = live
        t0 = time.time()
        self.models = json.load(open(os.path.join(TAM, "models.json")))
        city = json.load(open(os.path.join(TAM, "city_cells.json")))
        cell_city = {}
        for edid, cells in city.items():
            for c in cells:
                cell_city[c] = edid
        groups = {}
        files = [os.path.join(TAM, "mountains.json")] + glob.glob(os.path.join(TAM, "f_*.json")) + \
            glob.glob(os.path.join(TAM, "n_*.json"))
        for p in files:
            for it in json.load(open(p)):
                tag = cell_city.get("%d,%d" % (math.floor(it[2] / 4096), math.floor(it[3] / 4096)), "")
                groups.setdefault((it[1], tag), []).append(it)
        self.groups = groups
        self.sample = {k: [(it[2], it[3]) for it in v[::max(1, len(v) // 32)]] for k, v in groups.items()}
        self.todo = list(groups)
        self._sort_cam = None
        self.built = {}                                  # (model index, tag) -> actor
        self.asked = set()
        self.failed = set()
        self.state_key = None
        self._sort_t = self._feed_t = 0.0
        self._fin = set()
        # take over from the Whiterun-only distant layer: same refs, map-wide here
        for a in getattr(live, "distant_actors", []):
            a.destroy_actor()
        live.distant_actors = []
        live.distant_todo = []
        live.distant = {}
        live.distant_built = set()
        # terrain
        self.low_names = open(os.path.join(TAM, "terrain_low.txt")).read().split() \
            if os.path.exists(os.path.join(TAM, "terrain_low.txt")) else []
        self.low = {}                                    # group name -> (actor, component, {slot: index})
        self.chunks = {}                                 # chunk name -> actor
        self.chunk_asked = set()
        self.terrain_actors = []
        self.water = None
        self._chunk_t = 0.0
        log("loaded %d references in %d model groups (%.1fs); %d low-res terrain groups" %
            (sum(len(v) for v in groups.values()), len(groups), time.time() - t0, len(self.low_names)))

    # ------------------------------------------------------------ helpers
    def cam(self):
        return getattr(self.live, "cam_sky", None)

    def dist2(self, key, cam):
        return min((x - cam[0]) ** 2 + (y - cam[1]) ** 2 for x, y in self.sample[key])

    def finished(self):
        """Models the asset service has finished (ready or failed), re-read every few seconds."""
        if time.time() - getattr(self, "_fin_t", 0) > 5.0:
            self._fin_t = time.time()
            fin = set()
            for n in ("ready.txt", "failed.txt"):
                p = os.path.join(AREA, n)
                if os.path.exists(p):
                    s = set(open(p).read().split())
                    fin |= s
                    if n == "failed.txt":
                        self.failed = s
            self._fin = fin
        return self._fin

    def feed(self, cam):
        """Ask the asset service for the nearest unconverted models, at most MAX_OUTSTANDING at a time."""
        if time.time() - self._feed_t < 5.0:
            return
        self._feed_t = time.time()
        live, fin = self.live, self.finished()
        outstanding = [n for n in self.asked if n not in fin]
        room = MAX_OUTSTANDING - len(outstanding)
        if room <= 0:
            return
        new = {}
        for key in self.todo:
            name, nif = self.models[key[0]]
            if name in new or name in self.asked or live.mesh(name) is not None:
                continue
            if name in fin:                                          # converted earlier, never imported: let import_ready take it
                if name not in self.failed:
                    live.requested.add(name); getattr(live, "prefetch", set()).discard(name)
                self.asked.add(name)
                continue
            new[name] = nif
            if len(new) >= room:
                break
        if not new:
            return
        self.asked |= set(new)
        live.requested |= set(new)
        getattr(live, "prefetch", set()).difference_update(new)
        live.model_paths.update(new)
        with open(os.path.join(AREA, "models.json"), "w") as f:
            json.dump(live.model_paths, f)
        with open(os.path.join(AREA, "requests.txt"), "a") as f:
            f.write("".join(n + "\n" for n in new))

    # ------------------------------------------------------------ objects
    def build_some(self, cam):
        if cam and time.time() - self._sort_t > 10.0 and (self._sort_cam is None or
                                                          abs(cam[0] - self._sort_cam[0]) + abs(cam[1] - self._sort_cam[1]) > 3000):
            self._sort_t, self._sort_cam = time.time(), tuple(cam[:2])
            self.todo.sort(key=lambda k: self.dist2(k, cam))
        live = self.live
        for _ in range(min(6, len(self.todo))):
            key = self.todo.pop(0)
            name, nif = self.models[key[0]]
            m = live.mesh(name)
            if m is None:
                if name not in self.failed and live.mesh_cache.get(name) is not False:
                    self.todo.append(key)                          # not converted yet: back of the queue
                continue
            items = self.groups[key]
            a, c = instanced_actor(live, m, "Tam_%s%s" % (name, "_" + key[1] if key[1] else ""), "SkyBridge/Tamriel")
            live.fix_slots(c, m)
            live.water_slots(c, nif)
            cd = cull_for(nif)
            if cd:
                c.set_cull_distances(0, cd)
            xs = [unreal.Transform(V(it[3] * U, it[2] * U, it[4] * U), lb.ue_rotation(rot_from_angles(it[5], it[6], it[7])),
                                   V(it[8], it[8], it[8])) for it in items]
            c.add_instances(xs, False, True)
            if self.hidden(key[1]):
                a.set_is_temporarily_hidden_in_editor(True)
            self.built[key] = a
            ids = {it[0] for it in items}
            live.distant_built.update(ids)
            for rid in [r for r in getattr(live, "preview", {}) if r in ids]:
                live.preview.pop(rid).destroy_actor()             # the large-ref preview had the same piece
            return

    def hidden(self, tag):
        interior, ws = self.state_key or (True, "")
        if interior or (ws not in TAMRIEL_NAMES and ws not in CITY_WORLDS):
            return True
        return bool(tag) and CITY_WORLDS.get(ws) == tag

    def update_visibility(self):
        live = self.live
        key = (bool(getattr(live, "_interior", False)), getattr(live, "ws_name", ""))
        if key == self.state_key:
            return
        if key[1] != (self.state_key or (None, None))[1]:
            log("worldspace: %r" % key[1])
        self.state_key = key
        for (mi, tag), a in self.built.items():
            a.set_is_temporarily_hidden_in_editor(self.hidden(tag))
        off = self.hidden("")
        for a in self.terrain_actors + list(self.chunks.values()):
            a.set_is_temporarily_hidden_in_editor(off)
        if self.water:
            self.water.set_is_temporarily_hidden_in_editor(off)

    # ------------------------------------------------------------ terrain
    def terrain_step(self, cam):
        live, eal = self.live, unreal.EditorAssetLibrary
        for name in self.low_names:                                  # low-res groups: one import per tick
            if name in self.low:
                continue
            path = "/Game/Tamriel/" + name
            if not eal.does_asset_exist(path):
                fbx = os.path.join(AREA, "export", name + ".fbx")
                if not os.path.exists(fbx):
                    continue
                import_fbx(fbx, "/Game/Tamriel")
            mesh = unreal.load_asset(path)
            _, gx, gy = name.split("_")
            mi = far_instance(int(gx), int(gy))
            slots = {}
            for i, sm in enumerate(mesh.static_materials):
                slots[str(sm.material_slot_name)] = i
            a = live.spawn(unreal.StaticMeshActor, V(0, 0, 0), unreal.Rotator(yaw=90))
            c = a.static_mesh_component
            c.set_static_mesh(mesh)
            if mi:
                for i in slots.values():
                    c.set_material(i, mi)
            a.set_actor_label("TamrielLow_" + name[4:]); a.set_folder_path("SkyBridge/TamrielTerrain")
            if self.hidden(""):
                a.set_is_temporarily_hidden_in_editor(True)
            self.low[name] = (a, c, slots, mi)
            self.terrain_actors.append(a)
            if len(self.low) == len(self.low_names):
                self.drop_old_lod()
            return True
        if self.water is None and os.path.exists(os.path.join(TAM, "water_quads.csv")):
            self.spawn_water(); return True
        if not cam or self.hidden("") or time.time() - self._chunk_t < 1.0:
            return False                                             # interiors sit at unrelated coordinates
        self._chunk_t = time.time()
        return self.chunk_step(cam)

    def drop_old_lod(self):
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if isinstance(a, unreal.StaticMeshActor) and str(a.get_folder_path()) == "SkyBridge/Terrain":
                m = a.static_mesh_component.static_mesh
                if m and m.get_name() == "lodterrain":
                    a.destroy_actor()
                    log("old LOD terrain removed (the Tamriel low-res terrain covers it)")

    def low_slot(self, chunk, show_low):
        """Hide/show the low-res section of a chunk (material slot 'tlo_<cx>_<cy>' of its 16x16-cell group)."""
        _, cx, cy = chunk.split("_")
        group = "tlo_%d_%d" % (int(cx) // 4, int(cy) // 4)
        g = self.low.get(group)
        if not g:
            return
        _, c, slots, mi = g
        i = slots.get("tlo_%s_%s" % (cx, cy))
        if i is None:
            return
        import ue_assets
        c.set_material(i, mi if show_low else ue_assets.hidden_material())

    def chunk_step(self, cam):
        live, eal = self.live, unreal.EditorAssetLibrary
        ccx, ccy = math.floor(cam[0] / CHUNK_UNITS), math.floor(cam[1] / CHUNK_UNITS)
        want = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                cx, cy = ccx + dx, ccy + dy
                d = math.hypot((cx + .5) * CHUNK_UNITS - cam[0], (cy + .5) * CHUNK_UNITS - cam[1])
                if d < CHUNK_LOAD:
                    want.append((d, "tch_%d_%d" % (cx, cy)))
        want.sort()
        for name in list(self.chunks):                               # unload far chunks
            _, cx, cy = name.split("_")
            if math.hypot((int(cx) + .5) * CHUNK_UNITS - cam[0], (int(cy) + .5) * CHUNK_UNITS - cam[1]) > CHUNK_DROP:
                a = self.chunks.pop(name)
                if a: a.destroy_actor()
                self.low_slot(name, True)
        new = [n for _, n in want if n not in self.chunk_asked]
        if new:
            self.chunk_asked |= set(new)
            with open(os.path.join(TAM, "terrain_requests.txt"), "a") as f:
                f.write("".join(n + "\n" for n in new))
        ready = set(open(os.path.join(TAM, "terrain_ready.txt")).read().split()) \
            if os.path.exists(os.path.join(TAM, "terrain_ready.txt")) else set()
        for _, name in want:
            if name in self.chunks or name not in ready:
                continue
            fbx = os.path.join(AREA, "export", name + ".fbx")
            if not os.path.exists(fbx):
                self.chunks[name] = None                             # no LAND there (ocean edge / Whiterun's own terrain)
                continue
            path = "/Game/Tamriel/" + name
            if not eal.does_asset_exist(path):
                import_fbx(fbx, "/Game/Tamriel")
            mesh = unreal.load_asset(path)
            key = "tdet_" + name[4:]
            import ue_assets
            mi = ue_assets.material_for(key)
            a = live.spawn(unreal.StaticMeshActor, V(0, 0, 0), unreal.Rotator(yaw=90))
            a.static_mesh_component.set_static_mesh(mesh)
            if mi:
                a.static_mesh_component.set_material(0, mi)
            a.set_actor_label("TamrielChunk_" + name[4:]); a.set_folder_path("SkyBridge/TamrielTerrain")
            if self.hidden(""):
                a.set_is_temporarily_hidden_in_editor(True)
            self.chunks[name] = a
            self.low_slot(name, False)
            return True                                              # one import per tick
        return False

    def spawn_water(self):
        live = self.live
        plane = unreal.load_asset("/Engine/BasicShapes/Plane.Plane")
        wmat = unreal.load_asset("/Game/Area2Tex/M_SkyWater")
        a, c = instanced_actor(live, plane, "TamrielWater", "SkyBridge/Water")
        c.set_material(0, wmat); c.set_cast_shadow(False)
        xs = []
        for line in open(os.path.join(TAM, "water_quads.csv")).read().split():
            x0, y0, n, h = line.split(",")
            x0, y0, n, h = int(x0), int(y0), int(n), float(h)
            if n == 0:                                               # whole cell
                xs.append(unreal.Transform(V((y0 + 2048) * U, (x0 + 2048) * U, h * U), unreal.Rotator(0, 0, 0),
                                           V(4096 * U / 100, 4096 * U / 100, 1)))
            else:
                xs.append(unreal.Transform(V((y0 + 64) * U, (x0 + n * 64) * U, h * U), unreal.Rotator(0, 0, 0),
                                           V(128 * U / 100, n * 128 * U / 100, 1)))
        c.add_instances(xs, False, True)
        self.water = a
        if self.hidden(""):
            a.set_is_temporarily_hidden_in_editor(True)
        log("Tamriel water: %d strips" % len(xs))

    # ------------------------------------------------------------ tick
    def tick(self):
        cam = self.cam()
        self.update_visibility()
        if self.terrain_step(cam):
            return                                                   # one heavy editor operation per tick
        if cam:
            self.feed(cam)
        self.build_some(cam)


_layer = None


def tick(live):
    global _layer
    if _layer is None:
        if not os.path.exists(os.path.join(TAM, "models.json")) or getattr(live, "cam_sky", None) is None:
            return
        _layer = Tamriel(live)
        live._tamriel_on = True
    _layer.tick()
