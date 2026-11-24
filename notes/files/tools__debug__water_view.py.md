## Purpose
Visualizes river flow in Unreal Engine by drawing debug arrows based on quads and flow data from CSV files. Targets a specific river cell (5,-4) south of Whiterun market in Skyrim's coordinate system.

## How it is run
Command line: Execute directly via Python (e.g., `python tools/debug/water_view.py`). No other project files call it (git grep found no references).

## Inputs
- `area2/water_quads.csv` (quad coordinates, count, height)
- `area2/water_flow.csv` (flow direction, speed)

## Outputs
- Debug arrows drawn in Unreal viewport (`draw_debug_arrow`)
- Camera position/rotation set via `set_level_viewport_camera_info`
- Printed output: `arrows` count, camera vector, rotation

## Key functions
- `draw_debug_arrow`
- `get_editor_world`
- `find_look_at_rotation`
- `set_level_viewport_camera_info`

## Depends on
- `area2/water_quads.csv`
- `area2/water_flow.csv`
- Unreal Engine API (`unreal`, `os`, `math`)

## Gotchas
- Hardcoded user path `C:\Users\Aidan\SkyrimUnrealBridge`
- Skips flow segments with `sp == 0`
- Uses invalid conditional `n % 1` (always false)
- Fixed camera offset `3200 * U, -2600 * U`
- Filters quads beyond 2600-unit radius from target

Source: read, not executed.
