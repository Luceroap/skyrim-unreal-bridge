"""Write area2/tex/puddlenoise.png: seamless low-frequency fBm used by M_SkyMaster to place rain puddles in world space.

R = puddle shape noise (blobby, a few puddles per tile), G = finer noise for ragged puddle edges.
"""
import os
import numpy as np
from PIL import Image

N = 512
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "area2", "tex", "puddlenoise.png")


def tiling_noise(rng, cells):
    """Periodic value noise: random grid of `cells` x `cells`, smooth (cosine) interpolation, wraps at the edges."""
    g = rng.random((cells, cells))
    x = np.arange(N) * cells / N
    i0 = np.floor(x).astype(int); f = x - i0
    f = 0.5 - 0.5 * np.cos(np.pi * f)
    i1 = (i0 + 1) % cells
    a = g[np.ix_(i0, i0)]; b = g[np.ix_(i0, i1)]; c = g[np.ix_(i1, i0)]; d = g[np.ix_(i1, i1)]
    fy, fx = f[:, None], f[None, :]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(rng, base, octaves):
    v = np.zeros((N, N)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        v += amp * tiling_noise(rng, base * 2 ** o); tot += amp; amp *= 0.5
    v /= tot
    return (v - v.min()) / (v.max() - v.min())


def main():
    rng = np.random.default_rng(7)
    r = fbm(rng, 4, 5)
    g = fbm(rng, 16, 4)
    img = np.stack([r, g, np.zeros_like(r)], -1)
    Image.fromarray((img * 255).astype(np.uint8), "RGB").save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
