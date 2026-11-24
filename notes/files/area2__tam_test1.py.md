## Purpose
This script tests the integration of Skyrim mesh data into Unreal Engine by importing FBX assets and verifying material assignments, mesh properties, and bounding volumes. It serves as a diagnostic tool for the Skyrim-to-Unreal bridge project.

## How it is run
Command line: `python area2/tam_test1.py`. No other files call it, as confirmed by the `git grep` command (no matching callers found).

## Inputs
- FBX file: `area2/export/tlo_0_-1.fbx` (path derived from `tamriel_live.AREA`)
- Unreal Engine asset path: `/Game/Tamriel/tlo_0_-1`

## Outputs
- Console logs of material details (`far_material` output), import timing, mesh properties (static materials, bounds, nanite settings)
- Unreal Engine asset imported at `/Game/Tamriel/tlo_0_-1` (visible in Editor)

## Key functions
far_material
import_fbx
load_asset
get_bounds
far_instance

## Depends on
tamriel_live module
unreal module

## Gotchas
- Unreal Editor must be running for `unreal.load_asset` to succeed.

Source: read, not executed.
