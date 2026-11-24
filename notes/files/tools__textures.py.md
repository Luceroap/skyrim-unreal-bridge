## Purpose
This script extracts diffuse textures from Skyrim's BSA archives, converts them from DDS to PNG format (with DX10 format handling), and modifies MTL files to include Blender-friendly "map_Kd" texture references.

## How it is run
Command: `python -I textures.py <data_dir> <whiterun_dir>`
Called by: `tools/auto_build.py`, `tools/asset_service.py`, `tools/npc_build.py`, `tools/npc_build_creature.py`

## Inputs
- `data_dir`: Directory containing Skyrim BSA archives and loose texture files
- `whiterun_dir`: Directory containing MTL files (specifically `whiterun/obj/*.mtl`)

## Outputs
- PNG texture files in `whiterun_dir/tex/` (named after original DDS filename)
- Modified MTL files in `whiterun_dir/obj/` with added `map_Kd` lines referencing the PNG textures

## Key functions
norm: Normalize texture paths by stripping prefixes

## Depends on
tools/bsa.py, PIL.Image

## Gotchas
- Names PNGs by filename only, causing collisions for textures with same filename in different paths (e.g., `anukethreplacers/Hair/Jenassa.dds` and `anothermod/Hair/Jenassa.dds`)
- Prefers loose texture files (in `data_dir`) over BSA archives, meaning mod textures override vanilla
- Fixes "DX10" DDS files by converting SRGB formats to UNORM equivalents
- Skips already converted textures (checks for existing PNG files)
- Requires MTL files to contain "# skyrim diffuse: [texture path]" comments

Source: read, not executed.
