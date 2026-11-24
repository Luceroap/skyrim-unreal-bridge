## Purpose
Identifies texture keys used by Skyrim models with Projected-UV shading (SLSF1 bit 23) and Multi-Layer Parallax shaders (type 11). Generates two text files listing these keys for use in the Skyrim-to-Unreal bridge project.

## How it is run
Executed via `python -I tools/projected_snow.py` from the project root. Called by `COORDINATION.md` (line 357) during the NIF scanning process.

## Inputs
- NIF models at `area2/nif/*.nif` (459 files scanned as noted in `COORDINATION.md`).

## Outputs
- `area2/tex/projected_snow.txt` (empty as no models use Projected-UV flag).
- `area2/tex/multilayer_textures.txt` (contains `mountainslab01` key for all 17 mountain/cliff models).
- Terminal output listing scanned NIF count and key examples.

## Key functions
parse - Extracts shader properties from NIF files.
R - Binary data parser for NIF blocks.
shader_type_check - Filters for Projected-UV and Multi-Layer shaders.
key_categorization - Groups texture keys by shader type.
output_writing - Writes keys to `projected_snow.txt`/`multilayer_textures.txt`.

## Depends on
`nif2obj.py` (for `parse` and `R`).
`glob`, `os`, `sys` (standard libraries).

## Gotchas
- Projected-UV shader (bit 23) is unused in all 459 NIFs, so `projected_snow.txt` is intentionally empty.
- Mountain/cliff meshes exclusively use Multi-Layer Parallax shader (type 11) with the `mountainslab01` key.
- Texture keys are stored as lowercase stems (e.g., `mountainslab01` from `mountainslab01.png`).
- Script skips invalid NIF files via exception handling (no error messages).
- COORDINATION.md confirms 17 mountain models share a single `mountainslab01` key.

Source: read, not executed.
