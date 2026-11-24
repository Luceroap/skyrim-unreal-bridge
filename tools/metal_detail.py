"""Write area2/tex/metaldetail_n.png + metaldetail.png: seamless worked-metal detail (hammer dents, brushing, scratches, pits).

Used by remaster_materials as the armor detail layer (npc_material_types.PROFILES: metal_armor / leather_armor metal parts via
the spec-mask split, jewelry, dwarven creatures). Scratches and pits are darker in metaldetail.png (grime collects in them),
which the master also reads as rougher, so worn edges break up the clean Skyrim specular."""
import numpy as np
from detail_common import N, spectral_noise, segments, stamp, convolve, periodic_kernel, save


def main():
    rng = np.random.default_rng(57)
    dents = stamp(rng.uniform(0, N, (260, 2)), rng.uniform(0.5, 1.0, 260))
    dents = -convolve(dents, periodic_kernel(lambda d: np.clip(1.0 - (d / 46.0) ** 2, 0, 1) ** 2))   # overlapping peen marks
    brushed = spectral_noise(rng, 40, 420, -0.3, (0.08, 1.0))                                     # fine streaks along U
    pts, wts = segments(rng, 900, (8, 70))
    fine_scr = convolve(stamp(pts, wts), periodic_kernel(lambda d: np.exp(-(d / 0.8) ** 2)))
    pts, wts = segments(rng, 60, (60, 220))
    deep_scr = convolve(stamp(pts, wts), periodic_kernel(lambda d: np.exp(-(d / 1.4) ** 2)))
    pits = stamp(rng.uniform(0, N, (1400, 2)), rng.uniform(0.3, 1.0, 1400))
    pits = convolve(pits, periodic_kernel(lambda d: np.exp(-(d / 1.3) ** 2)))
    for a in (fine_scr, deep_scr, pits):
        a /= np.percentile(a, 99.9) + 1e-9
    tarnish = spectral_noise(rng, 1, 10, -1.2)
    height = dents / dents.std() * 0.7 + brushed * 0.12 - fine_scr * 0.6 - deep_scr * 1.2 - pits * 0.8
    bright = (0.5 + 0.03 * brushed - 0.10 * np.clip(fine_scr, 0, 1) - 0.18 * np.clip(deep_scr, 0, 1)
              - 0.14 * np.clip(pits, 0, 1) + 0.03 * tarnish + 0.02 * dents / dents.std())
    save("metaldetail", height, bright, 1.1)


if __name__ == "__main__":
    main()
