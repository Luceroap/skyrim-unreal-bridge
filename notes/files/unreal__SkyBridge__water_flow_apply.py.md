## Purpose
This script rebuilds the M_SkyWater material to enable per-instance flow-based ripple panning and applies flow vectors from `water_flow.csv` to CellWater actors. It converts Skyrim's coordinate system to Unreal Engine's axes for accurate water flow simulation.

## How it is run
Command line: `python tools/ue_run.py unreal/SkyBridge/water_flow_apply.py`  
Called by:
- `tools/water_flow_run.py` (via `git grep` output)
- `live_bridge.spawn_cell_water` (via COORDINATION.md's note about added try-block)

## Inputs
- `water_flow.csv` (from `C:\Users\Aidan\SkyrimUnrealBridge\area2`, with columns `fx,fy,speed`)
- CellWater actor instances (named "CellWater" in editor)
- Existing `M_SkyWater` material asset (`/Game/Area2Tex/M_SkyWater`)

## Outputs
- Rebuilt and saved `M_SkyWater` material with per-instance flow support
- Updates CellWater actor's per-instance custom data (flow vectors 0=x, 1=y)
- Returns status strings like "flow applied to 42 strips" or error messages

## Key functions
rebuild_water_material - Reconstructs M_SkyWater material with flow-based ripple panning  
apply_flow - Writes flow data from CSV to CellWater actor custom data  
run - Main entry point that combines material rebuild and flow application

## Depends on
- `os`, `unreal` (Python modules)
- `M_SkyWater` material asset at fixed path
- `water_flow.csv` in `area2/` directory
- CellWater actor with label "CellWater" in editor

## Gotchas
- `water_flow.csv` must have exactly the same number of rows as CellWater instances (else returns error)
- Skyrim Y-axis flows to Unreal X-axis, Skyrim X-axis flows to Unreal Y-axis (swapped)
- Requires CellWater actor named "CellWater" (fails if actor label differs)
- Material path `/Game/Area2Tex/M_SkyWater` is hard-coded (must match asset name)
- Missing `water_flow.csv` causes runtime failure (no error handling in script)

Source: read, not executed.
