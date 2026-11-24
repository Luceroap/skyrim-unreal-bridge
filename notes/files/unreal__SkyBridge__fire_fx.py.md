## Purpose
This module creates a procedural flame material and places animated flame actors at lit lights (torches, braziers, candles) within a specific intensity range. The flame animation is driven by a custom HLSL shader that produces a wobbling, multi-colored effect (white-hot core to orange to red).

## How it is run
Not executed from command line; called internally by `tools/showcase_shot.py` during live view updates. `place()` is the main entry point, called with a `live` object containing current light actors. The module runs within Unreal Engine's editor environment (not in-game).

## Inputs
- `live`: Object containing `light_actors` list, where each actor has a `light_component` with `intensity` (candela). Only lights with `20.0 <= intensity <= 400.0` are processed.

## Outputs
- Material asset at `/Game/FireFX/M_Flame` (additive, unlit, two-sided).
- Static mesh actors (flame planes) at each qualifying light location, stored in folder `SkyBridge/Fire`.
- Each flame uses two crossed planes (90° apart), scaled by light intensity, with no shadows/collision.

## Key functions
- `build`: Creates/rebuilds the flame material at `/Game/FireFX/M_Flame`.
- `clear`: Removes all flame actors from the `SkyBridge/Fire` folder.
- `place`: Spawns flames at lights within intensity bounds (20-400 candela).

## Depends on
- `tools/showcase_shot.py` (caller).
- Unreal Engine assets: `/Engine/BasicShapes/Plane`.
- Standard modules: `math`, `unreal`.

## Gotchas
- Flames float ~30 cm too high (per AGENT_BRIEFING.md).
- Only processes lights between 20.0 and 400.0 candela (MIN_I/MAX_I).
- Height calculation uses `math.sqrt(i / 65.0)` which affects flame scaling.
- Material is additive (may cause over-brightening).
- Uses two plane actors per flame (may increase draw calls).

Source: read, not executed.
