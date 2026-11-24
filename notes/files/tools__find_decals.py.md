## Purpose
Lists diffuse textures used as decals in Skyrim (identified by specific shader property flags). Writes base texture names (lowercase) to area2/tex/decal_textures.txt for Unreal compatibility, addressing z-fighting issues by requiring camera-ward offsets.

## How it is run
Command: `python tools/find_decals.py`  
Called by: `HANDOFF_FOR_CURSOR.md` (line 83), which references the script's output for z-fighting fixes.

## Inputs
- Skyrim .nif files in `area2/nif/` (parsed binary files with mesh data).
- Shader property flags (specifically bits 26/27 in `BSLightingShaderProperty`).

## Outputs
- File: `area2/tex/decal_textures.txt` (base names of decal textures, lowercase, one per line).
- Console output: Total count of decal textures, followed by each texture name and number of models using it.

## Key functions
parse - Parses NIF binary data into structured blocks.  
R - Binary reader for NIF data structure.  
DECAL flag check - Verifies shader property bits 26/27.  
Texture extraction - Extracts and normalizes texture paths.  
Output writer - Writes sorted texture list to decal_textures.txt.

## Depends on
- `nif2obj.py` (imports `R`, `parse`).
- Standard libraries: `glob`, `os`, `sys`.

## Gotchas
- Skips NIF files that fail binary parsing (exceptions caught and ignored).
- Converts texture names to lowercase (original casing may differ).
- Only processes textures with flags 26 and 27 (BSLightingShaderProperty bits).
- Requires correct NIF file structure to detect decals.
- Writes to `area2/tex/` directory (not `area1` or other paths).

Source: read, not executed.
