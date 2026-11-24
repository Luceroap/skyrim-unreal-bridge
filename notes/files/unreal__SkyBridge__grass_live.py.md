## Purpose
Manages dynamic grass rendering in Unreal Engine based on Skyrim's GRAS scatter data from LAND texture layers. It renders grass tiles within a radius of the camera, distinguishing between near grass (casts shadows) and far grass (no shadows), using preprocessed data from `area2/grass`.

## How it is run
The `update()` function is called every frame by the Live instance's update loop. It is referenced as a dependency in `tools/grass_world.py` and included in `tools/make_local_queue.py` as part of the grass module.

## Inputs
- `live`: A Live instance containing packet data (e.g., `pkt`, `mesh`, camera location).
- `cam_loc`: Optional camera position in Unreal Engine coordinates (defaults to active viewport camera).

## Outputs
- Grass actors with `InstancedStaticMeshComponent` (near/far) spawned in Unreal Engine.
- Updates internal state (`live._grass`) tracking active tiles, missing models, and build budgets.
- Debugging statistics via `stats(live)` (near/far instances, models built, tiles).

## Key functions
update: Main frame loop handling grass rendering within camera radius.
clear: Removes all grass actors and resets state.
stats: Returns instance statistics (near/far, models, tiles).
_actor: Creates grass actors per model with shadow/no-shadow components.
_wanted: Calculates tiles within camera radius and shadow distance.
_dataset: Handles worldspace transitions (e.g., city areas).

## Depends on
- `tools/grass_world.py` (caller).
- `area2/grass/index.json` and `cell_*` data files (gras scatter metadata).
- `remaster_materials` (for material adjustments in `_foliage`).

## Gotchas
- 5600 Skyrim units (≈80 m) radius for active grass tiles.
- Only 6 rebuilds per frame (`REBUILDS_PER_CALL = 6`).
- Worldspace data refreshed every 0.5 seconds (`t_ws` timeout).
- Missing models queued for 3 seconds before rebuilding (`t_missing` timeout).
- Near grass casts shadows; far grass does not.

Source: read, not executed.
