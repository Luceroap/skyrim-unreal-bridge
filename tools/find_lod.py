"""Where are Skyrim's terrain LOD meshes (.btr) and textures? Usage: python tools/find_lod.py"""
import collections, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bsa import Bsa

DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
for p in sorted(glob.glob(os.path.join(DATA, "*.bsa"))):
    try:
        b = Bsa(p)
    except Exception:
        continue
    c = collections.Counter()
    for f in b.files:
        if f.startswith("meshes\\terrain\\tamriel\\") and f.endswith(".btr"):
            c["btr level " + f.split(".")[1]] += 1
        elif f.startswith("textures\\terrain\\tamriel\\"):
            c["terrain tex"] += 1
        elif f.startswith("meshes\\terrain\\tamriel\\objects\\"):
            c["bto"] += 1
    if c:
        print(os.path.basename(p), dict(c))
loose = os.path.join(DATA, "meshes", "terrain", "tamriel")
print("loose btr:", [f for f in os.listdir(loose) if f.endswith(".btr")][:5] if os.path.isdir(loose) else None)
print("loose objects sample:", sorted(os.listdir(os.path.join(loose, "objects")))[:5] if os.path.isdir(os.path.join(loose, "objects")) else None)
