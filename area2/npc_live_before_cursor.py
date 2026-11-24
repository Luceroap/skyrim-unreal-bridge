"""NPCs in the live Unreal scene: imports area2/npc/export/npc_<baseId>.fbx (tools/npc_build.py) as skeletal meshes and poses them from
Skyrim's actor stream (Local\\SkyrimUnrealBridge_actors_v1, shared/BridgeShared.h). Called from live_bridge's tick: npc_live.tick(live).

Pose math. The FBX mesh is in 'imported space' u = F*k*v (F = diag(1,-1,1) mirror from the Blender/FBX path, k = 1.4287 cm per Skyrim unit),
and an actor is placed like any static: UE = A*u + pos with A = C*R*F^-1 (live_bridge.ue_rotation). The streamed bone X_i = (R_i, p_i) is WORLD space; the
actor's own placement is the streamed root node 'NPC'. In the rest pose (skeleton_<sex>.json) bone i has world (R0_i, p0_i). Local delta
  Rl = Rroot^T R_i,  pl = Rroot^T (p_i - p_root),  Rd = Rl R0_i^T,  td = pl - Rd p0_i
then in imported space the bone's component-space pose is  rot = (F Rd F) * RB0_i,  loc = (F Rd F) * tB0_i + k F td,  where (RB0_i, tB0_i)
is the bone's reference pose read from the imported mesh."""
import ctypes, glob, json, math, os, shutil, struct, time
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
EXPORT = os.path.join(AREA, "npc", "export")
U = 1.4287
MAX_NPCS = 12
RADIUS = 5200.0                      # Skyrim units from the camera (~75 m)
UPDATE_HZ = 15.0
FLIP = (1.0, -1.0, 1.0)

k32 = ctypes.windll.kernel32
k32.OpenFileMappingW.restype = ctypes.c_void_p
k32.MapViewOfFile.restype = ctypes.c_void_p
k32.MapViewOfFile.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_size_t]

MAXB, NAMELEN, MAXBONES = 512, 40, 320
APOSE = 180 + MAXBONES * 32
POSES_OFF = 32 + MAXB * NAMELEN

_state = dict(map=None, meshes={}, actors={}, rest={}, last=0.0, import_budget_t=0.0, mats={}, failed=set(), template={})


def log(msg):
    unreal.log("[SkyBridgeLive] npc: " + msg)


# ---------------------------------------------------------------- small matrix helpers (row-major 3x3 lists)
def quat_to_mat(x, y, z, w):
    return [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
            2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
            2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]


def mat_to_quat(m):
    tr = m[0] + m[4] + m[8]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2; w = 0.25 * s; x = (m[7] - m[5]) / s; y = (m[2] - m[6]) / s; z = (m[3] - m[1]) / s
    elif m[0] > m[4] and m[0] > m[8]:
        s = math.sqrt(1.0 + m[0] - m[4] - m[8]) * 2; w = (m[7] - m[5]) / s; x = 0.25 * s; y = (m[1] + m[3]) / s; z = (m[2] + m[6]) / s
    elif m[4] > m[8]:
        s = math.sqrt(1.0 + m[4] - m[0] - m[8]) * 2; w = (m[2] - m[6]) / s; x = (m[1] + m[3]) / s; y = 0.25 * s; z = (m[5] + m[7]) / s
    else:
        s = math.sqrt(1.0 + m[8] - m[0] - m[4]) * 2; w = (m[3] - m[1]) / s; x = (m[2] + m[6]) / s; y = (m[5] + m[7]) / s; z = 0.25 * s
    return x, y, z, w


def mul(a, b):
    return [sum(a[r * 3 + k] * b[k * 3 + c] for k in range(3)) for r in range(3) for c in range(3)]


def tr(a):
    return [a[0], a[3], a[6], a[1], a[4], a[7], a[2], a[5], a[8]]


