"""Write area2/tex/skindetail_n.png + skindetail.png: seamless human-skin micro detail (pores, cross-hatched micro-wrinkles,
faint mottling).

Used by remaster_materials (npc_material_types.PROFILES: skin, skin_beast, creature_skin, bone) at a high tiling over the
head/body UVs, so up close faces stop looking like smooth painted plastic. Pores are slightly darker (and so rougher) in
skindetail.png; the colour variation is kept very small because the face tint already carries the real skin colour."""
import numpy as np
from detail_common import N, spectral_noise, stamp, convolve, periodic_kernel, save


def main():
    rng = np.random.default_rng(73)
    g = 96                                                                  # jittered grid -> evenly spread, never clumped pores
    cell = N / g
    gy, gx = np.mgrid[0:g, 0:g]
    pts = np.stack([(gx + rng.uniform(0.1, 0.9, (g, g))) * cell, (gy + rng.uniform(0.1, 0.9, (g, g))) * cell], -1).reshape(-1, 2)
    keep = rng.random(len(pts)) < 0.8
    pores = convolve(stamp(pts[keep], rng.uniform(0.4, 1.0, keep.sum())), periodic_kernel(lambda d: np.exp(-(d / 1.6) ** 2)))
    big = convolve(stamp(rng.uniform(0, N, (500, 2)), rng.uniform(0.5, 1.0, 500)), periodic_kernel(lambda d: np.exp(-(d / 2.8) ** 2)))
    pores = pores / pores.max() + 0.6 * big / big.max()
    warp = spectral_noise(rng, 2, 10, -1.0) * 6.0
    y, x = np.mgrid[0:N, 0:N].astype(float)
    hatch = np.zeros((N, N))
    for a, f in ((0.55, 36), (-0.6, 32), (1.45, 20)):                       # skin's diamond micro-relief: 2-3 crossing line sets
        # integer cycles along each axis keep the lines periodic on the tile
        u = (round(f * np.cos(a)) * x + round(f * np.sin(a)) * y) / N + warp / N * f
        hatch += np.exp(-np.abs(np.sin(np.pi * u)) * 9.0)
    hatch /= hatch.max()
    mottle = spectral_noise(rng, 2, 24, -1.0)
    height = -pores * 1.0 - hatch * 0.55 + spectral_noise(rng, 60, 300, -0.4) * 0.08
    bright = 0.5 - 0.07 * np.clip(pores, 0, 1.5) - 0.035 * hatch + 0.02 * mottle
    save("skindetail", height, bright, 0.9)


if __name__ == "__main__":
    main()
