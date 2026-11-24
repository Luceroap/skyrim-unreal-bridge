"""Write area2/tex/fabric_n.png + fabric.png: seamless woven-cloth detail (twill weave, fibre fuzz, thread-to-thread variation).

Used by remaster_materials.npc_cloth as the close-range detail layer of NPC clothes instead of the generic grit of detailgrain
(which reads as photocopier noise on cloth). fabric_n = weave relief normal, fabric.png = matching brightness (0.5 = neutral)."""
import os
import numpy as np
from PIL import Image

N = 1024
T = 32                                                    # threads per tile each way (tiled ~11x over a UV island -> ~2.5 mm threads)
TEX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "area2", "tex")


def main():
    rng = np.random.default_rng(23)
    y, x = np.mgrid[0:N, 0:N]
    cx, cy = x * T / N, y * T / N
    i, j = np.floor(cx).astype(int), np.floor(cy).astype(int)
    fx, fy = cx - i, cy - j
    warp = np.cos((fx - 0.5) * np.pi * 0.95) ** 0.8             # vertical thread: round across its width
    weft = np.cos((fy - 0.5) * np.pi * 0.95) ** 0.8             # horizontal thread
    warp_top = ((i + j) % 4) < 2                                # 2/2 twill
    h = np.where(warp_top, 0.6 + 0.4 * warp, 0.35 + 0.4 * weft) # the thread on top stands higher
    thread_var = rng.normal(0, 0.06, (T, T))                    # each thread a little thicker / thinner / brighter
    h += thread_var[j % T, i % T]
    f = np.fft.fftfreq(N) * N
    r = np.hypot(f[:, None], f[None, :])
    amp = np.where((r > 60) & (r < 300), (r + 1e-6) ** -0.5, 0)
    fuzz = np.real(np.fft.ifft2(amp * np.exp(2j * np.pi * rng.random((N, N)))))
    h += 0.10 * fuzz / (fuzz.std() + 1e-9)                      # loose fibres
    h = (h - h.mean()) / h.std()
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
    k = 1.6
    n = np.stack([-gx * k, gy * k, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).round().astype(np.uint8), "RGB").save(os.path.join(TEX, "fabric_n.png"))
    c = np.clip(0.5 + 0.10 * h + 0.5 * thread_var[j % T, i % T], 0, 1)
    Image.fromarray((c * 255).round().astype(np.uint8), "L").convert("RGB").save(os.path.join(TEX, "fabric.png"))
    print("wrote fabric_n.png + fabric.png in", TEX)


if __name__ == "__main__":
    main()
