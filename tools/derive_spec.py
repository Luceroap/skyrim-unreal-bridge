"""Specular masks for textures whose normal map has no specular alpha (textures_pbr.py left <key>_s.png.none).
Without one, M_SkyMaster uses one flat roughness for the whole surface, which reads as flat/"last gen" on wood and stone.
Derived from the diffuse: fine luminance detail (high-pass) -> raised/brighter grain slightly smoother, crevices rougher,
kept in 0.1..0.6 (roughness 0.84..0.54 in the master) so nothing turns plastic. Writes <key>_s.png (max 1024 px) and
lists the keys in area2/tex/derived_spec.txt. Usage: python tools/derive_spec.py"""
import glob, os
import numpy as np
from PIL import Image, ImageFilter

TEX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "area2", "tex")
SKIP = ("lodtex_", "terrain", "rainstreaks", "skywater")

done = []
for marker in glob.glob(os.path.join(TEX, "*_s.png.none")):
    key = os.path.basename(marker)[:-len("_s.png.none")]
    base = os.path.join(TEX, key + ".png")
    out = os.path.join(TEX, key + "_s.png")
    if key.startswith(SKIP) or not os.path.exists(base) or os.path.exists(out) or os.path.exists(os.path.join(TEX, key + "_rmaos.png")):
        continue
    im = Image.open(base).convert("L")
    if max(im.size) > 1024:
        im = im.resize((min(1024, im.width), min(1024, im.height)), Image.LANCZOS)
    lum = np.asarray(im, dtype=np.float32) / 255.0
    low = np.asarray(im.filter(ImageFilter.GaussianBlur(max(2, im.width // 64))), dtype=np.float32) / 255.0
    spec = 0.3 + 1.6 * (lum - low) + 0.15 * (lum - lum.mean())
    spec = np.clip(spec, 0.1, 0.6)
    Image.fromarray((spec * 255).astype(np.uint8), "L").save(out)
    done.append(key)

with open(os.path.join(TEX, "derived_spec.txt"), "a") as f:
    f.write("".join(k + "\n" for k in done))
print("derived %d specular masks" % len(done))
