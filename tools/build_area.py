"""Extract + convert every model in whiterun/area.json to OBJ, and write placements CSV.
Usage: python -I build_area.py <Data dir> <area.json> <out_dir>"""
import sys, os, json, traceback, glob
sys.path.insert(0, os.path.dirname(__file__))
from bsa import Bsa
import nif2obj

data_dir, area, out = sys.argv[1:4]
d = json.load(open(area))
os.makedirs(os.path.join(out, "obj"), exist_ok=True)
os.makedirs(os.path.join(out, "nif"), exist_ok=True)
def open_archives(prefix_filter):
    """All v105 BSAs in Data that contain files we may need; mod archives first so they override vanilla."""
    mods, vanilla = [], []
    for p in sorted(glob.glob(os.path.join(data_dir, "*.bsa"))):
        base = os.path.basename(p)
        if base.lower().startswith(("skyrim - textures", "skyrim - sounds", "skyrim - voices", "skyrim - animations", "skyrim - interface", "skyrim - misc", "skyrim - shaders", "skyrim - patch", "skyrim - meshes")) and "meshes" not in prefix_filter:
            continue
        try:
            b = Bsa(p)
        except Exception:
            continue
        (vanilla if base.lower().startswith("skyrim - ") else mods).append(b)
    return mods + vanilla


archives = open_archives("meshes")


def asset(n):
    return n[:-4].replace("/", "_")


done, failed = {}, []
for nif in sorted({r["nif"] for r in d}):
    key = "meshes\\" + nif.replace("/", "\\")
    raw = None
    loose = os.path.join(data_dir, key)
    if os.path.exists(loose):
        raw = open(loose, "rb").read()      # your loose override (mods) wins
    else:
        for a in archives:
            if key in a.files:
                raw = a.read(key); break
    if raw is None:
        failed.append((nif, "not found")); continue
    name = asset(nif)
    nifp = os.path.join(out, "nif", name + ".nif")
    marker = os.path.join(out, "obj", name + ".v2")      # set once a model has been (re)converted with the NiTriShape-aware parser
    stale = os.path.exists(nifp) and b"NiTriShapeData" in open(nifp, "rb").read() and not os.path.exists(marker)
    if stale:   # drop the old export + Unreal asset so they are rebuilt from the corrected OBJ
        for old in (os.path.join(out, "export", name + ".fbx"), os.path.join(os.path.dirname(os.path.dirname(out)), "unreal", "SkyBridge", "Content", "Area2", name + ".uasset")):
            if os.path.exists(old): os.remove(old)
    if os.path.exists(os.path.join(out, "obj", name + ".obj")) and not stale:     # already converted (incremental)
        done[nif] = name; continue
    p = os.path.join(out, "nif", name + ".nif")
    open(p, "wb").write(raw)
    try:
        shapes = nif2obj.extract(p)
        if not shapes:
            failed.append((nif, "no geometry")); continue
        nif2obj.write_obj(shapes, os.path.join(out, "obj", name + ".obj"))
        open(marker, "w").write("1")
        done[nif] = name
    except Exception as e:
        failed.append((nif, repr(e)[:80]))

rows = []
import math
for r in d:
    if r["nif"] in done:
        rows.append("%s,%s,%s" % (done[r["nif"]], ",".join("%.3f" % x for x in r["pos"] + r["rot"]), r["scale"]))
open(os.path.join(out, "placements.csv"), "w").write("\n".join(rows) + "\n")
print(len(done), "models converted,", len(rows), "placements,", len(failed), "failed")
for f in failed: print("FAIL", f)






