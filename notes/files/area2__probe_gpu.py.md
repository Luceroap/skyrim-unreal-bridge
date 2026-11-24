## Purpose
This script executes Unreal Engine's GPU profiling command and processes live bridge packet data to extract weather and time information for debugging. It logs relevant packet values to the console while leveraging Unreal's Python API for system interaction.

## How it is run
Executed via Unreal Engine's Python environment (e.g., Unreal Editor's Python console). No other project files call it, as confirmed by `git grep` output showing no references to `probe_gpu.py`.

## Inputs
- Live bridge packet data (`live.pkt`) structured per `live_bridge.PKT_FMT`.
- Unreal Engine's internal state (via `unreal.SystemLibrary`).

## Outputs
- Printed hour, weather (decoded from byte data), and time values to stdout.
- Execution of `ProfileGPU` console command (no explicit output).

## Key functions
- `execute_console_command`: Runs `ProfileGPU` in Unreal.
- `struct.unpack`: Parses `live.pkt` data using `PKT_FMT`.
- `print`: Outputs extracted packet values.
- `Exception handling`: Catches errors when processing `live.pkt`.
- `import unreal`: Accesses Unreal engine API.

## Depends on
- `live_bridge.py` (imports `PKT_FMT`, `PKT_SIZE`, and `live.pkt`).
- `unreal` (for `SystemLibrary.execute_console_command`).

## Gotchas
- Requires active live bridge connection; fails with exceptions if `live.pkt` is unavailable.
- Depends on exact structure of `live.pkt` defined in `live_bridge`.
- Prints exceptions to stdout, potentially cluttering logs.
- Runs exclusively within Unreal Engine's Python environment.
- `PKT_FMT` must match the bridge's data format.

Source: read, not executed.