def mv(a, v):
    return [a[0] * v[0] + a[1] * v[1] + a[2] * v[2], a[3] * v[0] + a[4] * v[1] + a[5] * v[2], a[6] * v[0] + a[7] * v[1] + a[8] * v[2]]


def conj_flip(a):                          # F a F, F = diag(1,-1,1)
    return [a[r * 3 + c] * FLIP[r] * FLIP[c] for r in range(3) for c in range(3)]


# quaternions (x, y, z, w); qmul(a, b) <-> matrix a*b (same convention as quat_to_mat)
def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def qconj(a):
    return (-a[0], -a[1], -a[2], a[3])


def qflip(a):                              # F R F as a quaternion (mirror y): axis (x, y, z) -> (-x, y, -z)
    return (-a[0], a[1], -a[2], a[3])


def qrot(q, v):
    x, y, z, w = q
    tx = 2 * (y * v[2] - z * v[1]); ty = 2 * (z * v[0] - x * v[2]); tz = 2 * (x * v[1] - y * v[0])
    return (v[0] + w * tx + y * tz - z * ty, v[1] + w * ty + z * tx - x * tz, v[2] + w * tz + x * ty - y * tx)


def qnlerp(a, b, t):
    if a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3] < 0:
        b = (-b[0], -b[1], -b[2], -b[3])
    q = [a[i] + (b[i] - a[i]) * t for i in range(4)]
    n = math.sqrt(sum(c * c for c in q)) or 1.0
    return (q[0] / n, q[1] / n, q[2] / n, q[3] / n)


# ---------------------------------------------------------------- stream
def stream_seq():
    if _state["map"] is None:
        h = k32.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_actors_v1")
        if not h:
            return None
        _state["map"] = k32.MapViewOfFile(h, 4, 0, 0, 0)
    return struct.unpack_from("<I", ctypes.string_at(_state["map"] + 8, 4))[0]


def read_actors(cam=None, radius=None):
    """All actors; with cam/radius only actors within radius get their bones parsed (parsing ~30 x 134 bones costs ~3 ms)."""
    if stream_seq() is None:
        return None
    p = _state["map"]
    for _ in range(4):
        s0, = struct.unpack_from("<I", ctypes.string_at(p + 8, 4))
        if s0 & 1:
            continue
        hdr = struct.unpack("<8I", ctypes.string_at(p, 32))
        nA = min(hdr[4], 96)
        buf = ctypes.string_at(p, POSES_OFF + nA * APOSE)
        s1, = struct.unpack_from("<I", ctypes.string_at(p + 8, 4))
        if s0 != s1:
            continue
        names = [buf[32 + i * NAMELEN:32 + (i + 1) * NAMELEN].split(b"\0")[0].decode("latin1") for i in range(hdr[5])]
        actors = []
        for i in range(nA):
            o = POSES_OFF + i * APOSE
            id_, base, flags, nb = struct.unpack_from("<4I", buf, o)
            pos = struct.unpack_from("<3f", buf, o + 16)
            nm = buf[o + 132:o + 180].split(b"\0")[0].decode("latin1")
            bones = {}
            far = cam is not None and math.dist(pos, cam) > radius
            for j in range(0 if far else min(nb, MAXBONES)):
                ni, par, x, y, z, qx, qy, qz, qw = struct.unpack_from("<Hh3f4f", buf, o + 180 + j * 32)
                if ni < len(names):
                    bones[names[ni]] = ((x, y, z), (qx, qy, qz, qw))
            actors.append(dict(id=id_, base=base, flags=flags, pos=pos, name=nm, bones=bones))
        _state["seq"] = s0
        return actors
    return None


def rest_pose(sex):
    if sex not in _state["rest"]:
        d = {}
        try:
            for b in json.load(open(os.path.join(AREA, "npc", "skin", "skeleton_%s.json" % sex))):
                d[b["name"]] = (b["rot"], b["pos"])
        except Exception as e:
            log("no rest pose for %s: %s" % (sex, e))
        _state["rest"][sex] = d
    return _state["rest"][sex]


