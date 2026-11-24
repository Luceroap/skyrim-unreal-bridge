"""Merge runtime truth (cumulative dump) with Skyrim.esm WhiterunWorld refs into one area json.
Where the player has been (circles of COVER units around the dump centers) only the live data is used (it reflects mods,
disabled objects and exact transforms); elsewhere the ESM refs fill in.
Usage: python -I merge_area.py <out.json> <refs_all.tsv> <centers.txt> <area_esm.json> [cover=6000]"""
import sys, json, math

out, tsv, centers_f, esm_f = sys.argv[1:5]
COVER = float(sys.argv[5]) if len(sys.argv) > 5 else 6000.0
INCLUDE = ("architecture/", "landscape/plants/", "plants/", "landscape/rocks/", "landscape/trees/", "furniture/", "clutter/", "dungeons/misc/", "clutter/barrel", "clutter/crate", "clutter/hay", "clutter/signage/",
           "clutter/tombstones/", "clutter/common/commonchair", "clutter/common/commontable", "clutter/cart", "clutter/wagon",
           "furniture/blacksmith", "furniture/bench", "clutter/whiterun", "clutter/market")
EXCLUDE = ("lod", "marker", "/effects/", "fx", "collision", "destroyed")

centers = [tuple(map(float, l.split())) for l in open(centers_f).read().splitlines() if l.strip()]
truth, seen = [], set()
for line in open(tsv, encoding="latin1").read().splitlines()[1:]:
    f = line.split("\t")
    if len(f) < 13 or f[11] == "1" or f[0] in seen:
        continue
    seen.add(f[0])
    m = f[3].lower().replace("\\", "/")
    if m.startswith("meshes/"): m = m[7:]
    if not m.endswith(".nif") or not m.startswith(INCLUDE) or any(x in m for x in EXCLUDE):
        continue
    x, y, z, rx, ry, rz, sc = map(float, f[4:11])
    truth.append({"nif": m, "pos": [x, y, z], "rot": [rx, ry, rz], "scale": sc or 1.0})

esm = []
# Union: the live dump misses some objects the game clearly shows (e.g. most Whiterun houses), so game-file refs are always
# added unless the live data already has the same model at (almost) the same spot. 'destroyed'/'lod' variants are alternative
# states of the same object and would overlap the normal one, so they are skipped.
live_idx = {}
for t in truth:
    live_idx.setdefault(t["nif"], []).append(t["pos"])
for r in json.load(open(esm_f)):
    if any(x in r["nif"] for x in EXCLUDE) or not r["nif"].endswith(".nif"):
        continue
    if any(math.dist(p, r["pos"]) < 40 for p in live_idx.get(r["nif"], [])):
        continue
    esm.append(r)
json.dump(truth + esm, open(out, "w"))
print("merged: %d live refs + %d game-file refs (outside %d covered spots) = %d" % (len(truth), len(esm), len(centers), len(truth) + len(esm)))
print("unique models:", len({r["nif"] for r in truth + esm}))

