## Purpose
Runs Python scripts inside the live editor via the live_bridge debug hook, enabling real-time testing of changes without restarting the editor. Outputs the script execution result or an error message if the hook is unavailable.

## How it is run
Command line: `python tools/ue_run.py script.py [timeout_s]`. Called by `cap.py` (via `subprocess.run`), `weatherfx_build.py`, `weatherfx_splash.py`, `weatherfx_test.py`, `water_flow_run.py`, and referenced in `AGENT_BRIEFING.md` and `tools/debug/README.md`.

## Inputs
- `script.py`: Absolute or relative path to Python script to execute (e.g., `tools/debug/npc_capture.py`).
- `[timeout_s]`: Optional integer (default `30` seconds) for execution timeout.

## Outputs
Prints script execution result or `no answer (is live_bridge running?)` if live_bridge is inactive. Never creates new files or modifies existing ones.

## Key functions
ue_exec - Executes script via live_bridge hook.

## Depends on
start_bridge.py (imports `ue_exec`).

## Gotchas
- Live editor must have `live_bridge` active for execution (otherwise outputs error).
- Timeout defaults to 30 seconds if omitted.
- Requires `tools/debug/README.md`-style script paths (e.g., `tools/debug/*.py`).
- Does not support multi-line script arguments or file handles.
- `area2/exec_request.py.lock` must not be locked (per `COORDINATION.md:186`).

Source: read, not executed.