# ---------------------------------------------------------------- assets
def _png_for_slot(slot):
    nm = slot.lower().split(".0")[0]
    for d in (os.path.join(AREA, "npc", "tex"), os.path.join(AREA, "tex")):
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d), key=len, reverse=True):
            stem = f[:-4].lower()
            if f.endswith(".png") and not stem.endswith(("_n", "_s", "_rmaos")) and nm.endswith("_" + stem + "_dds"):
                return d, stem
    return None, None


def _material_for_slot(slot):
    import ue_assets
    d, stem = _png_for_slot(slot)
    if not stem:
        return None
    if d.endswith("tex") and os.path.basename(os.path.dirname(d)) == "npc":      # npc textures -> the shared texture folder
        for suffix in (".png", "_n.png", "_s.png", "_rmaos.png"):
            dst = os.path.join(AREA, "tex", stem + suffix)
            src = os.path.join(d, stem + suffix)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy(src, dst)
    m = ue_assets.material_for(stem)
    if m is None:
        return None
    if any(k in slot.lower() for k in ("hair", "brow", "beard", "lash", "scalp")):        # alpha-tested cards
        try:
            lst = os.path.join(AREA, "tex", "alpha_masked_extra.txt")            # read by remaster_materials.configure
            have = set(open(lst).read().split()) if os.path.exists(lst) else set()
            if stem not in have:
                with open(lst, "a") as f:
                    f.write(stem + "\n")
            import remaster_materials
            if isinstance(m, unreal.MaterialInstanceConstant):
                remaster_materials.configure(m, stem)
            else:
                m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        except Exception as e:
            log("masked material failed for %s: %s" % (slot, e))
    return m


def mesh_for(base):
    key = "%08x" % base
    if key in _state["meshes"]:
        return _state["meshes"][key]
    path = "/Game/Npc/npc_" + key
    fbx = os.path.join(EXPORT, "npc_%s.fbx" % key)
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        if not os.path.exists(fbx) or key in _state["failed"]:
            return None
        ui = unreal.FbxImportUI()
        for k, v in (("import_mesh", True), ("import_as_skeletal", True), ("import_materials", False), ("import_textures", False),
                     ("import_animations", False), ("create_physics_asset", False),
                     ("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)):
            ui.set_editor_property(k, v)
        t = unreal.AssetImportTask()
        t.filename = fbx; t.destination_path = "/Game/Npc"; t.automated = True; t.replace_existing = True; t.save = False
        t.options = ui
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    mesh = unreal.load_asset(path)
    if not isinstance(mesh, unreal.SkeletalMesh):
        _state["failed"].add(key)
        log("import failed for %s" % key)
        return None
    mats = list(mesh.get_editor_property("materials"))
    for sm in mats:
        mat = _material_for_slot(str(sm.material_slot_name))
        if mat is not None:
            sm.set_editor_property("material_interface", mat)
    mesh.set_editor_property("materials", mats)
    _state["meshes"][key] = mesh
    log("ready: %s (%d bones, %d materials)" % (key, 0, len(mats)))
    return mesh


# ---------------------------------------------------------------- actors
def _spawn(a_info, mesh, lb):
    world = unreal.EditorLevelLibrary
    actor = world.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0), unreal.Rotator())
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root = sds.k2_gather_subobject_data_for_instance(actor)[0]
    sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.PoseableMeshComponent))
    comp = actor.get_components_by_class(unreal.PoseableMeshComponent)[0]
    comp.set_skinned_asset_and_update(mesh)
    comp.set_editor_property("cast_shadow", True)
    actor.set_actor_label("NPC_" + a_info["name"].replace(" ", "_"))
    actor.set_folder_path("SkyBridge/NPCs")
    entry = dict(actor=actor, comp=comp, rest0={}, names=set(), ready=False)
    _ensure_rest(entry)
    return entry


