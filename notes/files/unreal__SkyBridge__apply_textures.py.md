## Purpose
Automates the application of vanilla diffuse textures to Whiterun meshes in Unreal Engine by importing PNG textures, creating materials, and assigning materials based on mesh slot naming conventions. Processes textures from Skyrim's BSA to Unreal Engine materials without normal/specular maps.

## How it is run
Directly executed as a script; called by `tools/textures.py` (per README.md). Command line: `python unreal/SkyBridge/apply_textures.py`.

## Inputs
- PNG textures in `C:\Users\Aidan\SkyrimUnrealBridge\whiterun\tex`
- Mesh assets in `unreal/SkyBridge/Content/WhiterunMeshes` with names starting with `wr` (e.g., `wrslate01.uasset`)

## Outputs
- Materials created at `/Game/WhiterunTex/M_*` (e.g., `M_wrslate01`)
- Updated mesh assets in `/Game/WhiterunMeshes/` with materials assigned
- Log entries for textured meshes (e.g., `TEXTURED wrslate01: 3/4 slots`)

## Key functions
Import texture PNGs
Create per-texture materials
Assign materials by slot matching
Save updated materials
Update mesh material assignments

## Depends on
`tools/textures.py` (calls this script)
Unreal Engine Python API (`unreal`, `AssetTools`, `MaterialEditingLibrary`)

## Gotchas
- Hardcoded Windows path `C:\Users\Aidan\SkyrimUnrealBridge\...` breaks on other systems
- Meshes must start with `wr` (e.g., `wrslate01.uasset`) to process
- Texture filenames (without extension) must match slot patterns (e.g., `wrslate01`)
- Alpha/transparency is ignored during texture application
- Requires vanilla diffuse textures from BSA DDS → PNG conversion

Source: read, not executed.
