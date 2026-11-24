## Purpose
Executes water flow application logic within the Unreal Engine editor's live_bridge environment. Rebuilds materials and applies flow data to the CellWater actor during real-time editing.

## How it is run
Command: `python tools/ue_run.py tools/water_flow_run.py`  
Called by `ue_run.py` (explicitly listed in the file's docstring) and referenced in `water_flow_apply.py`'s documentation.

## Inputs
- `water_flow.csv` (from `tools/water_flow.py`)
- Active live_bridge connection in Unreal editor

## Outputs
- Modified `CellWater` actor state in Unreal editor
- Output from `water_flow_apply.run()` (printed to console)

## Key functions
run() from water_flow_apply

## Depends on
- `tools/water_flow_apply.py` (imported and reloaded)
- `unreal/SkyBridge` directory (added to sys.path)

## Gotchas
- Editor must be running with live_bridge active
- `water_flow.csv` must exist in tools directory
- Requires exact path resolution via sys.path.insert
- Must be executed via `ue_run.py` (not standalone)
- Live_bridge must have CellWater actor active

Source: read, not executed.
