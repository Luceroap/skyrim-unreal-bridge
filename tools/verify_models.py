"""Automatic comparison: game truth (plugin dump with bounds) vs my converted models.
Usage: python -I verify_models.py <refs.tsv> <area2 dir> [placements.csv]
Checks per model (aggregated over all its loaded references):
  A. geometry: predicted bound centre (= root translate + scale * R * local bbox centre, using the game's own root transform)
     vs the game's world bound centre. Reports error relative to the game's bound radius and tests mirror/axis variants.
  B. coverage: loaded models that have no converted OBJ / no placement in Unreal.
  C. scale: game scale vs placement scale."""
import sys, os, math, collections, json

tsv, area = sys.argv[1], sys.argv[2]
csv = sys.argv[3] if len(sys.argv) > 3 else os.path.join(area, "placements.csv")


def asset(m):
    m = m.lower().replace("\\", "/")
    if m.startswith("meshes/"): m = m[7:]
    return m[:-4].replace("/", "_") if m.endswith(".nif") else None


def obj_bounds(path):
    xs, ys, zs = [], [], []
    for l in open(path):
        if l.startswith("v "):
            _, x, y, z = l.split()[:4]
            xs.append(float(x)); ys.append(float(y)); zs.append(float(z))
    if not xs: return None
    c = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
    r = max(math.dist(c, (x, y, z)) for x, y, z in zip(xs, ys, zs))
    return c, r


placed = collections.Counter(l.split(",")[0] for l in open(csv).read().split() if l)
models = collections.defaultdict(list)
for line in open(tsv, encoding="latin1").read().splitlines()[1:]:
    f = line.split("\t")
    if len(f) < 30 or f[11] == "1":
        continue
    a = asset(f[3])
    if not a: continue
    m = list(map(float, f[13:22])); bc = list(map(float, f[22:25])); br = float(f[25]); T = list(map(float, f[26:29])); s = float(f[29])
    models[a].append(dict(R=m, bc=bc, br=br, T=T, s=s, scale=float(f[10]), model=f[3]))
print("models with measured 3D bounds:", len(models))

VARIANTS = {
    "as-is": lambda c: c,
    "mirror-x": lambda c: (-c[0], c[1], c[2]),
    "mirror-y": lambda c: (c[0], -c[1], c[2]),
    "rot180z": lambda c: (-c[0], -c[1], c[2]),
    "swap-xy": lambda c: (c[1], c[0], c[2]),
    "swap-xy-neg": lambda c: (-c[1], -c[0], c[2]),
    "rot90z": lambda c: (-c[1], c[0], c[2]),
    "rot-90z": lambda c: (c[1], -c[0], c[2]),
}
bad, good, nogeo, skipped = [], 0, [], 0
for a, refs in sorted(models.items()):
    p = os.path.join(area, "obj", a + ".obj")
    if not os.path.exists(p):
        nogeo.append((a, len(refs), placed.get(a, 0))); continue
    ob = obj_bounds(p)
    if not ob: continue
    cl, rl = ob
    res = {}
    for name, fn in VARIANTS.items():
        errs = []
        for r in refs:
            c = fn(cl); R = r["R"]
            w = [r["T"][i] + r["s"] * sum(R[i * 3 + k] * c[k] for k in range(3)) for i in range(3)]
            errs.append(math.dist(w, r["bc"]) / max(r["br"], 1.0))
        res[name] = sum(errs) / len(errs)
    base = res["as-is"]
    best = min(res, key=res.get)
    rad_ratio = (rl * refs[0]["s"]) / max(refs[0]["br"], 1.0)
    if base < 0.35 and 0.5 < rad_ratio < 2.0:
        good += 1
    else:
        bad.append((a, len(refs), round(base, 2), best, round(res[best], 2), round(rad_ratio, 2)))

print("geometry OK: %d models; suspicious: %d; loaded-but-not-converted: %d" % (good, len(bad), len(nogeo)))
print("\n-- suspicious models (error = bound-centre error / game bound radius; best = variant that fits better) --")
for b in sorted(bad, key=lambda b: -b[1])[:40]:
    print("  %-62s refs=%-3d err=%-5s best=%-12s (%s) radius_ratio=%s" % b)
print("\n-- loaded in game but NOT converted/placed (by ref count) --")
for a, n, pl in sorted(nogeo, key=lambda x: -x[1])[:30]:
    print("  %-70s loaded=%-4d placed=%d" % (a, n, pl))
sc = [(a, refs[0]["scale"], len(refs)) for a, refs in models.items() if any(abs(r["scale"] - 1) > 0.01 for r in refs)]
print("\nmodels placed with non-1 scale in game:", len(sc))
json.dump({"suspicious": bad, "not_converted": nogeo}, open(os.path.join(area, "verify_report.json"), "w"), indent=1)
