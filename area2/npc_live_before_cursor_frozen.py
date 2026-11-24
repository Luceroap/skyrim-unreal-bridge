"""NPCs in the live Unreal scene: imports area2/npc/export/npc_<baseId>.fbx (tools/npc_build.py) as skeletal meshes and poses them from
Skyrim's actor stream (Local\\SkyrimUnrealBridge_actors_v1, shared/BridgeShared.h). Called from live_bridge's tick: npc_live.tick(live).

Pose math. The FBX mesh is in 'imported space' u = F*k*v (F = diag(1,-1,1) mirror from the Blender/FBX path, k = 1.4287 cm per Skyrim unit),
and an actor is placed like any static: UE = A*u + pos with A = C*R*F^-1 (live_bridge.ue_rotation). The streamed bone X_i = (R_i, p_i) is WORLD space; the
actor's own placement is the streamed root node 'NPC'. In the rest pose (skeleton_<sex>.json) bone i has world (R0_i, p0_i). Local delta
  Rl = Rroot^T R_i,  pl = Rroot^T (p_i - p_root),  Rd = Rl R0_i^T,  td = pl - Rd p0_i
then in imported space the bone's component-space pose is  rot = (F Rd F) * RB0_i,  loc = (F Rd F) * tB0_i + k F td,  where (RB0_i, tB0_i)
is the bone's reference pose read from the imported mesh."""
import ctypes, glob, json, math, os, re, shutil, struct, time
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
EXPORT = os.path.join(AREA, "npc", "export")
U = 1.4287
MAX_NPCS = 12
CREATURE_SLOTS = 6                   # of those, up to this many are reserved for the nearest creatures
RADIUS = 5200.0                      # Skyrim units from the camera (~75 m)
POSES_PER_FRAME = 5                  # limb updates per editor frame (~0.5-1 ms each), most overdue first
UPDATE_HZ = 60.0                     # stream polls; the stream itself is ~30 Hz, motion in between is interpolated every frame
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


BONE = struct.Struct("<Hh3f4f")


def parse_bones(a):
    """Bones of an actor returned by read_actors(lazy=True) (parsing every actor's ~134 bones costs ~3 ms per frame)."""
    if a["bones"] is None:
        buf, o, nb, names = a.pop("_raw")
        n = len(names)
        a["bones"] = {names[ni]: ((x, y, z), (qx, qy, qz, qw))
                      for ni, par, x, y, z, qx, qy, qz, qw in BONE.iter_unpack(buf[o + 180:o + 180 + nb * 32]) if ni < n}
    return a["bones"]


def read_actors(cam=None, radius=None, lazy=False):
    """All actors; with cam/radius only actors within radius get their bones parsed; lazy: none (call parse_bones)."""
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
        table = buf[32:32 + hdr[5] * NAMELEN]
        if _state.get("name_table") != table:
            _state["name_table"] = table
            _state["names"] = [table[i * NAMELEN:(i + 1) * NAMELEN].split(b"\0")[0].decode("latin1") for i in range(hdr[5])]
        names = _state["names"]
        actors = []
        for i in range(nA):
            o = POSES_OFF + i * APOSE
            id_, base, flags, nb = struct.unpack_from("<4I", buf, o)
            pos = struct.unpack_from("<3f", buf, o + 16)
            nm = buf[o + 132:o + 180].split(b"\0")[0].decode("latin1")
            a = dict(id=id_, base=base, flags=flags, pos=pos, name=nm, bones=None, _raw=(buf, o, min(nb, MAXBONES), names),
                     skel=buf[o + 36:o + 132].split(b"\0")[0].decode("latin1"), scale=struct.unpack_from("<f", buf, o + 32)[0])
            if not lazy:
                if cam is not None and math.dist(pos, cam) > radius:
                    a["bones"] = {}; del a["_raw"]
                else:
                    parse_bones(a)
            actors.append(a)
        _state["seq"] = s0
        return actors
    return None


def skel_key(a):
    """'male'/'female' for the human skeletons; otherwise a file-name key from the race skeleton nif path (creatures: area2/npc/skin/skeleton_<key>.json)."""
    s = a.get("skel", "")
    if not s or s.startswith("actors/character/"):
        return "female" if a["flags"] & 4 else "male"
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def rest_pose(sex):                       # `sex` is really the skeleton key (see skel_key)
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


