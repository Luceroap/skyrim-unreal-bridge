"""Build one creature (wolf, dragon, draugr, cow, ...) as a skinned FBX for Unreal from its race skeleton + body-skin meshes.
  python -I npc_build_creature.py <actor base form id hex> <skeleton nif (rel. to meshes/)> <body skin addon nif> [more nifs...]
Output: area2/npc/export/npc_<id>.fbx and area2/npc/skin/skeleton_<key>.json (key = skeleton path with non-alphanumerics -> '_'; the Unreal side
reads the same key). Texture overrides, if the plugin reported any, come from area2/npc/swaps_<id>.json (written by npc_batch.py)."""
import json, os, re, subprocess, sys

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
PY = sys.executable
T = os.path.join(ROOT, "tools")
AREA = os.path.join(ROOT, "area2")
NPC = os.path.join(AREA, "npc")

fid = sys.argv[1].lower().zfill(8)
skeleton = sys.argv[2].replace("\\", "/").lower()
gear = [a.replace("\\", "/") for a in sys.argv[3:] if not a.startswith("--")]
key = re.sub(r"[^a-z0-9]+", "_", skeleton).strip("_")


def run(*a):
    return subprocess.run([PY, "-W", "ignore", "-I", *a], capture_output=True, text=True)


# 1. extract the skeleton and the body meshes, convert the skeleton's rest pose
run(os.path.join(T, "npc_extract.py"), DATA, AREA, *["meshes\\" + p.replace("/", "\\") for p in [skeleton] + gear])
base = os.path.join(NPC, "nif")
skel_json = os.path.join(NPC, "skin", "skeleton_%s.json" % key)
src = os.path.join(base, skeleton.replace("/", "\\"))
if not os.path.exists(src):
    sys.exit("skeleton nif not found: " + skeleton)
if not os.path.exists(skel_json):
    print(run(os.path.join(T, "npc_skin.py"), "skeleton", src, skel_json).stdout.strip())

# 2. skinned meshes
gear_jsons = []
sw_file = os.path.join(NPC, "swaps_%s.json" % fid)
swaps = json.load(open(sw_file)) if os.path.exists(sw_file) else {}
for gi, g in enumerate(gear):
    nif = os.path.join(base, g.replace("/", "\\"))
    if not os.path.exists(nif):
        print("missing mesh", g); continue
    name = "gear_%s_%d.json" % (fid, gi)
    r = run(os.path.join(T, "npc_skin.py"), "mesh", nif, os.path.join(NPC, "skin", name), skel_json, "--creature")
    print(r.stdout.strip()[-400:], r.stderr.strip()[-200:])
    try:
        parts = json.load(open(os.path.join(NPC, "skin", name)))
    except Exception:
        continue
    if not parts:
        continue
    pairs = [p.split("=", 1) for p in swaps.get(g, "").split(";") if "=" in p]
    for s in parts:
        for shape, tex in pairs:
            if s["name"].strip().lower() == shape.strip().lower():
                t = tex.replace("/", "\\")
                s["texture"] = t if t.lower().startswith("textures\\") else "textures\\" + t
    json.dump(parts, open(os.path.join(NPC, "skin", name), "w"))
    gear_jsons.append(name)
if not gear_jsons:
    sys.exit("no skinned geometry could be read for %s" % fid)

# 2b. The mesh is bound to the bones' BIND pose (NiSkinData), which for creatures differs from skeleton.nif's rest pose. The game skins with
# X_bone * S^-1, so the rest pose that the Unreal side and the FBX armature must use is the bind pose: overwrite those bones in the skeleton json.
sk_list = json.load(open(skel_json))
orig_json = skel_json + ".nif_rest"
if not os.path.exists(orig_json):
    json.dump(sk_list, open(orig_json, "w"))                       # keep the raw skeleton.nif rest pose
binds = {}
for n in gear_jsons:
    for s in json.load(open(os.path.join(NPC, "skin", n))):
        for bname, (rot9, pos3) in s.get("bind", {}).items():
            binds[bname] = (rot9, pos3)
patched = 0
for b in sk_list:
    if b["name"] in binds:
        b["rot"], b["pos"] = binds[b["name"]]; patched += 1
json.dump(sk_list, open(skel_json, "w"))
print("rest pose = bind pose for %d of %d bones" % (patched, len(sk_list)))

# 3. textures
shapes = [s for n in gear_jsons for s in json.load(open(os.path.join(NPC, "skin", n)))]
texs = sorted({(s["texture"].lower() if s["texture"].lower().startswith("textures") else "textures\\" + s["texture"].lower()) for s in shapes if s["texture"]})
os.makedirs(os.path.join(NPC, "obj"), exist_ok=True)
with open(os.path.join(NPC, "obj", "npc_%s.mtl" % fid), "w") as m:
    for t in texs:
        m.write("newmtl %s\n# skyrim diffuse: %s\n" % (t.replace("\\", "_").replace(".", "_"), t))
print(run(os.path.join(T, "textures.py"), DATA, NPC).stdout[-300:])
run(os.path.join(T, "textures_pbr.py"), DATA, NPC)

# 4. Blender
fbx = os.path.join(NPC, "export", "npc_%s.fbx" % fid)
p = subprocess.run([r"D:\blender.exe", "-b", "-P", os.path.join(T, "npc_blender.py"), "--", os.path.join(NPC, "skin"), key, fbx] + gear_jsons + ["--creature"],
                   capture_output=True, text=True)
print([l for l in p.stdout.splitlines() if "EXPORTED" in l or "Error" in l or "Traceback" in l])
