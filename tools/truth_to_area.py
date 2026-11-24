"""Turn the runtime dump (SkyrimUnrealBridge_refs.tsv) into an area json for build_area.py.
Usage: python -I truth_to_area.py <refs.tsv> <out.json>"""
import sys, json, collections

out = sys.argv[1]
tsvs = sys.argv[2:]          # several dumps (taken at different spots) are merged; refs are de-duplicated by reference id
seen_ids = set()
INCLUDE = ("architecture/", "landscape/rocks/", "clutter/barrel", "clutter/crate", "clutter/hay", "clutter/signage/",
           "clutter/tombstones/", "clutter/common/commonchair", "clutter/common/commontable", "clutter/cart", "clutter/wagon",
           "furniture/blacksmith", "furniture/bench", "clutter/whiterun", "clutter/market")
EXCLUDE = ("lod", "marker", "/effects/", "fx", "collision")
res, cnt = [], collections.Counter()
lines = [l for t in tsvs for l in open(t, encoding="latin1").read().splitlines()[1:]]
for line in lines:
    f = line.split("\t")
    if len(f) < 13 or f[11] == "1" or f[0] in seen_ids:
        continue
    seen_ids.add(f[0])
    m = f[3].lower().replace("\\", "/")
    if m.startswith("meshes/"): m = m[7:]
    if not m.endswith(".nif") or not m.startswith(INCLUDE) or any(x in m for x in EXCLUDE):
        continue
    x, y, z, rx, ry, rz, sc = map(float, f[4:11])
    res.append({"nif": m, "pos": [x, y, z], "rot": [rx, ry, rz], "scale": sc or 1.0})
    cnt[m] += 1
json.dump(res, open(out, "w"))
print(len(res), "refs,", len(cnt), "unique models")
top = collections.Counter(m.split("/")[0] + "/" + m.split("/")[1] for m in cnt)
for k, v in top.most_common(8): print("  ", v, k)
