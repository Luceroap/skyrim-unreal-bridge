## Purpose
Derives specular masks for textures lacking specular alpha in their normal maps, ensuring detailed roughness variation on materials like wood and stone to avoid a flat appearance. Outputs are saved as _s.png files in the same directory and appended to `area2/tex/derived_spec.txt`.

## How it is run
Command line: `python tools/derive_spec.py`. Called by `start_bridge.py`, `demo.py`, `tools/lod_terrain.py`, `tools/puddle_noise.py`, and `tools/ue_run.py` as indicated in `COORDINATION.md`.

## Inputs
- Files matching `*_s.png.none` in `area2/tex/`
- Corresponding base `.png` textures (e.g., `key.png` for `key_s.png.none`)
- Skips entries starting with `lodtex_`, `terrain`, `rainstreaks`, or `skywater`
- Skips if base file missing, output `_s.png` exists, or `_rmaos.png` exists

## Outputs
- New `_s.png` files in `area2/tex/` (max 1024px resolution)
- Appended list of processed texture keys in `area2/tex/derived_spec.txt`

## Key functions
Loop over texture markers  
Resize oversized textures  
Calculate luminance detail  
Generate specular roughness  
Save derived mask  

## Depends on
numpy, PIL (Pillow), os, glob  
Project directory structure (`area2/tex/`)

## Gotchas
- Skips `lodtex_`, `terrain`, `rainstreaks`, and `skywater` prefixes
- Ignores files if output `_s.png` or `_rmaos.png` already exists
- Resizes textures exceeding 1024px to 1024x1024
- Uses Gaussian blur for low-frequency luminance
- Appends keys to `derived_spec.txt` without overwriting

Source: read, not executed.
