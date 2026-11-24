## Purpose
This script audits asset mapping and rendering discrepancies between Skyrim and Unreal Engine in the Whiterun area. It identifies missing meshes, untextured components, material instances without base colors, and other asset alignment issues.

## How it is run
Run directly via `python area2/probe.py` from the project root directory. No other files call it (git grep shows no references).

## Inputs
- `world_whiterunworld.json` (from `area2/`)
- `live` data structure (contains `actors`, `preview`, `city`, `distant_built`, etc.)
- Unreal Engine asset library (`/Game/Area2/` meshes)

## Outputs
- `area2/audit.txt` (written with audit details)
- Console output showing audit results (e.g., missing mesh counts)

## Key functions
- `game_ref_audit`: Processes game references not drawn
- `stream_queue_audit`: Analyzes stream queue contents
- `untextured_materials_check`: Identifies untextured mesh components
- `mis_without_basecolor`: Checks material instances lacking BaseColor
- `distant_model_audit`: Tracks distant models to build

## Depends on
- `live` (project module providing runtime data)
- `unreal.EditorAssetLibrary` (Unreal API for asset checks)
- `unreal.MaterialEditingLibrary` (Unreal API for material checks)

## Gotchas
- Hard-coded path `C:\Users\Aidan\SkyrimUnrealBridge` may break if project is moved
- Overwrites `audit.txt` on every execution
- Requires `live` data structure to be pre-populated
- Depends on Unreal Engine API availability (no fallback)
- Uses Unreal asset paths like `/Game/Area2/` which may change

Source: read, not executed.
