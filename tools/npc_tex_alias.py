"""NPC textures whose file name is shared by different paths (e.g. anukethreplacers\\Hair\\Jenassa.dds, ...\\Eyes\\Jenassa.dds,
...\\Brows\\Jenassa.dds) collapse onto one area2/tex/<stem>.png in textures.py. This converts every such texture to a unique
PNG named <parent folder>_<stem>.png (plus _n / _s companions) and writes area2/npc/tex_alias.json: {material slot name: unique stem},
which npc_live._material_for_slot consults first.
  python npc_tex_alias.py"""
import glob, io, json, os, re, struct, sys

sys.path.insert(0, os.path.dirname(__file__))
from bsa import Bsa
from PIL import Image

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
AREA = os.path.join(ROOT, "area2")
OUT = os.path.join(AREA, "tex")


def norm(p):
    p = p.strip().lower()
    i = p.find("textures\\")
    return p[i:] if i > 0 else p


slots = {}                                   # slot name -> texture path
for m in glob.glob(os.path.join(AREA, "npc", "obj", "*.mtl")):
    name = None
    for line in open(m):
        line = line.strip()
        if line.startswith("newmtl "):
            name = line[7:]
        mm = re.match(r"# skyrim diffuse: (.+)", line)
        if mm and name:
            slots[name] = norm(mm.group(1))

by_stem = {}
for t in set(slots.values()):
    by_stem.setdefault(os.path.basename(t).rsplit(".", 1)[0], set()).add(t)
clash = {t for paths in by_stem.values() if len(paths) > 1 for t in paths}
print(len(slots), "slots,", len(clash), "textures with a shared file name")

_archives = None


def read(tex):
    global _archives
    loose = os.path.join(DATA, tex)
    if os.path.exists(loose):
        return open(loose, "rb").read()
    if _archives is None:
        mods, van = [], []
        for p in sorted(glob.glob(os.path.join(DATA, "*.bsa"))):
            b = os.path.basename(p).lower()
            if b.startswith("skyrim - ") and not b.startswith("skyrim - textures"):
                continue
            try:
                (van if b.startswith("skyrim - ") else mods).append(Bsa(p))
            except Exception:
                pass
        _archives = mods + van
    for a in _archives:
        if tex in a.files:
            return a.read(tex)
    return None


def convert(tex, png):
    if os.path.exists(png):
        return True
    raw = read(tex)
    if raw is None:
        return False
    if raw[84:88] == b"DX10":
        fmt = struct.unpack_from("<I", raw, 128)[0]
        if fmt in (72, 75, 78, 99):
            raw = raw[:128] + struct.pack("<I", fmt - 1) + raw[132:]
    try:
        im = Image.open(io.BytesIO(raw)); im.load()
        im.convert("RGBA").save(png)
        return True
    except Exception as e:
        print("FAILED", tex, e)
        return False


def unique_stem(tex):
    parts = tex.replace("/", "\\").split("\\")
    return re.sub(r"[^a-z0-9]+", "_", (parts[-2] + "_" + parts[-1].rsplit(".", 1)[0]).lower())


alias = {}
for slot, tex in sorted(slots.items()):
    if tex not in clash:
        continue
    stem = unique_stem(tex)
    if not convert(tex, os.path.join(OUT, stem + ".png")):
        print("MISSING", tex)
        continue
    base = tex.rsplit(".", 1)[0]
    convert(base + "_n.dds", os.path.join(OUT, stem + "_n.png"))
    alias[slot.lower()] = stem
json.dump(alias, open(os.path.join(AREA, "npc", "tex_alias.json"), "w"), indent=1, sort_keys=True)
print(len(alias), "slots aliased:", sorted(set(alias.values()))[:40])
