"""Downhill flow direction for every water strip in area2/water_quads.csv -> area2/water_flow.csv (same line order).
Skyrim stores no flow vectors for exterior water, so the flow is the along-channel slope of the river bed: terrain heights (LAND VHGT)
are smoothed over the wet squares only (cross-channel bank slopes cancel, the along-channel slope stays) and the flow is the negative gradient.
Columns: fx,fy,speed   (fx, fy = unit direction in Skyrim axes, x east / y north; speed 0..1: lakes ~0.1, steep rivers 1)
Usage: python -I water_flow.py"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import distant_world as dw

ROOT = dw.ROOT
STEP = 128.0

cells, worlds, land = {}, {}, {}
for p in dw.PLUGINS:
    if os.path.exists(os.path.join(dw.DATA, p)):
        dw.read_water(os.path.join(dw.DATA, p), cells, worlds, land=land)
print("water cells", len(cells), "land cells", len(land))

gxs = [k[0] for k in land]; gys = [k[1] for k in land]
gx0, gy0 = min(gxs), min(gys)
W, Hh = (max(gxs) - gx0 + 1) * 32, (max(gys) - gy0 + 1) * 32
H = np.full((Hh, W), np.nan, dtype=np.float32)          # H[row=y, col=x], 128-unit samples
WL = np.full((Hh, W), np.nan, dtype=np.float32)         # water level of the cell (nan = no water)
for (gx, gy), hm in land.items():
    a = np.array(hm, dtype=np.float32)[:32, :32]
    r0, c0 = (gy - gy0) * 32, (gx - gx0) * 32
    H[r0:r0 + 32, c0:c0 + 32] = a
    if (gx, gy) in cells:
        WL[r0:r0 + 32, c0:c0 + 32] = cells[(gx, gy)]
wet = (H < WL) & ~np.isnan(H)


def gauss(sig):
    r = int(3 * sig)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2)
    return k / k.sum()


def blur(a, sig):
    k = gauss(sig)
    a = np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 1, a)
    return np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 0, a)


M = wet.astype(np.float32)
Hz = np.where(wet, H, 0.0).astype(np.float32)
SIG = 3.0                                                # squares (~380 units): wider than a river, narrower than its bends
Hs = blur(Hz, SIG) / np.maximum(blur(M, SIG), 1e-3)
gy_, gx_ = np.gradient(Hs, STEP)                          # d/dy (rows), d/dx (cols), height units per unit distance
fx, fy = -gx_, -gy_

n_out, speeds = 0, []
with open(os.path.join(ROOT, "area2", "water_quads.csv")) as fin, open(os.path.join(ROOT, "area2", "water_flow.csv"), "w") as fout:
    for line in fin.read().split():
        x0, y0, n, h = line.split(",")
        x0, y0, n = int(x0), int(y0), int(n)
        r = int(round(y0 / STEP)) - gy0 * 32
        c0 = int(round(x0 / STEP)) - gx0 * 32
        vx = vy = 0.0; cnt = 0
        for c in range(c0, c0 + n):
            if 0 <= r < Hh and 0 <= c < W and wet[r, c]:
                vx += fx[r, c]; vy += fy[r, c]; cnt += 1
        if cnt == 0:
            for c in range(c0, c0 + n):
                if 0 <= r < Hh and 0 <= c < W and not np.isnan(Hs[r, c]):
                    vx += fx[r, c]; vy += fy[r, c]; cnt += 1
        if cnt:
            vx /= cnt; vy /= cnt
        mag = (vx * vx + vy * vy) ** 0.5
        if mag < 1e-6:
            fout.write("0,0,0\n"); continue
        sp = float(np.clip(mag / 0.03, 0.12, 1.0)) if mag > 0.002 else 0.08   # nearly flat (lakes, pools): slow drift
        fout.write("%.4f,%.4f,%.3f\n" % (vx / mag, vy / mag, sp)); n_out += 1; speeds.append(sp)
print("wrote %d strips with flow; speed percentiles 10/50/90: %s" % (n_out, np.percentile(speeds, [10, 50, 90]).round(2) if speeds else "-"))
