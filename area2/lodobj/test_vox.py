import json, math, collections, sys, time
import numpy as np
sys.path.insert(0, 'tools')
import nif2obj, lod_objects as L

VOX = float(sys.argv[2]) if len(sys.argv) > 2 else 128.0
d = json.load(open('area2/distant_refs.json'))
t0 = time.time()
geo = {}
for m in {i['model'] for i in d}:
    vs, fs = [], []
    for l in open('area2/obj/' + m + '.obj'):
        if l.startswith('v '):
            vs.append(list(map(float, l.split()[1:4])))
        elif l.startswith('f '):
            fs.append([int(x.split('/')[0]) - 1 for x in l.split()[1:4]])
    V = np.array(vs); F = np.array(fs)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    S = np.concatenate([V, (a + b + c) / 3, (a + b) / 2, (b + c) / 2, (a + c) / 2])
    geo[m] = S
print('geo', time.time() - t0, sum(len(s) for s in geo.values()))
lvl, bx, by = map(int, sys.argv[1].split('.'))
open('area2/lodobj/tmp.bto', 'wb').write(L.read_data(r'meshes\terrain\tamriel\objects\tamriel.%d.%d.%d.bto' % (lvl, bx, by), L.MESH_BSAS))
sh = nif2obj.extract('area2/lodobj/tmp.bto')
x0, y0, x1, y1 = bx * 4096 - 2048, by * 4096 - 2048, (bx + lvl) * 4096 + 2048, (by + lvl) * 4096 + 2048
keys = []
for it in d:
    S = geo[it['model']]
    R = np.array(it['rot']).reshape(3, 3)
    W = S @ R.T * it['scale'] + np.array(it['pos'])
    m = (W[:, 0] > x0) & (W[:, 0] < x1) & (W[:, 1] > y0) & (W[:, 1] < y1)
    if m.any():
        keys.append(np.floor(W[m] / VOX).astype(np.int64))
K = np.concatenate(keys)
enc = lambda k: (k[:, 0] + 2**20) * 2**42 + (k[:, 1] + 2**20) * 2**21 + (k[:, 2] + 2**20)
occ = set()
base = np.unique(enc(K))
for dx in (-1, 0, 1):
    for dy in (-1, 0, 1):
        for dz in (-1, 0, 1):
            occ.append if False else None
dil = np.unique(np.concatenate([enc(K + np.array([dx, dy, dz])) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)]))
print('vox', len(base), len(dil), time.time() - t0)
tot = collections.Counter(); drop = collections.Counter()
for n, vs, uv, tr, tex in sh:
    V = np.array(vs)
    inside = np.isin(enc(np.floor(V / VOX).astype(np.int64)), dil)
    for g in L.pieces(vs, tr):
        ids = np.array(sorted({i for t in g for i in tr[t]}))
        k = tex.split('\\')[-1] if tex else None
        tot[k] += len(g)
        if inside[ids].mean() > 0.8:
            drop[k] += len(g)
for k in tot:
    print('%-32s %7d tris, dropped %5.1f%%' % (k, tot[k], 100.0 * drop[k] / tot[k]))
print(time.time() - t0)
