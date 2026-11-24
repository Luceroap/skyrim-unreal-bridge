"""Compare runtime-truth references (SkyrimUnrealBridge_refs.tsv from the plugin) with area/placements.csv.
Usage: python -I compare_refs.py <refs.tsv> <placements.csv> [player_x player_y radius]"""
import sys, math, collections

tsv, csv = sys.argv[1], sys.argv[2]
px, py, rad = (float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (20848, -7352, 11000)


def asset(model):
    m = model.lower().replace("\\", "/")
    if m.startswith("meshes/"): m = m[7:]
    return m.replace("architecture/whiterun/", "").replace(".nif", "").replace("/", "_"), m


truth = []
for line in open(tsv, encoding="latin1").read().splitlines()[1:]:
    f = line.split("\t")
    if len(f) < 13: continue
    a, m = asset(f[3])
    x, y, z, rx, ry, rz = map(float, f[4:10])
    truth.append(dict(id=f[0], base=f[1], model=m, asset=a, pos=(x, y, z), rot=(rx, ry, rz), scale=float(f[10]),
                      disabled=f[11] == "1", loaded=f[12] == "1"))

mine = []
for line in open(csv).read().split():
    f = line.split(",")
    if len(f) >= 8 and f[0] != "terrain":
        mine.append(dict(asset=f[0], pos=tuple(map(float, f[1:4])), rot=tuple(map(float, f[4:7])), scale=float(f[7]), used=False))

arch = [t for t in truth if t["model"].startswith("architecture/whiterun/") and "lod" not in t["asset"]]
print("truth refs with models: %d; whiterun architecture (non-LOD): %d; my placements: %d" % (len(truth), len(arch), len(mine)))

ok = moved = missing = 0
bad = []
for t in arch:
    if t["disabled"]: continue
    best, bd = None, 1e18
    for m in mine:
        if m["asset"] == t["asset"] and not m["used"]:
            d = math.dist(m["pos"], t["pos"])
            if d < bd: best, bd = m, d
    if best is None or bd > 400:
        missing += 1; bad.append(("MISSING", t, None, bd)); continue
    best["used"] = True
    dyaw = abs((math.degrees(best["rot"][2] - t["rot"][2]) + 180) % 360 - 180)
    if bd < 2 and dyaw < 1: ok += 1
    else: moved += 1; bad.append(("OFF", t, best, bd))
print("matched exactly: %d, position/rotation differs: %d, in game but not in my set: %d" % (ok, moved, missing))

extra = [m for m in mine if not m["used"] and math.hypot(m["pos"][0] - px, m["pos"][1] - py) < rad - 1500]
print("in my set but not found loaded in game (within radius): %d" % len(extra))
for m in extra[:15]:
    print("  EXTRA", m["asset"], [round(v) for v in m["pos"]])
print("--- sample mismatches ---")
for kind, t, m, d in bad[:25]:
    print(kind, t["asset"], "truth", [round(v) for v in t["pos"]], "yaw", round(math.degrees(t["rot"][2])) % 360,
          "| mine", ([round(v) for v in m["pos"]], round(math.degrees(m["rot"][2])) % 360) if m else None, "dist", round(d))

print("--- game objects by model folder (loaded, not in my set) ---")
cnt = collections.Counter()
for t in truth:
    if t["disabled"]: continue
    if t["model"].startswith("architecture/whiterun/"): continue
    parts = t["model"].split("/")
    cnt["/".join(parts[:2])] += 1
for k, v in cnt.most_common(25): print("  %5d  %s" % (v, k))
