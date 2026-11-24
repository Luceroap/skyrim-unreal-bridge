## Purpose
Collapses Skyrim NPC textures with shared filenames (e.g., Jenassa.dds in multiple folders) into unique PNGs. Generates `area2/npc/tex_alias.json` for texture slot aliasing in NPC rendering.

## How it is run
Command: `python tools/npc_tex_alias.py`.  
Called by user via documentation in COORDINATION.md (lines 87, 89) and referenced by `area2/npc_live_before_cursor_frozen.py` (line 204) and `unreal/SkyBridge/npc_live.py` (line 204).

## Inputs
- Skyrim Special Edition game data path: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`
- Texture paths from `.mtl` files in `area2/npc/obj/`
- `.dds` textures from game archives (`.bsa`) or loose files

## Outputs
- PNGs in `area2/npc/tex/` named `<parent_folder>_<stem>.png` (e.g., `hair_jenassa.png`)
- JSON file: `area2/npc/tex_alias.json` mapping slot names to unique stems

## Key functions
norm - Normalize texture paths to "textures\" prefix  
read - Fetch texture from BSA files or loose files  
convert - Convert DDS to PNG (adjusts DX10 headers)  
unique_stem - Generate unique filename from path components  
alias - Build slot alias mapping  

## Depends on
bsa.py, PIL.Image, and standard libraries (glob, json, os, re)

## Gotchas
- Skips textures without filename clashes (only processes `clash` set)  
- Converts DX10 textures (format 72–78) to DX9 (71–77)  
- Prints "MISSING" for failed texture conversions  
- Incremental execution (~20s) as noted in COORDINATION.md  
- JSON keys use lowercase slot names (e.g., `slot.lower()`)

Source: read, not executed.
