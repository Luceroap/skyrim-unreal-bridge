"""Which texture keys use Skyrim's special snow/mountain shading, from the models in area2/nif/*.nif:
  area2/tex/projected_snow.txt      shapes with the Projected-UV shader flag (SLSF1 bit 23)
  area2/tex/multilayer_textures.txt shapes with shader type 11 (Multi-Layer Parallax): in the converted set this is exactly the mountain/cliff meshes
Keys are the diffuse file stem, lower-case (same key as the converted PNG). Usage: python -I projected_snow.py"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nif2obj import R, parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTED, MULTILAYER = 1 << 23, 11
proj, multi, models, scanned = {}, {}, {}, 0
for path in sorted(glob.glob(os.path.join(ROOT, "area2", "nif", "*.nif"))):
    try:
        data, blocks, strings, bsver = parse(open(path, "rb").read())
    except Exception:
        continue
    scanned += 1
    for typ, pos, size in blocks:
        if typ != "BSLightingShaderProperty":
            continue
        try:
            r = R(data, pos)
            stype = r.u32()                               # skyrim shader type
            r.i32(); k = r.u32(); [r.i32() for _ in range(k)]; r.i32()    # NiObjectNET: name, extra data, controller
            flags1 = r.u32(); r.u32(); r.f(4)
            if not (flags1 & PROJECTED or stype == MULTILAYER):
                continue
            ts = r.i32()
            if ts < 0:
                continue
            rr = R(data, blocks[ts][1])
            if not rr.u32():
                continue
            key = os.path.splitext(os.path.basename(rr.lstr().lower().replace("\\", "/")))[0]
            if flags1 & PROJECTED:
                proj[key] = proj.get(key, 0) + 1
            if stype == MULTILAYER:
                multi[key] = multi.get(key, 0) + 1
            models.setdefault(key, set()).add(os.path.basename(path))
        except Exception:
            continue
for name, d in (("projected_snow.txt", proj), ("multilayer_textures.txt", multi)):
    with open(os.path.join(ROOT, "area2", "tex", name), "w") as f:
        for k in sorted(d):
            f.write(k + "\n")
    print("%s: %d texture keys" % (name, len(d)))
print("scanned %d nifs" % scanned)
for k in sorted(multi):
    print("  multilayer: %-26s e.g. %s" % (k, sorted(models[k])[0]))
