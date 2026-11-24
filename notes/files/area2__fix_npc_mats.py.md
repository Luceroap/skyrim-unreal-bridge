## Purpose
This script updates materials for NPC skeletal meshes in Unreal Engine by replacing them with remastered versions from the `remaster_materials` module. It processes only meshes with names starting with "npc_", ensuring compatibility with the project's naming conventions.

## How it is run
Executed as a standalone Python script within Unreal Engine's editor environment. No other files call it (confirmed via `git grep` showing no references to `fix_npc_mats.py` in project files).

## Inputs
- Skeletal meshes from `/Game/Npc` directory with names starting with "npc_"
- `remaster_materials` module (reloaded at runtime)
- `npc_live` module (`nl`) for material mappings

## Outputs
- Modified skeletal meshes saved directly in Unreal Editor (no new files)
- Prints `meshes refreshed: X` (count of processed meshes)
- Prints `hair MIs: Y` (count of `MI_hair_` assets in `/Game/Area2Tex`)

## Key functions
list_assets
load_asset
get_editor_property
set_editor_property
save_loaded_asset
_material_for_slot

## Depends on
swap_npc.py (executed first via `exec`)
remaster_materials
npc_live

## Gotchas
- Requires NPC mesh names to explicitly start with "npc_" prefix (e.g., "npc_dwarf")
- Modifies assets in-place without backups or versioning
- Hardcoded path in `swap_npc.py` execution (C:\Users\Aidan\...)
- Relies on `nl._material_for_slot` returning valid materials (no fallback)
- Uses `name[4:]` key extraction which assumes consistent "npc_" prefix length

Source: read, not executed.
