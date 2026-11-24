## Purpose
The script logs the bounding box data (origin and extent) for specific mesh assets in the Unreal Engine project, aiding in level design and spatial debugging for the Whiterun area.

## How it is run
Executed directly as a standalone Python script in the Unreal editor. No other files call it (confirmed by empty `git grep` results for "probe_bounds.py").

## Inputs
Hardcoded mesh names: `["wrhousebanneredmare01", "wrhouse02", "wrbridge01", "wrguardhouse01", "wrbreezehome01"]` located at `/Game/WhiterunMeshes/`.

## Outputs
Logs to Unreal Engine's console via `unreal.log` with formatted strings like `PROBE wrhousebanneredmare01 origin=(x,y,z) ext=(x,y,z)`.

## Key functions
load_asset  
get_bounds  
log

## Depends on
unreal module (Unreal Engine Python API)

## Gotchas
- Mesh names hardcoded in the script; renaming assets in UE requires manual script edits.  
- No error handling for missing assets; crashes silently if a mesh is missing.  
- Log output is unstructured text; no file export or programmatic access to bounds data.

Source: read, not executed.
