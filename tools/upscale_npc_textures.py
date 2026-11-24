"""AI-upscale low-resolution NPC body, face, hair, and armor textures.

Uses the existing RealESRGAN x2 model and CUDA path, but targets area2/npc/tex
and keeps originals in area2/npc/tex_orig.
"""
import glob
import os
import shutil
import sys

import numpy as np
import spandrel
import torch
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "area2", "npc", "tex")
ORIG = os.path.join(ROOT, "area2", "npc", "tex_orig")
DONE = os.path.join(TEX, "upscaled.txt")
MODEL = os.path.join(ROOT, "tools", "models", "RealESRGAN_x2plus.pth")
TILE, PAD = 384, 16


def upscale_rgb(model, rgb):
    h, w, _ = rgb.shape
    out = np.zeros((h * 2, w * 2, 3), np.uint8)
    for y in range(0, h, TILE):
        for x in range(0, w, TILE):
            y0, x0 = max(0, y - PAD), max(0, x - PAD)
            y1, x1 = min(h, y + TILE + PAD), min(w, x + TILE + PAD)
            source = torch.from_numpy(rgb[y0:y1, x0:x1].copy()).permute(2, 0, 1).float().div(255).unsqueeze(0).cuda().half()
            with torch.no_grad():
                result = model(source).clamp(0, 1)
            image = (result[0].permute(1, 2, 0).float().cpu().numpy() * 255 + 0.5).astype(np.uint8)
            ty, tx = (y - y0) * 2, (x - x0) * 2
            th, tw = (min(h, y + TILE) - y) * 2, (min(w, x + TILE) - x) * 2
            out[y * 2:y * 2 + th, x * 2:x * 2 + tw] = image[ty:ty + th, tx:tx + tw]
    return out


def main():
    if not torch.cuda.is_available():
        sys.exit("CUDA PyTorch is required")
    model = spandrel.ModelLoader().load_from_file(MODEL).model.cuda().half().eval()
    done = set(open(DONE).read().split()) if os.path.exists(DONE) else set()
    os.makedirs(ORIG, exist_ok=True)
    count = 0
    for path in sorted(glob.glob(os.path.join(TEX, "*.png"))):
        key = os.path.splitext(os.path.basename(path))[0]
        if key in done or key.endswith(("_n", "_s", "_rmaos")):
            continue
        image = Image.open(path)
        if max(image.size) > 1024 or min(image.size) < 64:
            continue
        shutil.copy2(path, os.path.join(ORIG, os.path.basename(path)))
        rgba = image.convert("RGBA")
        result = Image.fromarray(upscale_rgb(model, np.asarray(rgba.convert("RGB"))))
        if rgba.getchannel("A").getextrema()[0] < 255:
            result.putalpha(rgba.getchannel("A").resize(result.size, Image.Resampling.LANCZOS))
        result.save(path)
        with open(DONE, "a") as handle:
            handle.write(key + "\n")
        count += 1
        print("upscaled %s %s -> %s" % (key, image.size, result.size), flush=True)
    torch.cuda.empty_cache()
    print("done: %d NPC textures" % count)


if __name__ == "__main__":
    main()