_SKIN = re.compile(r"(female|male)(body|head|hands|feet)|_facetint_|skin|argonian|khajiit")
_CARDS = ("hair", "brow", "beard", "lash", "scalp", "eyes_", "_eyes")


def _alias(slot):
    p = os.path.join(AREA, "npc", "tex_alias.json")                   # tools/npc_tex_alias.py: slots whose file name is shared by other paths
    try:
        mt = os.path.getmtime(p)
        if _state.get("alias_mt") != mt:
            _state["alias"], _state["alias_mt"] = json.load(open(p)), mt
    except Exception:
        return None
    s = slot.lower()
    return _state["alias"].get(s) or next((v for k, v in _state["alias"].items() if k.startswith(s) and len(s) >= 50), None)


def _material_for_slot(slot):
    import ue_assets
    import remaster_materials
    stem = _alias(slot)
    d = os.path.join(AREA, "tex") if stem else None
    if not stem:
        d, stem = _png_for_slot(slot)
    if not stem:
        return None
    m = _material_for_stem(slot, d, stem)
    if isinstance(m, unreal.MaterialInstanceConstant):
        low = slot.lower()
        try:
            if any(k in low for k in _CARDS):
                remaster_materials.npc_hair(m)
            elif _SKIN.search(low):
                remaster_materials.npc_skin(m)
        except Exception as e:
            log("npc material setup failed for %s: %s" % (slot, e))
    return m


def _material_for_stem(slot, d, stem):
    import ue_assets
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


def _is_bind(bones, rest, rq):
    """True when every limb bone sits at the SAME angle from its rest pose (a pure root rotation): the skeleton is un-animated."""
    rq_c = qconj(rq)
    restq = _state.setdefault("restq", {})
    angs = []
    for raw in LIMBS:
        if raw in bones and raw in rest:
            q0 = restq.get((id(rest), raw))
            if q0 is None:
                q0 = restq[(id(rest), raw)] = qconj(mat_to_quat(rest[raw][0]))
            w = qmul(qmul(rq_c, bones[raw][1]), q0)[3]
            angs.append(math.degrees(2.0 * math.acos(min(1.0, abs(w)))))
    return len(angs) >= 4 and (max(angs) - min(angs)) < 6.0


def _ingest(entry, a_info, now):
    """New stream sample for this actor: pick the pose to show and append (t, root, pose) to its short history.
    A pose is (bones, root quat, root pos); bones are world space but only their offset from that root is used, so a pose
    taken from any frame or actor can be shown at any root."""
    bones = a_info["bones"]
    root = bones.get("NPC") or bones.get("skeleton.nif") or (next(iter(bones.values())) if bones else None)   # creatures: first bone of the tree
    if not root:
        return False
    rp, rq = root
    entry["scale"] = a_info.get("scale", 1.0) or 1.0              # actor scale (dragons, giants, ...): bones are streamed scaled, the mesh is scaled by the actor
    sex = skel_key(a_info)                                        # skeleton key: male / female / creature race (rest pose json)
    rest = rest_pose(sex)
    lp = entry.get("lp")
    if lp is None:
        entry["lp"] = (rp, now); entry["speed"] = 0.0
    elif now - lp[1] >= 0.25:                                   # root speed in Skyrim units/s, refreshed 4x per second
        entry["speed"] = math.dist(rp, lp[0]) / (now - lp[1]); entry["lp"] = (rp, now)
    moving = entry.get("speed", 0.0) > 25.0
    pose = (bones, rq, rp)
    # Skyrim stops animating actors it is not showing (outside its camera view / far away): their streamed skeleton is the bind pose, i.e. a T/A pose.
    # Keep the last real pose of that actor, or borrow a natural one from another animated actor of the same sex.
    if _is_bind(bones, rest, rq):
        # a walker borrows the LIVE pose of an animated walker (so the stride keeps cycling); a standing actor keeps its own last pose
        tpl = _state["template"]
        pose = (tpl.get((sex, True)) if moving else entry.get("snap")) or entry.get("snap") or tpl.get((sex, moving)) or tpl.get((sex, False)) or pose
    else:
        entry["snap"] = pose
        _state["template"][(sex, moving)] = pose                # animated walkers feed the walking template, standing ones the idle one
    hist = entry.setdefault("hist", [])
    if hist:
        gap = now - hist[-1]["t"]
        if gap < 0.25:                                          # editor hitches would inflate the stream interval
            entry["dt"] = 0.8 * entry.get("dt", gap) + 0.2 * gap
        if math.dist(rp, hist[-1]["rp"]) > 300.0:              # teleport / load door: do not glide across the map
            hist.clear()
    hist.append(dict(t=now, rp=rp, rq=rq, pose=pose, sex=sex))
    del hist[:-16]                                              # enough to bridge a stream pause while rt catches up
    return True


