## Purpose
Starts Skyrim via SKSE (auto-loads latest save), waits for live data stream, then launches Unreal Editor window. Bridges Skyrim and Unreal Engine 5 for real-time data transfer.

## How it is run
Command line: `C:\Users\Aidan\SkyrimUnrealBridge\start_bridge.ps1` (PowerShell). Called by README.md (line 79) and referenced in project documentation.

## Inputs
No command-line arguments. Hardcoded paths ($root = 'C:\Users\Aidan\SkyrimUnrealBridge', $game = 'D:\SteamLibrary\steamapps\common\Skyrim Special Edition').

## Outputs
- Launches SkyrimSE process and waits for data stream (via `tools/read_bridge.py`)
- Launches UnrealEditor.exe with specific parameters (`-windowed -ResX=1280 -ResY=720`)
- Displays progress messages: "Waiting for Skyrim to stream data...", "Bridge running."

## Key functions
Test-Stream - Checks for live data stream from Skyrim
Start-Process - Launches SkyrimSE and UnrealEditor
Get-Process - Verifies Skyrim process status
Write-Host - Displays status messages
Start-Sleep - Adds delays for process startup

## Depends on
- `tools/read_bridge.py` (called via `python -I -u "$root\tools\read_bridge.py"`)
- `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\skse64_loader.exe`
- `D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe`
- `unreal\SkyBridge\SkyBridge.uproject` (Unreal project file)

## Gotchas
- Requires disabling Smart App Control if Skyrim plugin is blocked
- PowerShell execution policy must permit script execution
- Fails with "No data from Skyrim" error if SKSE plugin blocked
- Hardcoded paths must match user's actual installation locations
- Requires 20-second delay after Skyrim launch to handle Bethesda launcher window

Source: read, not executed.
