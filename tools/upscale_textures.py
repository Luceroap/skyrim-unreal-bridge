"""AI-upscale (Real-ESRGAN x2, CUDA) the low-resolution diffuse textures in area2/tex.

Only diffuse maps whose longest side is <= MAX_SRC (most textures are already 2K/4K from texture mods; upscaling those
would only cost VRAM). Alpha is resized with Lanczos. Originals are kept in area2/tex_orig/, finished names are listed
in area2/tex/upscaled.txt. Afterwards re-import the textures (editor closed):
  UnrealEditor-Cmd.exe SkyBridge.uproject -run=pythonscript -script=unreal/SkyBridge/reimport_textures.py
Usage: python tools/upscale_textures.py [--max-src 1024]
"""
import argparse, glob, os, shutil, sys
import numpy as np
import torch
import spandrel
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "area2", "tex")
ORIG = os.path.join(ROOT, "area2", "tex_orig")
DONE = os.path.join(TEX, "upscaled.txt")
MODEL = os.path.join(ROOT, "tools", "models", "RealESRGAN_x2plus.pth")
TILE, PAD = 384, 16


def upscale_rgb(model, s, rgb):
    """rgb: HxWx3 uint8 -> (sH)x(sW)x3 uint8, processed in padded tiles to keep VRAM low (Skyrim + Unreal share the GPU)."""
    h, w, _ = rgb.shape
    out = np.zeros((h * s, w * s, 3), np.uint8)
    t = torch.from_numpy(rgb.copy()).permute(2, 0, 1).float().div(255).unsqueeze(0).cuda().half()
    for y in range(0, h, TILE):
        for x in range(0, w, TILE):
            y0, x0 = max(0, y - PAD), max(0, x - PAD)
            y1, x1 = min(h, y + TILE + PAD), min(w, x + TILE + PAD)
            with torch.no_grad():
                r = model(t[:, :, y0:y1, x0:x1]).clamp(0, 1)
            r = (r[0].permute(1, 2, 0).float().cpu().numpy() * 255 + 0.5).astype(np.uint8)
            ty, tx = (y - y0) * s, (x - x0) * s
            th, tw = (min(h, y + TILE) - y) * s, (min(w, x + TILE) - x) * s
            out[y * s:y * s + th, x * s:x * s + tw] = r[ty:ty + th, tx:tx + tw]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-src", type=int, default=1024)
    a = ap.parse_args()
    if not torch.cuda.is_available():
        sys.exit("CUDA PyTorch required (pip install torch --index-url https://download.pytorch.org/whl/cu128)")
    desc = spandrel.ModelLoader().load_from_file(MODEL)
    model = desc.model.cuda().half().eval()
    done = set(open(DONE).read().split()) if os.path.exists(DONE) else set()
    os.makedirs(ORIG, exist_ok=True)
    n = 0
    for f in sorted(glob.glob(os.path.join(TEX, "*.png"))):
        key = os.path.splitext(os.path.basename(f))[0]
        if key in done or key.endswith(("_n", "_rmaos", "_s")) or key.startswith(("skywater", "terrain")):
            continue
        im = Image.open(f)
        if max(im.size) > a.max_src or min(im.size) < 64:
            continue
        shutil.copy2(f, os.path.join(ORIG, os.path.basename(f)))
        rgba = im.convert("RGBA")
        rgb = np.asarray(rgba.convert("RGB"))
        up = Image.fromarray(upscale_rgb(model, desc.scale, rgb))
        if im.mode in ("RGBA", "LA", "P") and rgba.split()[3].getextrema()[0] < 255:
            up.putalpha(rgba.split()[3].resize(up.size, Image.LANCZOS))
        up.save(f)
        with open(DONE, "a") as fh:
            fh.write(key + "\n")
        n += 1
        print("upscaled %s %s -> %s" % (key, im.size, up.size), flush=True)
    torch.cuda.empty_cache()
    print("done: %d textures" % n)


if __name__ == "__main__":
    main()
