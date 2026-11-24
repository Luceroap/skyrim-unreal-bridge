"""Index of every mesh in the game (BSAs + loose files): asset name -> nif path, so a model name can be turned back into its file even when
area2/models.json (rewritten by every editor session) no longer has it.   python tools/mesh_index.py   -> area2/mesh_index.json
Asset name rule (same as live_bridge.asset_name): lower-case path under meshes/, '/' -> '_', '.nif' dropped."""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bsa import Bsa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
OUT = os.path.join(ROOT, "area2", "mesh_index.json")


def key(rel):                       # rel: 'clutter/banners/x.nif'
    return rel[:-4].replace("/", "_").lower()


def build():
    idx = {}
    for p in sorted(glob.glob(os.path.join(DATA, "*.bsa"))):             # vanilla first, mod archives later (they override the same path anyway)
        try:
            a = Bsa(p)
        except Exception:
            continue
        for f in a.files:
            if f.startswith("meshes\\") and f.endswith(".nif"):
                rel = f[7:].replace("\\", "/")
                idx.setdefault(key(rel), rel)
    for f in glob.glob(os.path.join(DATA, "meshes", "**", "*.nif"), recursive=True):    # loose files win
        rel = os.path.relpath(f, os.path.join(DATA, "meshes")).replace("\\", "/").lower()
        idx[key(rel)] = rel
    json.dump(idx, open(OUT, "w"))
    return idx


def load():
    if os.path.exists(OUT):
        return json.load(open(OUT))
    return build()


if __name__ == "__main__":
    i = build()
    print("indexed %d meshes -> %s" % (len(i), OUT))
