"""Extract + convert the companion maps (normal '_n', PBR 'rmaos') for every diffuse texture referenced by <area>/obj/*.mtl.
Usage: python -I textures_pbr.py <Data dir> <area dir>
Writes <area>/tex/<name>_n.png and <name>_rmaos.png. Normal maps: BC5 (2-channel) is expanded to RGB."""
import sys, os, re, glob, io, struct, math
def norm(p):
    p = p.strip().lower()
    i = p.find("textures\\")          # some meshes carry a dev-build prefix (skyrimhd\build\pc\data\textures\...) that the game strips
    return p[i:] if i > 0 else p

sys.path.insert(0, os.path.dirname(__file__))
from bsa import Bsa
from PIL import Image

data_dir, area = sys.argv[1:3]
texdir = os.path.join(area, "tex")
archives = []
_mods, _van = [], []
for _p in sorted(glob.glob(os.path.join(data_dir, "*.bsa"))):
    _b = os.path.basename(_p).lower()
    if _b.startswith("skyrim - ") and not _b.startswith("skyrim - textures"): continue
    try: (_van if _b.startswith("skyrim - ") else _mods).append(Bsa(_p))
    except Exception: pass
archives = _mods + _van
bases = set()
for m in glob.glob(os.path.join(area, "obj", "*.mtl")):
    for line in open(m):
        mm = re.match(r"# skyrim diffuse: (.+)", line.strip())
        if mm:
            bases.add(norm(mm.group(1))[:-4])


def read(path):
    loose = os.path.join(data_dir, path)
    if os.path.exists(loose):
        return open(loose, "rb").read()
    for a in archives:
        if path in a.files:
            return a.read(path)
    return None


def decode(raw):
    if raw[84:88] == b"DX10":
        f = struct.unpack_from("<I", raw, 128)[0]
        if f in (72, 75, 78, 99):
            raw = raw[:128] + struct.pack("<I", f - 1) + raw[132:]
    im = Image.open(io.BytesIO(raw)); im.load()
    return im


n_ok = 0
for base in sorted(bases):
    name = os.path.basename(base)
    for suffix in ("_n", "_rmaos"):
        png = os.path.join(texdir, name + suffix + ".png")
        spec = os.path.join(texdir, name + "_s.png")
        need_spec = suffix == "_n" and not os.path.exists(spec) and not os.path.exists(spec + ".none")
        if os.path.exists(png) and not need_spec:
            continue
        raw = read(base + suffix + ".dds")
        if raw is None:
            continue
        try:
            im = decode(raw)
            if need_spec:                        # Skyrim keeps the specular (shine) mask in the normal map's alpha
                a = im.convert("RGBA").split()[3]
                lo, hi = a.getextrema()
                if hi - lo > 8:
                    a.save(spec)
                else:
                    open(spec + ".none", "w").close()
                if os.path.exists(png):
                    continue
            if suffix == "_n":
                im = im.convert("RGB")
                r, g, b = im.split()
                if b.getextrema()[1] == 0:       # BC5: reconstruct Z from X,Y
                    rd, gd = list(r.getdata()), list(g.getdata())
                    bd = [int(255 * math.sqrt(max(0.0, 1 - ((x / 127.5 - 1) ** 2) - ((y / 127.5 - 1) ** 2))) * 0.5 + 127.5 * 0) for x, y in zip(rd, gd)]
                    b = Image.new("L", im.size); b.putdata([min(255, v * 1) for v in [int((math.sqrt(max(0.0, 1 - ((x / 127.5 - 1) ** 2) - ((y / 127.5 - 1) ** 2))) * 0.5 + 0.5) * 255) for x, y in zip(rd, gd)]])
                    im = Image.merge("RGB", (r, g, b))
            else:
                im = im.convert("RGBA")
            im.save(png); n_ok += 1
        except Exception as e:
            print("FAILED", base + suffix, e)
print("companion maps written:", n_ok, "for", len(bases), "textures")


