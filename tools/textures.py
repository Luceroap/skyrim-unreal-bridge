"""Extract the diffuse textures referenced by whiterun/obj/*.mtl from Skyrim's Textures BSAs, convert DDS -> PNG,
and add 'map_Kd' lines to the MTLs so Blender picks them up.
Usage: python -I textures.py <data_dir> <whiterun_dir>"""
import sys, os, re, glob, io, struct
def norm(p):
    p = p.strip().lower()
    i = p.find("textures\\")          # some meshes carry a dev-build prefix (skyrimhd\build\pc\data\textures\...) that the game strips
    return p[i:] if i > 0 else p

sys.path.insert(0, os.path.dirname(__file__))
from bsa import Bsa
from PIL import Image

data_dir, wr = sys.argv[1:3]
mtls = glob.glob(os.path.join(wr, "obj", "*.mtl"))
wanted = {}
for m in mtls:
    for line in open(m):
        mm = re.match(r"# skyrim diffuse: (.+)", line.strip())
        if mm:
            wanted[norm(mm.group(1))] = None
print(len(wanted), "textures wanted")

archives = []
_mods, _van = [], []
for _p in sorted(glob.glob(os.path.join(data_dir, "*.bsa"))):
    _b = os.path.basename(_p).lower()
    if _b.startswith("skyrim - ") and not _b.startswith("skyrim - textures"): continue
    try: (_van if _b.startswith("skyrim - ") else _mods).append(Bsa(_p))
    except Exception: pass
archives = _mods + _van      # mod archives first so they override vanilla
outdir = os.path.join(wr, "tex")
os.makedirs(outdir, exist_ok=True)
for tex in sorted(wanted):
    png = os.path.join(outdir, os.path.basename(tex).rsplit(".", 1)[0] + ".png")
    if os.path.exists(png):
        wanted[tex] = png; continue                                 # already converted (incremental)
    loose = os.path.join(data_dir, tex)  # prefer nothing loose: vanilla look, see README
    raw = None
    if os.path.exists(loose):
        raw = open(loose, "rb").read()          # loose file from your mod list wins
    else:
        for a in archives:
            if tex in a.files:
                raw = a.read(tex); break
    if raw is None:
        print("MISSING", tex); continue
    try:
        if raw[84:88] == b"DX10":  # Pillow lacks the *_SRGB DXGI formats: treat as the UNORM equivalent
            fmt = struct.unpack_from("<I", raw, 128)[0]
            if fmt in (72, 75, 78, 99):
                raw = raw[:128] + struct.pack("<I", fmt - 1) + raw[132:]
        im = Image.open(io.BytesIO(raw)); im.load()
        im = im.convert("RGBA")
        im.save(png)
        wanted[tex] = png
        print("ok", tex, im.size)
    except Exception as e:
        print("FAILED", tex, e)

for m in mtls:
    out = []
    for line in open(m):
        out.append(line.rstrip("\n"))
        mm = re.match(r"# skyrim diffuse: (.+)", line.strip())
        if mm and wanted.get(norm(mm.group(1))):
            out.append("map_Kd " + wanted[norm(mm.group(1))].replace("\\", "/"))
    open(m, "w").write("\n".join(out) + "\n")



