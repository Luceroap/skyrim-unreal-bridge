"""Compare Unreal's placed-object bounds (area2/ue_actors.csv, written by the game at startup) with the game's own bounds
(plugin dump with bounds). Both sides are converted to Unreal space; an error is reported per placed object and per model.
Usage: python -I verify_unreal.py <refs_with_bounds.tsv> <area2 dir>"""
import sys, os, math, collections

tsv, area = sys.argv[1:3]
U = 1.4287
rows = [l.split(",") for l in open(os.path.join(area, "placements.csv")).read().split()]
ue = [l.split(",") for l in open(os.path.join(area, "ue_actors.csv")).read().split() if l]
ue_rows = {}   # (model, rounded placement pos) -> bounds
placements = [r for r in rows if r[0] != "terrain"]
# ue_actors.csv has one row per placement whose mesh loaded, in file order; rebuild the same filter by matching names/positions
by_name = collections.defaultdict(list)
for u in ue:
    by_name[u[0]].append([float(v) for v in u[1:]])


def asset(m):
    m = m.lower().replace("\\", "/")
    if m.startswith("meshes/"): m = m[7:]
    return m[:-4].replace("/", "_") if m.endswith(".nif") else None


truth = []
for line in open(tsv, encoding="latin1").read().splitlines()[1:]:
    f = line.split("\t")
    if len(f) < 30 or f[11] == "1": continue
    a = asset(f[3])
    if not a: continue
    truth.append((a, [float(v) for v in f[4:7]], [float(v) for v in f[22:25]], float(f[25])))

res = collections.defaultdict(list)
matched = missing = 0
for a, pos, bc, br in truth:
    cand = by_name.get(a)
    if not cand:
        missing += 1; continue
    # the Unreal actor of this model nearest to the game's position (UE space: x<->y swap, cm)
    ue_pos = (pos[1] * U, pos[0] * U, pos[2] * U)
    best = min(cand, key=lambda c: math.dist(ue_pos, c[0:3]))
    if math.dist(ue_pos, best[0:3]) > 150: missing += 1; continue
    exp = (bc[1] * U, bc[0] * U, bc[2] * U)
    err = math.dist(exp, best[3:6]) / max(br * U, 1.0)
    res[a].append((err, best[6] / max(br * U, 1.0)))
    matched += 1
print("truth objects: %d, matched to an Unreal actor: %d, no Unreal actor within 1.5 m: %d" % (len(truth), matched, missing))
bad = []
for a, v in res.items():
    e = sorted(x[0] for x in v)[len(v) // 2]; rr = sorted(x[1] for x in v)[len(v) // 2]
    if e > 0.35 or not 0.5 < rr < 2.0: bad.append((a, len(v), round(e, 2), round(rr, 2)))
ok = len(res) - len(bad)
print("models whose Unreal bounds agree with the game: %d / %d" % (ok, len(res)))
for b in sorted(bad, key=lambda b: -b[2])[:30]: print("  MISMATCH %-60s refs=%-3d bound-centre err=%s (x radius)  radius ratio=%s" % b)
