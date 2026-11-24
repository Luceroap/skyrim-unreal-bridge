"""Shared helpers for the seamless close-range detail textures (leather_detail.py, metal_detail.py, skin_detail.py).

Everything is periodic on an N x N tile (FFT noise, circular convolution, wrapped stamping), so the outputs tile with no seams.
Each texture pair is <stem>_n.png (tangent-space normal, +Y up like fabric_n) and <stem>.png (brightness, 0.5 = neutral):
M_SkyMaster reads the brightness as a colour multiplier (x2) and as a roughness offset (darker = rougher, DetailRoughness)."""
import os
import numpy as np
from PIL import Image

N = 1024
TEX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "area2", "tex")


def spectral_noise(rng, lo, hi, slope=-0.5, aniso=(1.0, 1.0)):
    """Band-limited noise (frequencies lo..hi cycles per tile), unit std. aniso stretches the spectrum per axis (x, y)."""
    f = np.fft.fftfreq(N) * N
    r = np.hypot(f[None, :] * aniso[0], f[:, None] * aniso[1])
    amp = np.where((r >= lo) & (r <= hi), (r + 1e-6) ** slope, 0.0)
    n = np.real(np.fft.ifft2(amp * np.exp(2j * np.pi * rng.random((N, N)))))
    return n / (n.std() + 1e-9)


def periodic_kernel(fn):
    """Kernel image fn(distance in px) centred on pixel (0, 0) with wrap-around distances, for circular convolution."""
    d = np.minimum(np.arange(N), N - np.arange(N)).astype(float)
    return fn(np.hypot(d[None, :], d[:, None]))


def convolve(img, kernel):
    return np.real(np.fft.ifft2(np.fft.fft2(img) * np.fft.fft2(kernel)))


def stamp(points, weights=None):
    """Impulse image: weight added at each (x, y) point (floats, wrapped)."""
    img = np.zeros((N, N))
    p = np.asarray(points)
    xi = np.floor(p[:, 0]).astype(int) % N
    yi = np.floor(p[:, 1]).astype(int) % N
    np.add.at(img, (yi, xi), 1.0 if weights is None else weights)
    return img


def segments(rng, count, length, angle=None, angle_jitter=np.pi):
    """Points along `count` random straight scratches (lengths in px, ~2 samples per px), wrapped onto the tile."""
    pts, wts = [], []
    for _ in range(count):
        L = rng.uniform(*length)
        a = (angle if angle is not None else 0.0) + rng.uniform(-angle_jitter, angle_jitter)
        x0, y0 = rng.uniform(0, N, 2)
        t = np.linspace(0.0, 1.0, max(2, int(L * 2)))
        depth = rng.uniform(0.4, 1.0) * np.sin(np.pi * t) ** 0.5            # scratches fade in/out at their ends
        pts.append(np.stack([x0 + np.cos(a) * L * t, y0 + np.sin(a) * L * t], -1))
        wts.append(depth * 0.5)                                            # 2 samples per px -> unit line density
    return np.concatenate(pts), np.concatenate(wts)


def save(stem, height, brightness, strength):
    """Normalise height, write <stem>_n.png (normal, `strength` = slope gain) and <stem>.png (brightness, re-centred on 0.5)."""
    h = (height - height.mean()) / (height.std() + 1e-9)
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
    n = np.stack([-gx * strength, gy * strength, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    os.makedirs(TEX, exist_ok=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).round().astype(np.uint8), "RGB").save(os.path.join(TEX, stem + "_n.png"))
    c = np.clip(brightness - brightness.mean() + 0.5, 0.0, 1.0)          # mean 0.5: no overall darkening up close
    Image.fromarray((c * 255).round().astype(np.uint8), "L").convert("RGB").save(os.path.join(TEX, stem + ".png"))
    print("wrote %s_n.png + %s.png in %s (brightness mean %.3f, std %.3f)" % (stem, stem, TEX, c.mean(), c.std()))
