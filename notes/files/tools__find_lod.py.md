## Purpose
This script locates Skyrim Special Edition's terrain LOD meshes (.btr) and texture files by scanning BSA archives and loose files in the game's Data directory. It identifies terrain mesh levels, texture counts, and object files to support asset analysis.

## How it is run
Execute via `python tools/find_lod.py` from project root. No other files call it (confirmed via `git grep -n "find_lod\.py"` only shows itself).

## Inputs
- Hardcoded `DATA` path: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`
- BSA files in `DATA` (e.g., `Skyrim.esm`, `Skyrim - Textures.esm`)

## Outputs
- Per-BSA counts: `btr level X`, `terrain tex`, `bto` counters (e.g., `Skyrim.esm` with counts)
- First 5 loose `.btr` files in `DATA\meshes\terrain\tamriel\`
- Sample `objects` directory content from `DATA\meshes\terrain\tamriel\objects\`

## Key functions
Bsa file parsing  
Terrain LOD type counting  
Loose file sample inspection  

## Depends on
tools/bsa.py (Bsa class import)

## Gotchas
- Hardcoded Steam install path must match user's actual path
- Fails if Skyrim Data directory structure differs (e.g., `meshes\terrain\tamriel`)
- Only lists first 5 loose `.btr` files (truncation)
- Requires all BSA files to be accessible and uncorrupted
- Windows backslashes (`\`) used in paths; may cause issues on non-Windows systems

Source: read, not executed.
