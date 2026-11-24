## Purpose
Upscales low-resolution diffuse textures (≤1024px longest side) using Real-ESRGAN x2 via PyTorch CUDA, preserving originals in `area2/tex_orig/` and listing processed files in `area2/tex/upscaled.txt`. Skips textures already at 2K/4K resolution or with specific naming patterns.

## How it is run
Command: `python tools/upscale_textures.py [--max-src 1024]`  
Called by `unreal/SkyBridge/reimport_textures.py` after upscaling (as noted in its docstring), and referenced in `README.md` and `HANDOFF_FOR_CURSOR.md`.

## Inputs
- PNG texture files in `area2/tex/` with longest side ≤ `--max-src` (default 1024px) and min dimension ≥64px.
- Original file names excluding those ending in `_n`, `_rmaos`, `_s` or starting with `skywater`, `terrain`.
- `tools/models/RealESRGAN_x2plus.pth` model file.

## Outputs
- Upscaled texture PNGs replacing originals in `area2/tex/`.
- Originals copied to `area2/tex_orig/`.
- Names of processed textures appended to `area2/tex/upscaled.txt`.
- Console logs showing processed file sizes (e.g., `upscaled skywater 2048x1024 -> 4096x2048`).

## Key functions
upscale_rgb
main
ModelLoader
torch.cuda.empty_cache
os.makedirs

## Depends on
`tools/models/RealESRGAN_x2plus.pth`  
`spandrel` (model loader)  
`torch` (CUDA)  
`PIL` (image handling)  
`numpy` (array operations)  
`unreal/SkyBridge/reimport_textures.py` (post-processing trigger)

## Gotchas
- Requires CUDA-enabled PyTorch (install via `pip install torch --index-url https://download.pytorch.org/whl/cu128`).
- Skips textures named `_n`, `_rmaos`, `_s`, or starting with `skywater`, `terrain`.
- Only upscales textures with longest side ≤1024px by default (adjustable via `--max-src`).
- Alpha channel resized with Lanczos to preserve transparency.
- Min texture size of 64px required (skips smaller files).

Source: read, not executed.
