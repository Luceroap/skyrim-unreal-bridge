## Purpose
Background watchdog that relaunches the Unreal editor (remaster view) after it crashes while Skyrim is being played. It ensures relaunches only occur when Skyrim is in the world, the editor crashed (not cleanly exited), and relaunch limits aren't exceeded.

## How it is run
Command line: `pythonw tools/editor_watchdog.py` (main loop), `--start` (detached), `--stop`, `--once [--act]`, or `--test`. Called via command line from `COORDINATION.md` documentation; no code files directly call it (grep shows only `COORDINATION.md` references).

## Inputs
- `area2/no_watchdog.txt` (pause signal)
- `area2/editor_watchdog_state.json` (relaunch history)
- `play.PROJ/Saved/Crashes` (crash reports)
- `play.LOGS` (editor log files)

## Outputs
- `area2/editor_watchdog.log` (all actions)
- `area2/editor_watchdog_state.json` (updated relaunch count)
- Launches Unreal editor via `play.UE` and `start_bridge.py --remaster`

## Key functions
log: Log messages to file and console.
processes: Enumerate processes by name.
skyrim_in_world: Check Skyrim world state via shared memory.
classify: Classify editor log as crash/clean/killed.
decide: Determine relaunch need based on state.
relaunch: Execute editor relaunch and bridge start.
load_state: Read watchdog state.
save_state: Write watchdog state.
loop: Main monitoring loop.

## Depends on
- `play.py` (project module for paths/constants)
- `area2` directory structure (all state/log files)

## Gotchas
- Pauses when `area2/no_watchdog.txt` exists.
- Only relaunches on crashes (ignores clean exits).
- Limits to 3 relaunches in 30 minutes.
- Requires 6+ GB RAM free.
- Mutex prevents multiple instances.

Source: read, not executed.
