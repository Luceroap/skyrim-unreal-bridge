"""Build one named NPC (body + baked FaceGen head/hair/eyes/brows/beard) as a skinned FBX for Unreal.
  python -I npc_build.py <base npc form id hex> <male|female>
Output: area2/npc/export/npc_<id>.fbx (armature + one mesh), textures in area2/tex (shared with the static pipeline).
Face tint: area2/npc/tex/<id>.png (the baked skin colour map for the head)."""
import json, os, subprocess, sys

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
PY = sys.executable
T = os.path.join(ROOT, "tools")
AREA = os.path.join(ROOT, "area2")
NPC = os.path.join(AREA, "npc")

fid, sex = sys.argv[1].lower().zfill(8), sys.argv[2]
gear = [a for a in sys.argv[3:] if not a.startswith("--")]          # armor-addon model paths from the gear stream (relative to meshes/)
slots = int(next((a[8:] for a in sys.argv[3:] if a.startswith("--slots=")), "0") or "0", 16)          # worn biped slots (bit0 Head, bit1 Hair, bit11 LongHair)
face_id = next((a[7:].lower().zfill(8) for a in sys.argv[3:] if a.startswith("--face=")), fid)    # NPC whose baked head this actor uses (guards: template NPC)


def run(*a):
    return subprocess.run([PY, "-W", "ignore", "-I", *a], capture_output=True, text=True)


# 1. body parts + skeleton + this NPC's face files
r = run(os.path.join(T, "npc_extract.py"), DATA, AREA, "face:" + face_id)
face_nif = None
for line in r.stdout.splitlines():
    if line.lower().strip().startswith("meshes") and face_id in line.lower():
        face_nif = line.split("  ")[0].strip().replace("meshes\\", "", 1)
if not face_nif:
    sys.exit("no FaceGen head for %s (%s)" % (fid, r.stdout[-300:]))
base = os.path.join(NPC, "nif")
skel_json = os.path.join(NPC, "skin", "skeleton_%s.json" % sex)
face_json = "face_%s.json" % fid
out = run(os.path.join(T, "npc_skin.py"), "mesh", os.path.join(base, face_nif), os.path.join(NPC, "skin", face_json), skel_json)
print(out.stdout.strip())

# helmets / hoods / circlets-with-hair-slot hide the baked hair in game: drop the hair shapes (head, brows, eyes, beard, scalp stay)
if slots & (0x1 | 0x2 | 0x800):
    fj = os.path.join(NPC, "skin", face_json)
    all_shapes = json.load(open(fj))
    kept = [s for s in all_shapes if "hair" not in s["name"].lower()]
    if len(kept) != len(all_shapes):
        json.dump(kept, open(fj, "w"))
        print("helmet worn: hid %d hair shape(s)" % (len(all_shapes) - len(kept)))

# 1b. worn armor/clothing: extract + convert each addon nif; decide which base body parts it replaces
gear_jsons, omit = [], set()
if gear:
    run(os.path.join(T, "npc_extract.py"), DATA, AREA, *["meshes\\" + g.replace("/", "\\") for g in gear])
    for gi, g in enumerate(gear):
        src = os.path.join(base, g.replace("/", "\\"))
        if not os.path.exists(src):
            continue
        name = "gear_%s_%d.json" % (fid, gi)
        run(os.path.join(T, "npc_skin.py"), "mesh", src, os.path.join(NPC, "skin", name), skel_json)
        try:
            parts = json.load(open(os.path.join(NPC, "skin", name)))
        except Exception:
            continue
        if not parts:
            continue
        sw_file = os.path.join(NPC, "swaps_%s.json" % fid)               # texture overrides from the armor addon (e.g. Whiterun vs Riften guard colours)
        if os.path.exists(sw_file):
            sw = json.load(open(sw_file)).get(g, "")
            pairs = [p.split("=", 1) for p in sw.split(";") if "=" in p]
            changed = False
            for s in parts:
                for shape, tex in pairs:
                    if s["name"].strip().lower() == shape.strip().lower():
                        t = tex.replace("/", "\\")
                        s["texture"] = t if t.lower().startswith("textures\\") else "textures\\" + t      # texture sets store paths relative to Data\textures
                        changed = True
            if changed:
                json.dump(parts, open(os.path.join(NPC, "skin", name), "w"))
        gear_jsons.append(name)
        for s in parts:                                              # which base body parts does this piece cover? (T-pose bbox heuristics)
            vs = s["verts"]
            if not vs: continue
            zmin, zmax = min(v[2] for v in vs), max(v[2] for v in vs)
            xspan = max(v[0] for v in vs) - min(v[0] for v in vs)
            if zmin < 80 and zmax > 95 and xspan > 25: omit.add("body")         # torso piece (cuirass, robes)
            if zmax < 22: omit.add("feet")                                     # boots
            if 55 < zmin and zmax < 100 and xspan > 55: omit.add("hands")      # gauntlets / bracers spread by the T-pose
shapes_extra = [json.load(open(os.path.join(NPC, "skin", n))) for n in gear_jsons]

# 2. textures: every texture referenced by the face shapes + the head tint
shapes = json.load(open(os.path.join(NPC, "skin", face_json)))
for lst in shapes_extra:
    shapes += lst
texs = sorted({s["texture"].lower() if s["texture"].lower().startswith("textures") else "textures\\" + s["texture"].lower()
               for s in shapes if s["texture"]})
texs.append("textures\\actors\\character\\facegendata\\facetint\\skyrim.esm\\%s.dds" % face_id)   # skyrim.esm folder; other plugins keep their own
mtl_dir = os.path.join(NPC, "obj"); os.makedirs(mtl_dir, exist_ok=True)
with open(os.path.join(mtl_dir, "npc_%s.mtl" % fid), "w") as m:
    for t in texs:
        m.write("newmtl %s\n# skyrim diffuse: %s\n" % (t.replace("\\", "_").replace(".", "_"), t))
print(run(os.path.join(T, "textures.py"), DATA, NPC).stdout[-400:])
run(os.path.join(T, "textures_pbr.py"), DATA, NPC)

# 3. Blender: armature + body + head parts -> FBX
fbx = os.path.join(NPC, "export", "npc_%s.fbx" % fid)
p = subprocess.run([r"D:\blender.exe", "-b", "-P", os.path.join(T, "npc_blender.py"), "--", os.path.join(NPC, "skin"), sex, fbx, face_json] + gear_jsons +
                   ["--omit=" + ",".join(sorted(omit))], capture_output=True, text=True)
print([l for l in p.stdout.splitlines() if "EXPORTED" in l or "Error" in l])
