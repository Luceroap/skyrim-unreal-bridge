## Purpose
Extracts and converts normal ('_n') and PBR ('_rmaos') companion maps from Skyrim DDS textures referenced in MTL files. Expands BC5 normal maps (2-channel) to RGB format for Unreal Engine compatibility.

## How it is run
Command: `python -I tools/textures_pbr.py <Data dir> <area dir>`  
Called by: `tools/asset_service.py`, `tools/auto_build.py`, `tools/npc_build.py`, `tools/npc_build_creature.py`

## Inputs
- `data_dir`: Skyrim Data directory containing BSA archives
- `area`: Subdirectory (e.g., "area2") containing `obj/*.mtl` files referencing textures
- Texture references parsed from `area/obj/*.mtl` (via `# skyrim diffuse: path`)

## Outputs
- `area/tex/<name>_n.png`: Normal map (RGB format, BC5 reconstructed)
- `area/tex/<name>_rmaos.png`: PBR map (RGBA)
- `area/tex/<name>_s.png`: Specular mask (from normal map alpha channel)
- `area/tex/<name>_s.png.none`: Marker if specular mask was skipped

## Key functions
norm() - Path normalization
read() - Fetch DDS from BSA or loose files
decode() - Convert DDS to PIL Image
reconstruct_bc5() - Reconstruct BC5 Z channel
handle_specular() - Generate _s.png from normal map alpha

## Depends on
- `tools/bsa.py` (BSA archive handling)
- `PIL.Image` (Image processing)

## Gotchas
- Normal maps with zero alpha channel are reconstructed from X/Y channels
- Specular masks require significant alpha variation (>8 range) to generate _s.png
- Skips reprocessing if existing output files exist and no specular mask is needed
- DX10 DDS headers are modified (format code reduced by 1)
- Fails silently for invalid DDS (prints "FAILED" to stderr)

Source: read, not executed.
