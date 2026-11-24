## Purpose
This script uses the Unreal Editor's viewport camera to perform line traces for ground detection, identifying objects, actors, and mesh materials in the scene.

## How it is run
Executed within Unreal Editor's Python environment. `git grep "probe_ground.py"` found no other project files calling it, indicating it is run manually or via direct editor invocation.

## Inputs
Current editor viewport camera position (`loc`) and rotation (`rot`), retrieved via `unreal.EditorLevelLibrary.get_level_viewport_camera_info()`.

## Outputs
Console output lines containing:
- Forward/side trace offsets (`fwd`, `side`)
- Actor name (`act.get_actor_label()`)
- Actor folder path (`act.get_folder_path()`)
- Static mesh name (`sm`)
- Up to six material names (`mats[:6]`)

## Key functions
`line_trace_single`
`get_forward_vector`
`get_right_vector`
`get_actor_label`
`get_folder_path`
`get_num_materials`
`get_material`
`static_mesh.get_name`

## Depends on
None (relies solely on Unreal Engine modules, no other project files imported).

## Gotchas
- Requires Unreal Editor to be running.
- Materials printed limited to first six entries.
- Line traces vertically span 3500 units (500 up to 3000 down).
- Hardcoded probe offsets (300,150; 500,300; 200,0; 800,-300).
- Uses `TRACE_TYPE_QUERY1` which must be enabled in editor settings.

Source: read, not executed.