def _ensure_rest(entry):
    """Read the reference pose of EVERY bone once, before any bone is moved (a child's component-space transform changes when its parent moves).
    A freshly imported mesh builds its skeleton asynchronously: until get_num_bones() > 0 nothing can be read or posed."""
    if entry["ready"]:
        return True
    comp = entry["comp"]
    n = comp.get_num_bones()
    if n <= 0:
        return False
    names = set(str(comp.get_bone_name(i)) for i in range(n))
    rest0, rest0q = {}, {}
    for nm in names:
        t0 = comp.get_bone_transform_by_name(nm, unreal.BoneSpaces.COMPONENT_SPACE)
        qq = t0.rotation
        rest0[nm] = (quat_to_mat(qq.x, qq.y, qq.z, qq.w), (t0.translation.x, t0.translation.y, t0.translation.z))
        rest0q[nm] = ((qq.x, qq.y, qq.z, qq.w), rest0[nm][1])
    entry["names"], entry["rest0"], entry["rest0q"], entry["ready"] = names, rest0, rest0q, True
    return True


def _plan(entry, sex):
    """Per-bone constants of the pose math (module docstring), folded so a bone costs two quaternion products + two vector ops:
    rot = qflip(conj(q_root)) * qflip(q_i) * H,       H = qflip(conj(q_R0)) * q_RB0
    loc = F Rroot^T (R_i d + k (p_i - p_root)),     d = R0^T (F tB0 - k p0)"""
    if entry.get("plan_sex") == sex:
        return entry["plan"]
    plan = []
    for name, (R0, p0) in rest_pose(sex).items():
        un = ue_bone(name)
        if un not in entry["rest0q"]:
            continue
        qRB0, tB0 = entry["rest0q"][un]
        H = qmul(qflip(qconj(mat_to_quat(R0))), qRB0)
        c = (FLIP[0] * tB0[0] - U * p0[0], FLIP[1] * tB0[1] - U * p0[1], FLIP[2] * tB0[2] - U * p0[2])
        minor = any(k in name for k in ("Finger", "Toe", "Breast", "Butt", "Belly", "Anus", "Pussy", "Genitals"))
        plan.append((name, un, mv(tr(R0), c), H, minor))
    entry["plan"], entry["plan_sex"] = plan, sex
    return plan


def ue_bone(name):
    """Unreal's FBX import renames bones: spaces -> '-', '[' and ']' -> '_'  ('NPC Root [Root]' -> 'NPC-Root-_Root_')."""
    return name.replace(" ", "-").replace("[", "_").replace("]", "_")


LIMBS = ("NPC L UpperArm [LUar]", "NPC R UpperArm [RUar]", "NPC L Forearm [LLar]", "NPC L Thigh [LThg]", "NPC R Thigh [RThg]", "NPC L Calf [LClf]")


def _is_bind(bones, rest, RrT):
    """True when every limb bone sits at the SAME angle from its rest pose (a pure root rotation): the skeleton is un-animated."""
    angs = []
    for raw in LIMBS:
        if raw in bones and raw in rest:
            rel = mul(mul(RrT, quat_to_mat(*bones[raw][1])), tr(rest[raw][0]))
            angs.append(math.degrees(math.acos(max(-1.0, min(1.0, (rel[0] + rel[4] + rel[8] - 1.0) / 2.0)))))
    return len(angs) >= 4 and (max(angs) - min(angs)) < 6.0


