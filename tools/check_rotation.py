"""Compare the REFR rotation angles with the actual world rotation matrix of the loaded 3D (from the plugin dump)."""
import sys, math, collections

tsv = sys.argv[1]
rows = []
for line in open(tsv, encoding="latin1").read().splitlines()[1:]:
    f = line.split("\t")
    if len(f) < 22 or f[11] == "1":
        continue
    rx, ry, rz = map(float, f[7:10])
    m = list(map(float, f[13:22]))          # row-major world rotate
    rows.append((f[3], rx, ry, rz, m))
print(len(rows), "refs with a loaded 3D rotation")

# hypotheses for how (rx,ry,rz) map to the world matrix; test the pure-yaw refs first
def ypred_cw(z):   # clockwise heading: local +Y -> (sin z, cos z), local +X -> (cos z, -sin z)
    return [math.cos(z), math.sin(z), 0, -math.sin(z), math.cos(z), 0, 0, 0, 1]      # R (row-major) = Rz(-z)
def ypred_ccw(z):
    return [math.cos(z), -math.sin(z), 0, math.sin(z), math.cos(z), 0, 0, 0, 1]      # R = Rz(+z)
def err(a, b): return max(abs(x - y) for x, y in zip(a, b))

pure = [r for r in rows if abs(r[1]) < 1e-3 and abs(r[2]) < 1e-3]
print(len(pure), "pure-yaw refs")
c = collections.Counter()
bad = []
for name, rx, ry, rz, m in pure:
    e1, e2 = err(m, ypred_cw(rz)), err(m, ypred_ccw(rz))
    k = "cw(R=Rz(-z))" if e1 < 0.02 else "ccw(R=Rz(+z))" if e2 < 0.02 else "neither"
    c[k] += 1
    if k != "cw(R=Rz(-z))" and len(bad) < 8: bad.append((name.split("\\")[-1], round(math.degrees(rz)), [round(v, 2) for v in m]))
print(dict(c))
for b in bad: print("  ", b)

# tilted refs: find which Euler composition reproduces the matrix
def Rx(a): return [[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]]
def Ry(a): return [[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]]
def Rz(a): return [[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]]
def mul(a, b): return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
flat = lambda M: [v for row in M for v in row]
tilted = [r for r in rows if abs(r[1]) > 0.02 or abs(r[2]) > 0.02]
print(len(tilted), "tilted refs")
orders = {}
import itertools
for sx, sy, sz in itertools.product((1, -1), repeat=3):
    for order in ("xyz", "zyx", "yxz", "zxy", "xzy", "yzx"):
        ok = 0
        for name, rx, ry, rz, m in tilted:
            axes = {"x": Rx(sx * rx), "y": Ry(sy * ry), "z": Rz(sz * rz)}
            M = axes[order[0]]
            for ch in order[1:]: M = mul(M, axes[ch])
            if err(flat(M), m) < 0.02: ok += 1
        orders[(sx, sy, sz, order)] = ok
best = sorted(orders.items(), key=lambda kv: -kv[1])[:4]
print("best Euler conventions (sign x,y,z, order) -> matches:", best)
