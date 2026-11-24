## Purpose
Generates seamless fine surface grain textures for close-range detail in Skyrim materials, specifically for M_SkyMaster. Creates detailgrain_n.png (normal map for micro-bumps) and detailgrain.png (brightness variation texture) to reduce texture smear at close camera distances.

## How it is run
Execute directly via command line: `python tools/detail_noise.py`. Called by `unreal/SkyBridge/remaster_materials.py` (via comment line 118).

## Inputs
Hardcoded parameters (N=1024, seed=11), spectral noise frequency ranges (8-60, 60-220, 220-480 cycles/tile), and slopes (0.9, 0.6, 0.3).

## Outputs
Writes two files to `area2/tex/`:
- `detailgrain_n.png` (RGB normal map, 1024×1024)
- `detailgrain.png` (L grayscale brightness variation, 1024×1024)

## Key functions
spectral_noise - FFT-based band-limited noise generator
main - Entry point producing output textures
pits - Creates sparse small pits/grit
normal_map - Computes surface normal from height field
brightness_variation - Clips and scales noise for detailgrain.png

## Depends on
`unreal/SkyBridge/remaster_materials.py` (calls via referenced comment)
`numpy`, `PIL`, `os` (standard libraries)

## Gotchas
- Hardcoded RNG seed (11) produces identical outputs on every run
- Output directory `area2/tex` is hardcoded and must exist
- Noise parameters (8-60, 60-220, etc.) are fixed in code
- Output resolution fixed at 1024×1024
- Writes directly to project's `area2/tex` without configuration

Source: read, not executed.
