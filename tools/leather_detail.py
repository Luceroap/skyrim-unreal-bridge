"""Write area2/tex/leatherdetail_n.png + leatherdetail.png: seamless tanned-leather detail (pebbled grain, flex creases, scuffs).

Used by remaster_materials (npc_material_types.PROFILES: leather, leather_armor, metal_armor straps, creature hides) as the
close-range detail layer of leather instead of the woven fabric. Grain cells and creases are darker in leatherdetail.png,
which the master also reads as rougher (DetailRoughness)."""
import numpy as np
from detail_common import N, spectral_noise, segments, stamp, convolve, periodic_kernel, save

G = 44                                                      # pebbles per tile edge (tiled ~10x per UV island -> ~2 mm grain)


def voronoi_border(rng, g):
    """Periodic F2 - F1 (cell units) of a jittered g x g point grid: 0 on cell borders, ~0.5 at cell centres."""
    jit = rng.uniform(0.15, 0.85, (g, g, 2))
    y, x = np.mgrid[0:N, 0:N] * (g / N)
    i, j = np.floor(x).astype(int), np.floor(y).astype(int)
    f1 = np.full((N, N), 9.0)
    f2 = np.full((N, N), 9.0)
    for dj in (-1, 0, 1):
        for di in (-1, 0, 1):
            ci, cj = i + di, j + dj
            p = jit[cj % g, ci % g]
            d = np.hypot(ci + p[..., 0] - x, cj + p[..., 1] - y)
            f2 = np.where(d < f1, f1, np.minimum(f2, d))
            f1 = np.minimum(f1, d)
    return f2 - f1


def main():
    rng = np.random.default_rng(41)
    border = voronoi_border(rng, G)
    pebble = 1.0 - np.exp(-border * 4.0)                   # rounded domes, narrow grooves between them
    pebble *= 1.0 + 0.25 * spectral_noise(rng, 20, 90, -0.5)   # uneven pebble heights
    creases = np.zeros((N, N))
    for aniso, w in (((1.0, 4.0), 1.0), ((3.5, 1.0), 0.7), ((1.0, 1.0), 0.5)):
        n = spectral_noise(rng, 2, 18, -1.0, aniso)
        creases += w * np.exp(-np.abs(n) * 7.0)            # zero crossings of smooth noise = long thin folds
    creases /= creases.max()
    pts, wts = segments(rng, 70, (20, 90))
    scuff = convolve(stamp(pts, wts), periodic_kernel(lambda d: np.exp(-(d / 2.2) ** 2)))
    scuff /= scuff.max() + 1e-9
    mottle = spectral_noise(rng, 1, 8, -1.0)
    height = pebble * 1.0 - creases * 1.8 - scuff * 0.4
    bright = 0.5 + 0.03 * (pebble - pebble.mean()) / pebble.std() - 0.2 * creases + 0.07 * scuff + 0.03 * mottle
    save("leatherdetail", height, bright, 1.4)


if __name__ == "__main__":
    main()
