## Purpose
Automates close-up rendering of NPCs in Unreal Editor without modifying the user's camera. Captures high-resolution images by positioning virtual cameras relative to NPC models using data from `npc_step.txt`.

## How it is run
Command line: `ue_run.py npc_capture.py 60` (as called by `area2/cap.py`). Other files calling it: `area2/cap.py`.

## Inputs
- `area2/npc_step.txt` with one of these commands:
  - `setup [names] [distance]` (e.g., `setup NPC1,NPC2 200`)
  - `grab <prefix>` (e.g., `grab face`)
  - `done`

## Outputs
- PNG files in `area2/` named `<prefix>_<index>.png` (e.g., `face_0.png`).
- Modifies shared memory variable `live._npc_caps` (stored in `npc_live.py`).

## Key functions
setup
grab
done
create_render_target2d
export_render_target

## Depends on
npc_live.py (via `sys.modules["npc_live"]`)
area2/cap.py (caller)
Unreal Engine API

## Gotchas
- Requires NPC models to have hardcoded socket names "NPC-Head-_Head_" and "NPC-Spine2-_Spn2_".
- Only processes NPCs with >100 bones (via `get_num_bones()`).
- Defaults to 170.0 distance if `step[2]` is omitted.
- Requires Unreal Editor to be running (uses editor-level functions).
- Relies on `npc_live` module’s `_state` being populated.

Source: read, not executed.
