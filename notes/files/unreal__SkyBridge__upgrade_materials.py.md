## Purpose
Rebuilds Skyrim-derived materials into PBR (Physically Based Rendering) format by importing normal and RMAOS (roughness/metallic/AO) maps, enabling Nanite geometry on meshes, and fixing material assignments on static meshes. Automatically processes all textures in the Area2 content folder.

## How it is run
Executed via command line:  
`<UE_CMD> <UPROJECT> -run=pythonscript -script="C:/Users/Aidan/SkyrimUnrealBridge/unreal/SkyBridge/upgrade_materials.py"`  
Triggered by `tools/auto_build.py` (line 63) during the automatic build process.

## Inputs
- Source texture path: `C:\Users\Aidan\SkyrimUnrealBridge\area2\tex\`
- Configuration files: `alpha_masked.txt` (masked materials), `foliage_textures.txt` (foliage materials)
- Existing Unreal assets: `M_<texture>` material templates, texture files with `_n` (normal) and `_rmaos` suffixes

## Outputs
- PBR materials in `/Game/Area2Tex/` (replacing `M_<texture>` with normal/RMAOS maps)
- Nanite enabled on `Area2` static meshes (modified `.uasset` files)
- Material slots reassigned on static meshes via `material_slot_name` matching
- Logs: `PBR materials rebuilt: [n] with normal maps, [n] with rmaos`, `NANITE enabled on [n] meshes`, `REASSIGNED [n] material slots`

## Key functions
task - Asset import task creator  
import_companion_maps - Processes _n.png and _rmaos.png textures  
rebuild_materials - Converts to PBR with normal/RMAOS mapping  
enable_nanite - Activates Nanite on static meshes  
reassign_materials - Fixes slot assignments via filename matching

## Depends on
- `tools/auto_build.py` (caller)
- Unreal Engine Python API (`unreal`, `AssetToolsHelpers`)
- `area2/tex/alpha_masked.txt`
- `area2/tex/foliage_textures.txt`
- Existing Unreal assets at `/Game/Area2Tex/`

## Gotchas
- Skips `_n` and `_rmaos` textures during material rebuild
- Foliage shading fails silently with warning if expression setup fails
- Requires `alpha_masked.txt` and `foliage_textures.txt` to exist (else uses empty sets)
- Reassigns materials only for slots matching `_*_dds` suffixes
- Uses absolute paths (C:\Users\...) which may break on non-Windows systems

Source: read, not executed.
