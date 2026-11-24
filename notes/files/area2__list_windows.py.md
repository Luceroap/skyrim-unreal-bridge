## Purpose
This script enumerates visible top-level Windows (including minimized windows via the taskbar) and outputs process names, process IDs, minimization status, and window titles using Windows API functions. It provides a real-time system window overview.

## How it is run
Executed directly via Python (e.g., `python area2/list_windows.py`). `git grep` shows no other project files call this script.

## Inputs
System window state via Windows API (no command-line arguments or external files).

## Outputs
Console output formatted as:  
`<process_name (28 chars)> <PID (6 digits)> <min? (3 chars)> <window_title (max 90 chars)>`,  
sorted by process name.

## Key functions
cb (window enumeration callback)  
EnumWindows (start window scan)  
GetWindowText (retrieve window title)  
GetWindowThreadProcessId (get process ID)  
QueryFullProcessImageNameW (get process executable name)

## Depends on
No project files (only standard library imports: `ctypes`, `ctypes.wintypes`, `subprocess`).

## Gotchas
- Redundant condition `u.IsWindowVisible(h) and not u.IsIconic(h) or u.IsWindowVisible(h)` simplifies to checking visibility alone.
- Unused `subprocess` module imported but never referenced.
- Window titles truncated to 90 characters (`b.value[:90]`).
- Process names may be empty if `QueryFullProcessImageNameW` fails.
- Minimized windows correctly marked as "min" despite redundant visibility check.

Source: read, not executed.
