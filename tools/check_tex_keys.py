"""Report mesh materials whose texture key is ambiguous (suffix match picked by ue_assets.import_model) and diffuse
textures that share a file name across folders (area2/tex is flat by base name).
Usage: python tools/check_tex_keys.py"""
import collections, glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREA = os.path.join(ROOT, "area2")
keys = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(AREA, "tex", "*.png"))]
keys = [k for k in keys if not k.endswith(("_n", "_rmaos", "_s"))]
by_base = collections.defaultdict(set)
ambiguous = {}
for mtl in glob.glob(os.path.join(AREA, "obj", "*.mtl")):
    mat = None
    for line in open(mtl, errors="replace"):
        if line.startswith("newmtl "):
            mat = line.split(None, 1)[1].strip().lower()
        m = re.match(r"# skyrim diffuse: (.+)", line.strip())
        if m and mat:
            path = m.group(1).strip().lower().replace("/", "\\")
            i = path.find("textures\\")
            path = path[i:] if i > 0 else path
            base = os.path.splitext(os.path.basename(path))[0]
            by_base[base].add(path)
            cands = [k for k in keys if mat.endswith("_" + k.lower() + "_dds")]
            if len(cands) > 1 or (cands and cands[0].lower() != base):
                ambiguous[mat] = (base, cands)
print("materials with ambiguous/wrong key:", len(ambiguous))
for mat, (base, c) in sorted(ambiguous.items())[:40]:
    print("  %s  real=%s  candidates=%s" % (mat[-70:], base, c))
dup = {b: p for b, p in by_base.items() if len(p) > 1}
print("diffuse base names used by several folders:", len(dup))
for b, p in sorted(dup.items())[:30]:
    print("  %s: %s" % (b, sorted(p)))
