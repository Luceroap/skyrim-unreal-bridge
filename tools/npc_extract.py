"""Copy the character skeleton + base body NIFs (loose overrides first, then mod BSAs, then vanilla) into area2/npc/nif.
Usage: python -I npc_extract.py <data_dir> <area_dir> [extra nif paths relative to Data, e.g. meshes\\armor\\iron\\f\\cuirass_0.nif]"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bsa import Bsa

DATA, AREA = sys.argv[1], sys.argv[2]
CA = "meshes\\actors\\character\\character assets"
BASE = [CA + "\\skeleton.nif", CA + " female\\skeleton_female.nif"]
for sex in ("male", "female"):
    for part in ("body", "hands", "feet"):               # both sexes' body parts live in "character assets"
        BASE.append("%s\\%s%s_1.nif" % (CA, sex, part))
WANT = BASE + [p.replace("/", "\\") for p in sys.argv[3:]]

archives = []
for p in sorted(glob.glob(os.path.join(DATA, "*.bsa"))):
    try:
        archives.append((os.path.basename(p).lower().startswith("skyrim - "), Bsa(p)))
    except Exception:
        pass
archives.sort(key=lambda t: t[0])           # mod archives before vanilla

out = os.path.join(AREA, "npc", "nif")

# `face:<hex form id>` args: per-NPC baked head (face, hair, eyes, brows, beard) + face tint; plugin folder is whatever has the file
for arg in [a for a in WANT if a.lower().startswith("face:")]:
    WANT.remove(arg)
    fid = arg.split(":", 1)[1].lower().zfill(8)
    hits = []
    for pat in ("meshes\\actors\\character\\facegendata\\facegeom\\*\\%s.nif" % fid,
                "textures\\actors\\character\\facegendata\\facetint\\*\\%s.dds" % fid):
        loose = glob.glob(os.path.join(DATA, pat))
        if loose:
            hits.append(os.path.relpath(loose[0], DATA)); continue
        suffix = pat.split("*", 1)[1]
        pre = pat.split("*", 1)[0]
        for _van, a in archives:
            m = [f for f in a.files if f.startswith(pre.lower()) and f.endswith(suffix.lower())]
            if m:
                hits.append(m[0]); break
    WANT += hits

for rel in WANT:
    raw = None
    loose = os.path.join(DATA, rel)
    if os.path.exists(loose):
        raw = open(loose, "rb").read(); src = "loose"
    else:
        for _van, a in archives:
            if rel.lower() in a.files:
                raw = a.read(rel); src = os.path.basename(a.f.name); break
    if raw is None:
        print("MISSING", rel); continue
    dst = os.path.join(out, rel.lower().replace("meshes\\", "", 1))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "wb").write(raw)
    print("%-70s %7d bytes  from %s" % (rel, len(raw), src))