def _pose(entry, a_info, sex, lb):
    comp, actor = entry["comp"], entry["actor"]
    if not _ensure_rest(entry):
        return False                                                         # skeleton still building: try again next tick
    bones = a_info["bones"]
    rest = rest_pose(sex)
    root = bones.get("NPC") or bones.get("skeleton.nif")
    if not root:
        return False
    rp, rq = root
    Rr = quat_to_mat(*rq)
    RrT = tr(Rr)
    actor.set_actor_location_and_rotation(unreal.Vector(rp[1] * U, rp[0] * U, rp[2] * U), lb.ue_rotation(Rr), False, False)
    cache = entry["rest0"]
    # Skyrim stops animating actors it is not showing (outside its camera view / far away): their streamed skeleton is the bind pose, i.e. a T/A pose.
    # Keep the last real pose of that actor, or borrow a natural one from another animated actor of the same sex (always relative to the root).
    sex = "female" if a_info["flags"] & 4 else "male"
    now_t = time.time()
    lp = entry.get("lp")
    if lp is None:
        entry["lp"] = (rp, now_t); entry["speed"] = 0.0
    elif now_t - lp[1] >= 0.25:                                   # root speed in Skyrim units/s, refreshed 4x per second
        entry["speed"] = math.dist(rp, lp[0]) / (now_t - lp[1]); entry["lp"] = (rp, now_t)
    moving = entry.get("speed", 0.0) > 25.0
    if _is_bind(bones, rest, RrT):
        # a walker borrows the LIVE pose of an animated walker (so the stride keeps cycling); a standing actor keeps its own last pose
        local = (_state["template"].get((sex, True)) if moving else entry.get("local")) or entry.get("local") or _state["template"].get((sex, moving)) or _state["template"].get((sex, False))
        if local:
            rebuilt = {}
            for n, (Rl, pl) in local.items():
                R = mul(Rr, Rl)
                pw = mv(Rr, pl)
                rebuilt[n] = ((rp[0] + pw[0], rp[1] + pw[1], rp[2] + pw[2]), mat_to_quat(R))
            bones = rebuilt
    else:
        local = {n: (mul(RrT, quat_to_mat(*q)), mv(RrT, (p[0] - rp[0], p[1] - rp[1], p[2] - rp[2]))) for n, (p, q) in bones.items()}
        entry["local"] = local
        _state["template"][(sex, moving)] = local                  # animated walkers feed the walking template, standing ones the idle one
    for name, (p, q) in bones.items():
        if name not in rest or ue_bone(name) not in entry["names"]:
            continue
        uname = ue_bone(name)
        if uname not in cache:
            continue
        RB0, tB0 = cache[uname]
        R0, p0 = rest[name]
        Ri = quat_to_mat(*q)
        pl = mv(RrT, (p[0] - rp[0], p[1] - rp[1], p[2] - rp[2]))
        Rd = mul(mul(RrT, Ri), tr(R0))
        td = [pl[i] - v for i, v in enumerate(mv(Rd, p0))]
        Rdf = conj_flip(Rd)
        rot = mul(Rdf, RB0)
        loc = mv(Rdf, tB0)
        loc = (loc[0] + U * FLIP[0] * td[0], loc[1] + U * FLIP[1] * td[1], loc[2] + U * FLIP[2] * td[2])
        qx, qy, qz, qw = mat_to_quat(rot)
        tf = unreal.Transform()
        tf.translation = unreal.Vector(*loc)
        tf.rotation = unreal.Quat(qx, qy, qz, qw)
        comp.set_bone_transform_by_name(uname, tf, unreal.BoneSpaces.COMPONENT_SPACE)
    return True


_gear = dict(map=None, last=0.0, data={})
GEAR_SZ = 32 + 24 * 112 + 2 * 112 + 24 * 200


def read_gear():
    """Worn gear stream (~1 Hz): actor ref id -> dict(wfl, weapons=[right, left])."""
    now = time.time()
    if now - _gear["last"] < 1.0:
        return _gear["data"]
    _gear["last"] = now
    if _gear["map"] is None:
        h = k32.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_gear_v1")
        if not h:
            return _gear["data"]
        _gear["map"] = k32.MapViewOfFile(h, 4, 0, 0, 0)
    p = _gear["map"]
    n = min(struct.unpack("<5I", ctypes.string_at(p, 20))[4], 96)
    buf = ctypes.string_at(p, 32 + n * GEAR_SZ)
    d = {}
    for i in range(n):
        o = 32 + i * GEAR_SZ
        id_, base, cnt, flags, face, wfl = struct.unpack_from("<6I", buf, o)
        w = [buf[o + 32 + 24 * 112 + h * 112:o + 32 + 24 * 112 + (h + 1) * 112].split(b"\0")[0].decode("latin1") for h in range(2)]
        d[id_] = dict(wfl=wfl, weapons=w)
    _gear["data"] = d
    return d


