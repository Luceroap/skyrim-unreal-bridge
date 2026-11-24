"""Write area2/tex/detailgrain_n.png + detailgrain.png: seamless fine surface grain for M_SkyMaster's close-range detail.

Skyrim's textures are 512-2048 px stretched over metres of mesh, so up close they look smeared. The master material tiles
this grain at a multiple of the mesh UVs and fades it in near the camera: normal = micro bumps (pits, grit, fibres),
detailgrain.png = matching brightness variation (0.5 = neutral).
"""
import os
import numpy as np
from PIL import Image

N = 1024
TEX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "area2", "tex")


def spectral_noise(rng, lo, hi, slope):
    """Periodic band-limited noise via FFT: frequencies lo..hi (cycles per tile), amplitude ~ f^-slope. Wraps exactly."""
    f = np.fft.fftfreq(N) * N
    r = np.hypot(f[:, None], f[None, :])
    amp = np.where((r >= lo) & (r <= hi), (r + 1e-6) ** -slope, 0.0)
    ph = np.exp(2j * np.pi * rng.random((N, N)))
    v = np.real(np.fft.ifft2(amp * ph))
    return (v - v.mean()) / (v.std() + 1e-9)


def main():
    rng = np.random.default_rng(11)
    h = 0.55 * spectral_noise(rng, 8, 60, 0.9) + 0.35 * spectral_noise(rng, 60, 220, 0.6) + 0.10 * spectral_noise(rng, 220, 480, 0.3)
    pits = np.clip(spectral_noise(rng, 40, 160, 0.5) - 1.6, 0, None)        # sparse small pits / grit
    h = h - 1.5 * pits
    h = (h - h.mean()) / h.std()
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
    k = 2.2
    n = np.stack([-gx * k, gy * k, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).round().astype(np.uint8), "RGB").save(os.path.join(TEX, "detailgrain_n.png"))
    c = np.clip(0.5 + 0.12 * h, 0, 1)
    Image.fromarray((c * 255).round().astype(np.uint8), "L").convert("RGB").save(os.path.join(TEX, "detailgrain.png"))
    print("wrote detailgrain_n.png + detailgrain.png in", TEX)


if __name__ == "__main__":
    main()