def _apply_pose(entry, pose, sex, far):
    comp = entry["comp"]
    bones, rq, rp = pose
    qa = qflip(qconj(rq))
    RrT = tr(quat_to_mat(*rq))
    M = [RrT[i] * FLIP[i // 3] for i in range(9)]                  # F * Rroot^T
    ks = U / (entry.get("scale", 1.0) or 1.0)                      # streamed bone offsets include the actor scale; the mesh is scaled by the actor instead
    batch = hasattr(unreal.SkyBridgeViewLibrary, "apply_pose")     # C++: one pass + render refresh (see SkyBridgeViewLibrary.h)
    names, tfs = [], []
    tf = unreal.Transform()
    for name, un, d, H, minor in _plan(entry, sex):
        if far and minor:
            continue
        b = bones.get(name)
        if b is None:
            continue
        p, q = b
        v = qrot(q, d)
        w = (v[0] + ks * (p[0] - rp[0]), v[1] + ks * (p[1] - rp[1]), v[2] + ks * (p[2] - rp[2]))
        r = qmul(qa, qmul(qflip(q), H))
        loc = unreal.Vector(M[0] * w[0] + M[1] * w[1] + M[2] * w[2], M[3] * w[0] + M[4] * w[1] + M[5] * w[2],
                            M[6] * w[0] + M[7] * w[1] + M[8] * w[2])
        if batch:
            t = unreal.Transform()
            t.translation, t.rotation = loc, unreal.Quat(*r)
            names.append(un)
            tfs.append(t)
        else:
            tf.translation = loc
            tf.rotation = unreal.Quat(*r)
            comp.set_bone_transform_by_name(un, tf, unreal.BoneSpaces.COMPONENT_SPACE)
    if batch:
        unreal.SkyBridgeViewLibrary.apply_pose(comp, names, tfs)


def _smooth(entry, now, dist, lb):
    """Every editor frame: place the actor between its last two stream samples (shown ~one stream interval late, so motion is
    continuous instead of stepping at the stream rate), and switch the limbs to the sample nearest that time."""
    hist = entry.get("hist")
    if not hist or not _ensure_rest(entry):
        return None
    # Playback clock rt runs ~delay behind the newest sample. When the stream pauses (Skyrim hitches stall it for ~0.3 s)
    # rt slows down instead of running into the newest sample and freezing, then catches up (up to 2x) instead of jumping.
    delay = min(0.2, max(0.04, 1.6 * entry.get("dt", 0.05)))
    newest = hist[-1]["t"]
    rt = entry.get("rt")
    if rt is None or abs(newest - rt) > 1.0:
        rt = newest - delay
    else:
        rate = max(0.0, min(2.0, 1.0 + (newest - rt - delay) / (2.0 * delay)))
        rt = min(newest, rt + (now - entry.get("rt_wall", now)) * rate)
    rt = max(rt, hist[0]["t"])
    entry["rt"], entry["rt_wall"] = rt, now
    t = rt
    i = 0
    while i + 1 < len(hist) and hist[i + 1]["t"] <= t:
        i += 1
    a = hist[i]
    if i + 1 < len(hist) and t > a["t"]:
        b = hist[i + 1]
        f = min(1.0, (t - a["t"]) / max(1e-4, b["t"] - a["t"]))
    else:
        b, f = a, 0.0
    rp = [a["rp"][k] + (b["rp"][k] - a["rp"][k]) * f for k in range(3)]
    rq = qnlerp(a["rq"], b["rq"], f)
    entry["actor"].set_actor_location_and_rotation(unreal.Vector(rp[1] * U, rp[0] * U, rp[2] * U),
                                                   lb.ue_rotation(quat_to_mat(*rq)), False, False)
    sc = entry.get("scale", 1.0) or 1.0
    if abs(sc - entry.get("scale_set", 1.0)) > 0.01:               # only meaningful for scaled actors (dragons, giants, ...)
        entry["actor"].set_actor_scale3d(unreal.Vector(sc, sc, sc)); entry["scale_set"] = sc
    s = b if f >= 0.5 else a
    if s is not entry.get("shown") and now - entry.get("posed_t", 0.0) >= _pose_gap(dist) * 0.9:
        return s                                                   # limbs due: tick picks which NPCs get posed this frame
    return None


def _pose_gap(dist):
    """Seconds between limb updates: every stream sample near, fewer far away."""
    return 1.0 / 30 if dist < 1500 else (1.0 / 12 if dist < 3000 else 1.0 / 6)


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
    """Every editor frame: smooth each NPC between stream samples. When the stream has a new frame (seq changed, ~30 Hz,
    checked at most UPDATE_HZ): read it, spawn/despawn, record the samples."""
    import live_bridge as lb
    now = time.time()
    if now - _state["last"] >= 1.0 / UPDATE_HZ and live.pkt is not None:
        _state["last"] = now
        seq = stream_seq()
        if seq is not None and seq != _state.get("seq"):
            _read_and_spawn(live, lb, now)
    for e in _state["actors"].values():
        e["due"] = _smooth(e, now, e.get("dist", 0.0), lb)
    # limb updates: the most overdue first (relative to each NPC's distance-based rate), so near NPCs cannot starve far ones
    due = [e for e in _state["actors"].values() if e.get("due")]
    due.sort(key=lambda e: -(now - e.get("posed_t", 0.0)) / _pose_gap(e.get("dist", 0.0)))
    for e in due[:POSES_PER_FRAME]:
        s = e["due"]
        _apply_pose(e, s["pose"], s["sex"], e.get("dist", 0.0) > 700)    # beyond ~10 m fingers/toes/body-physics bones are not visible
        e["shown"], e["posed_t"] = s, now


def _has_fbx(base):
    """os.path.exists per actor per frame was ~10% of the NPC time; new FBXs (npc_batch) are picked up within 10 s."""
    c = _state.setdefault("fbx_cache", {})
    hit = c.get(base)
    now = time.time()
    if hit is None or (not hit[0] and now - hit[1] > 10.0):
        hit = c[base] = (os.path.exists(os.path.join(EXPORT, "npc_%08x.fbx" % base)), now)
    return hit[0]


def _read_and_spawn(live, lb, now):
    v = struct.unpack(lb.PKT_FMT, ctypes.string_at(live.pkt, lb.PKT_SIZE))
    cam = v[10:13]
    actors = read_actors(lazy=True)
    if actors is None:
        return
    want = []
    for a in actors:
        if a["flags"] & 1:                                                    # skip the player (first-person)
            continue
        d = math.dist(a["pos"], cam)
        if d <= RADIUS and _has_fbx(a["base"]):
            want.append((d, a))
    want.sort(key=lambda t: t[0])
    keep = set()
    imported_this_tick = 0
    gear = None
    chosen = []
    # creatures (wolves, dragons, ...) are rarer and matter more than the 12th townsperson: up to CREATURE_SLOTS of the nearest come first
    is_human = lambda a: a.get("skel", "").startswith("actors/character/") or not a.get("skel")
    ordered = [t for t in want if not is_human(t[1])][:CREATURE_SLOTS] + [t for t in want if is_human(t[1])]
    for d, a in ordered:
        if len(chosen) >= MAX_NPCS:
            break
        if parse_bones(a):                                                    # humanoids and creatures (creatures: first streamed bone is the root)
            chosen.append((d, a))
    for d, a in chosen:
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
        e["dist"] = d
        _ingest(e, a, now)
        try:
            gear = gear if gear is not None else read_gear()
            _weapon(e, a, gear, live, lb)
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