def _weapon(entry, a, gear, live, lb):
    """Right-hand weapon as a rigid mesh on the streamed WEAPON node, only while the weapon is drawn."""
    g = gear.get(a["id"])
    path = g["weapons"][0] if g else ""
    node = a["bones"].get("WEAPON")
    want = bool(path and node and (a["flags"] & 8) and (g["wfl"] & 1) and not (g["wfl"] & 4))
    cur = entry.get("weapon")
    if not want:
        if cur:
            try: cur["actor"].destroy_actor()
            except Exception: pass
            entry["weapon"] = None
        return
    name = lb.Live.asset_name(path)
    mesh = live.mesh(name)
    if mesh is None:
        live.request(name, path)                                  # the asset service converts it; shows up on a later tick
        return
    p, q = node
    loc = unreal.Vector(p[1] * U, p[0] * U, p[2] * U)
    rot = lb.ue_rotation(quat_to_mat(*q))
    if cur is None or cur["path"] != path:
        if cur:
            try: cur["actor"].destroy_actor()
            except Exception: pass
        act = live.spawn(unreal.StaticMeshActor, loc, rot)
        act.static_mesh_component.set_static_mesh(mesh)
        act.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        act.set_folder_path("SkyBridge/NPCs")
        cur = entry["weapon"] = dict(actor=act, path=path)
    cur["actor"].set_actor_location_and_rotation(loc, rot, False, False)


def tick(live):
    now = time.time()
    if now - _state["last"] < 1.0 / UPDATE_HZ:
        return
    _state["last"] = now
    import live_bridge as lb
    actors = read_actors()
    if actors is None or live.pkt is None:
        return
    v = struct.unpack(lb.PKT_FMT, ctypes.string_at(live.pkt, lb.PKT_SIZE))
    cam = v[10:13]
    want = []
    for a in actors:
        if a["flags"] & 1 or "NPC" not in a["bones"]:                       # skip the player (first-person) and creatures
            continue
        d = math.dist(a["pos"], cam)
        if d <= RADIUS and os.path.exists(os.path.join(EXPORT, "npc_%08x.fbx" % a["base"])):
            want.append((d, a))
    want.sort(key=lambda t: t[0])
    keep = set()
    imported_this_tick = 0
    for d, a in want[:MAX_NPCS]:
        mesh = _state["meshes"].get("%08x" % a["base"])
        if mesh is None:
            if imported_this_tick:
                continue                                                      # one (slow) import per tick
            mesh = mesh_for(a["base"]); imported_this_tick += 1
            if mesh is None:
                continue
        e = _state["actors"].get(a["id"])
        if e is None:
            e = _state["actors"][a["id"]] = _spawn(a, mesh, lb)
        keep.add(a["id"])
        _pose(e, a, "female" if a["flags"] & 4 else "male", lb)
        try:
            _weapon(e, a, read_gear(), live, lb)
        except Exception as ex:
            if str(ex) != _state.get("werr"):
                _state["werr"] = str(ex); log("weapon error: %s" % ex)
    for aid in [k for k in _state["actors"] if k not in keep]:
        try:
            if _state["actors"][aid].get("weapon"):
                _state["actors"][aid]["weapon"]["actor"].destroy_actor()
            _state["actors"][aid]["actor"].destroy_actor()
        except Exception:
            pass
        del _state["actors"][aid]
