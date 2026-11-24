## Purpose
Audits material slots in Unreal Engine static meshes within the Area2 directory, flagging slots not using designated texture materials located in `/Game/Area2Tex/M_`. Ensures consistent material assignments across meshes.

## How it is run
Executed via Unreal Engine's Python console (e.g., `python audit_slots.py` in editor). No other project files reference it (confirmed via `git grep` with empty results).

## Inputs
- `.uasset` files in `C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Content\Area2\`.

## Outputs
Console logs via `unreal.log` showing:
- Total slots checked and unassigned/white slots count (e.g., `AUDIT total slots 100, unassigned/white 15`).
- Top 40 material slots by usage (e.g., `AUDIT slot=UV0 used by 23 meshes e.g. mesh0`).

## Key functions
`scan_mesh_materials`
`validate_material_path`
`log_top_slot_usage`
`skip_terrain_mesh`
`flag_incorrect_materials`

## Depends on
`unreal` (Engine API), `glob`, `os`, `collections` (standard libraries). No other project files.

## Gotchas
- Hardcoded Windows path `C:\Users\Aidan\...` breaks on non-Windows systems.
- Skips "terrain" mesh by exact filename (`n == "terrain"`), not by mesh type.
- Only audits meshes in `Area2` directory (Content/Area2).

Source: read, not executed.
