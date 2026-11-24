## Purpose
Fills missing diffuse color maps for textures with _n.png filenames (no corresponding .png) by sourcing from Skyrim's game data (loose files, PBR folders, BSA archives, and mods). Updates alpha masking entries for textures with >5% transparency.

## How it is run
Command: `python tools/fill_textures.py` from project root. Called by project workflow; referenced in README.md (line 192), COORDINATION.md (line 42), and used by `unreal/SkyBridge/remaster_materials.py` (line 625).

## Inputs
- Missing color maps: `area2/tex/*_n.png` without `*.png` counterpart.
- Game data: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`.
- BSA archives: `Data/*.bsa`.
- Alpha mask list: `area2/tex/alpha_masked_extra.txt`.

## Outputs
- Filled textures: `area2/tex/<key>.png`.
- Updated mask list: `area2/tex/alpha_masked_extra.txt`.

## Key functions
decode (DDS data→RGBA)
main (processes missing textures)

## Depends on
bsa.py, PIL, alpha_masked_extra.txt

## Gotchas
- Hardcoded Steam installation path (`D:\SteamLibrary\...`).
- Processes BSA archives in reverse order (last mod wins).
- Uses 5% alpha transparency threshold to mark masked textures.
- Updates `alpha_masked_extra.txt` on every run.
- Fails to locate textures in non-default Skyrim paths.

Source: read, not executed.
