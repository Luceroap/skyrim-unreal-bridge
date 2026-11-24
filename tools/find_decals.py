"""List diffuse textures that Skyrim draws as decals (BSLightingShaderProperty flags1 bit 26 Decal / 27 Dynamic Decal).
Decal shapes lie on top of walls/floors; Skyrim offsets them with depth bias, Unreal needs a small camera-ward offset or
they z-fight (flicker). Writes area2/tex/decal_textures.txt (base names, lower case).
Usage: python tools/find_decals.py"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nif2obj import R, parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
DECAL = (1 << 26) | (1 << 27)
found = {}
for path in glob.glob(os.path.join(AREA, "nif", "*.nif")):
    try:
        data, blocks, strings, bsver = parse(open(path, "rb").read())
    except Exception:
        continue
    for typ, pos, size in blocks:
        if typ != "BSLightingShaderProperty":
            continue
        try:
            r = R(data, pos)
            r.u32()
            r.i32(); k = r.u32(); [r.i32() for _ in range(k)]; r.i32()
            f1 = r.u32(); r.u32(); r.f(4)
            ts = r.i32()
            if not (f1 & DECAL) or ts < 0:
                continue
            rr = R(data, blocks[ts][1])
            if rr.u32():
                tex = rr.lstr().lower().replace("/", "\\")
                found.setdefault(os.path.splitext(os.path.basename(tex))[0], set()).add(os.path.basename(path))
        except Exception:
            continue
with open(os.path.join(AREA, "tex", "decal_textures.txt"), "w") as f:
    f.write("\n".join(sorted(found)) + "\n")
print(len(found), "decal textures")
for k, v in sorted(found.items()):
    print("  %s (%d models)" % (k, len(v)))
