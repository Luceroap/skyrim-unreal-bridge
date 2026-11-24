## Purpose
Generates a seamless RGB texture map (`puddlenoise.png`) used by `M_SkyMaster` to place rain puddles in the game world. The R channel defines blobby puddle shapes while the G channel controls ragged edge detail.

## How it is run
Command: `python tools/puddle_noise.py`  
Called by: `start_bridge.py`, `demo.py`, `tools/lod_terrain.py`, `tools/derive_spec.py`, `tools/ue_run.py` (via `COORDINATION.md`).

## Inputs
Fixed RNG seed (7), hardcoded noise parameters (`base=4, octaves=5` for R channel; `base=16, octaves=4` for G channel).

## Outputs
Writes to `area2/tex/puddlenoise.png` (RGB image), printed message `wrote [path]`.

## Key functions
tiling_noise - Periodic value noise with cosine interpolation  
fbm - Fractal Brownian motion noise  
main - Entry point generating and saving image

## Depends on
`numpy`, `PIL.Image`, `os`

## Gotchas
The random seed is fixed (7), ensuring deterministic output.  
The B channel in the output image is always zero (no blue component).  
The output path is constructed relative to the script's location.  
Hardcoded noise parameters (4/5 for R, 16/4 for G) cannot be modified.  
The image is saved as `RGB` format (no alpha channel).

Source: read, not executed.
