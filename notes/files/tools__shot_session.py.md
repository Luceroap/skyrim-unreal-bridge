## Purpose
Starts a clean photo session for the SkyrimUnrealBridge project by freeing system memory and launching Skyrim with the Unreal view. Prevents memory exhaustion by checking free commit memory (RAM + pagefile) and terminates resource-heavy processes before initialization.

## How it is run
Command line: `python tools/shot_session.py [--max]`  
Called by:  
- `Photo_Shoot.bat` (line 6: `python tools\shot_session.py --max`)  
- Documented in `AGENT_BRIEFING.md` (lines 9 and 32)

## Inputs
- Optional `--max` flag (triggers showcase quality mode)  
- System memory state (free commit memory via `free_commit_gb()`)  

## Outputs
- Terminates: `run_local_queue` processes, `llama-server.exe`, and `codex.exe` (if window title ≠ "nothing")  
- Launches: `play.py` (root directory) to start Skyrim/Unreal view  
- If `--max` provided:  
  - Runs `max_quality.py` and `set_cvar.py r.ScreenPercentage 100`  
  - Prints status messages (e.g., "free commit memory: 35 GB", "showcase quality is on")  

## Key functions
`free_commit_gb()`: Calculates free commit memory (RAM + pagefile)  
`say(s)`: Prints timestamped console messages  
`kill_cmd(pattern)`: Terminates processes matching pattern  

## Depends on
- `play.py` (root directory)  
- `max_quality.py` (tools directory)  
- `set_cvar.py` (tools directory)  
- `Data/SKSE/Plugins/SkyrimUnrealBridge.sky` (for night mode input via user edit)  

## Gotchas
- Requires ≥30 GB free commit memory (RAM + pagefile) to proceed  
- Windows-only (uses `taskkill`, PowerShell, and Win32 API)  
- Waits 15 seconds after launching `play.py` before applying `--max` settings  
- Terminates `codex.exe` only if window title ≠ "nothing"  
- Night mode requires manual edit to `Data/SKSE/Plugins/SkyrimUnrealBridge.sky` (write "hour 22")  

Source: read, not executed.
