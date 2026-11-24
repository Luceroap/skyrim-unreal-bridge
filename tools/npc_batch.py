"""Build FBXs for every named NPC currently loaded in Skyrim (reads the actor stream) that has none yet.
  python -I npc_batch.py [max]     (Skyrim must be running with the bridge plugin)"""
import ctypes, ctypes.wintypes as wt, os, struct, subprocess, sys

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
EXPORT = os.path.join(ROOT, "area2", "npc", "export")
k = ctypes.windll.kernel32
k.OpenFileMappingW.restype = ctypes.c_void_p
k.MapViewOfFile.restype = ctypes.c_void_p
k.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
h = k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_actors_v1")
if not h:
    sys.exit("actors mapping not found (Skyrim not running with the plugin)")
p = k.MapViewOfFile(h, 4, 0, 0, 0)
nA = struct.unpack("<8I", ctypes.string_at(p, 32))[4]
APOSE, OFF = 180 + 320 * 32, 32 + 512 * 40
gear = {}                                                         # actor ref id -> worn armor addon model paths
gh = k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_gear_v1")
if gh:
    gp = k.MapViewOfFile(gh, 4, 0, 0, 0)
    gn = struct.unpack("<5I", ctypes.string_at(gp, 20))[4]
    GSZ = 32 + 24 * 112 + 2 * 112 + 24 * 200
    swaps = {}                                                    # actor ref id -> {gear model path: "shape=texture;..."}
    slots = {}
    creature = {}
    face = {}                                                     # actor ref id -> face NPC (guards use a template NPC's baked head)
    for i in range(gn):
        gb = ctypes.string_at(gp + 32 + i * GSZ, GSZ)
        gid, gbase, cnt, gfl, gface = struct.unpack_from("<5I", gb, 0)
        slots[gid] = struct.unpack_from("<I", gb, 24)[0]            # worn biped slot mask (helmets hide the baked hair)
        creature[gid] = struct.unpack_from("<I", gb, 28)[0]         # 1 = non-humanoid: paths are its body-skin meshes
        gear[gid] = [gb[32 + j * 112:32 + (j + 1) * 112].split(b"\0")[0].decode("latin1") for j in range(cnt)]
        face[gid] = gface
        sw0 = 32 + 24 * 112 + 2 * 112
        swaps[gid] = {gear[gid][j]: gb[sw0 + j * 200:sw0 + (j + 1) * 200].split(b"\0")[0].decode("latin1") for j in range(cnt)}
if not gh:
    creature = {}
force = "--force" in sys.argv
TRIED = os.path.join(ROOT, "area2", "npc", "tried.txt")             # attempted builds (so a failing one is not retried every pass by the autobuilder)
tried = set(open(TRIED).read().split()) if os.path.exists(TRIED) and "--autobuild" in sys.argv else set()
todo = []
creatures = []                                                    # (base, name, skeleton nif, body skin meshes) for non-humanoid actors
for i in range(nA):
    b = ctypes.string_at(p + OFF + i * APOSE, 180)
    refid = struct.unpack_from("<I", b, 0)[0]
    base, flags = struct.unpack_from("<2I", b, 4)
    skel = b[36:132].split(b"\0")[0].decode("latin1")
    name = b[132:180].split(b"\0")[0].decode("latin1")
    if flags & 1 or "%08x" % base in tried:                          # the player's own head is not a FaceGen file
        continue
    if os.path.exists(os.path.join(EXPORT, "npc_%08x.fbx" % base)) and not force:
        continue
    if not skel.startswith("actors/character/"):                     # creature: own skeleton, body = skin armor addons reported by the plugin
        if skel and creature.get(refid) and gear.get(refid) and all(c[0] != base for c in creatures):
            if refid in swaps:
                import json as _json
                _json.dump(swaps[refid], open(os.path.join(ROOT, "area2", "npc", "swaps_%08x.json" % base), "w"))
            creatures.append((base, name, skel, gear[refid]))
        continue
    if refid in swaps:                                            # texture overrides for this actor's armor (read by npc_build.py)
        import json as _json
        os.makedirs(os.path.join(ROOT, "area2", "npc"), exist_ok=True)
        _json.dump(swaps[refid], open(os.path.join(ROOT, "area2", "npc", "swaps_%08x.json" % base), "w"))
    todo.append((base, "female" if flags & 4 else "male", name, gear.get(refid, []), face.get(refid, base), slots.get(refid, 0)))
only = next((a[7:].lower() for a in sys.argv[1:] if a.startswith("--only=")), None)      # e.g. --only=guard
if only:
    todo = [t for t in todo if only in t[2].lower()]
nums = [a for a in sys.argv[1:] if a.isdigit()]
limit = int(nums[0]) if nums else 6
if only:
    creatures = [c for c in creatures if only in c[1].lower()]
for base, name, skel, g in creatures[:limit]:
    print("building creature %08x %s (%s, %d body meshes)" % (base, name, skel, len(g)), flush=True)
    open(TRIED, "a").write("%08x\n" % base)
    r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "npc_build_creature.py"), "%08x" % base, skel, *g], capture_output=True, text=True)
    print("  ", (r.stdout.strip().splitlines() or ["(no output)"])[-1][:160], r.stderr.strip()[-160:])
for base, sex, name, g, fc, sl in todo[:limit]:
    print("building %08x %s (%s) with %d gear models, face %08x, worn slots 0x%x" % (base, name, sex, len(g), fc, sl), flush=True)
    open(TRIED, "a").write("%08x\n" % base)
    r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "npc_build.py"), "%08x" % base, sex, "--face=%08x" % fc, "--slots=%x" % sl, *g], capture_output=True, text=True)
    print("  ", (r.stdout.strip().splitlines() or ["(no output)"])[-1][:160], r.stderr.strip()[-160:])
