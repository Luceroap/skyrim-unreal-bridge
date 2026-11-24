## Purpose
This script verifies that the new folded pose math in `npc_live.py` produces identical results to the original per-bone matrix math stored in `_pose_old.txt`. It compares bone transformations and rotation angles to ensure correctness and performance improvements.

## How it is run
Command: `python area2/test_npc_math.py`. It is executed directly from the command line as referenced in `COORDINATION.md` (lines 65, 120) and `README.md` (line 308), but not called by other files in the project.

## Inputs
- `npc_live.py` (read into execution namespace)
- `_pose_old.txt` (bone data for comparison)
- Predefined bone names (e.g., `"NPC Pelvis [Pelv]"`)
- Fixed random seed (`random.seed(3)`)

## Outputs
Console output showing:
- Worst position/rotation differences between new/old methods
- Worst angle difference for binding checks (degrees)
- Performance comparison: "per bone: old X us, new Y us"

## Key functions
`rq` - Generates normalized random quaternion vectors.  
`entry` - Initializes pose state with rest bone data.

## Depends on
- `npc_live.py` (executed as stub via `exec`)
- `_pose_old.txt` (data file)
- Standard modules (`math`, `random`, `sys`, `types`)
- Functions from `npc_live.py` (e.g., `quat_to_mat`, `_apply_pose`)

## Gotchas
- Uses fixed random seed `3`, ensuring reproducible but non-random comparisons.
- Hardcoded Windows path (`C:\Users\Aidan\...`) will fail on non-Windows systems.
- Requires `_pose_old.txt` to exist in `area2/` directory.
- Performance check shows new method is ~12x faster (from `COORDINATION.md`).
- Mocks Unreal module (`sys.modules["unreal"]`) which may require adjustments if `SkyBridgeViewLibrary` changes.

Source: read, not executed.
