## Purpose
Resets a rain visual effect in the Unreal Engine editor by clearing a material parameter and removing the associated actor. This script ensures the rain impact does not persist after the effect is cleared.

## How it is run
Run as a Python script in the Unreal Editor. No other project files reference this script (git grep returned no matching calls).

## Inputs
Current editor world state, optional `live.rain_occ` actor (if present in the `live` module).

## Outputs
- Modifies `MPC_RainOcc` material parameter `Occ` to black (`0,0,0,0`).
- Destroys `rain_occ` actor (if `live.rain_occ` exists).
- Prints labels of remaining `SceneCapture2D` actors.

## Key functions
- `get_editor_world`: Retrieves current editor world instance.
- `load_asset`: Loads the `MPC_RainOcc` material.
- `set_vector_parameter_value`: Sets material parameter to black.
- `destroy_actor`: Removes the `rain_occ` actor.
- `get_all_level_actors`: Collects all level actors for filtering.

## Depends on
- Unreal Engine Python API (`unreal`, `EditorLevelLibrary`).
- `live` module (must define `rain_occ` attribute).
- `MPC_RainOcc` material path (`/Game/Area2Tex/MPC_RainOcc`).

## Gotchas
- `live.rain_occ` must exist to destroy the actor; otherwise, no effect.
- Material parameter change applies unconditionally.
- Prints list of `SceneCapture2D` actors regardless of rain effect status.
- Requires Unreal Editor context to execute.
- Material path must match exact asset location.

Source: read, not executed.
