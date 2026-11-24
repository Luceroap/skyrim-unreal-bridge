## Purpose
This script sets Unreal Engine console variables in the live editor by executing commands through the bridge. It adjusts in-editor settings like screen resolution and shadow quality without requiring manual input.

## How it is run
Command line: `python tools/set_cvar.py "r.ScreenPercentage 100" "sg.ShadowQuality 4"`.  
Other files that call it: `tools/shot_session.py` (line 48).

## Inputs
Console command strings passed as command-line arguments (e.g., `"r.ScreenPercentage 100"`), each representing a single Unreal Engine console command.

## Outputs
Modifies Unreal Engine's runtime console variables in-memory. No files or folders are modified; output is logged via `print()` statements.

## Key functions
`ue_exec(code, 30)` - Executes Python code in Unreal editor with 30s timeout  
`sys.argv[1:]` - Processes console command arguments  
`unreal.SystemLibrary.execute_console_command` - Sets engine variables  

## Depends on
`start_bridge.py` (imports `ue_exec`)

## Gotchas
- Requires running Unreal Engine editor to execute console commands
- Console commands must be passed as quoted arguments (e.g., `"r.ScreenPercentage 100"`)
- Command execution times out after 30 seconds
- Depends on `start_bridge` module being accessible in Python path
- Fails if Unreal bridge connection is inactive

Source: read, not executed.
