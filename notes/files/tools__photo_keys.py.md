## Purpose
Handles Skyrim photo hotkeys (F8/F9 for 4K/8K screenshots, F5/F6 for time/weather adjustments) via a game engine bridge. Runs in the background, capturing high-res images and modifying in-game sky settings through the SkyrimUnrealBridge plugin.

## How it is run
Command line: `python tools\photo_keys.py` (invoked by `Photo_Shoot.bat`). Called from `make_local_queue.py` as a dependency.

## Inputs
Keyboard hotkeys (F5: time +1.5h, F6: next weather, F7: reset sky, F8: 4K photo, F9: 8K photo), current game state (hour/weather) read from `SkyrimUnrealBridge.sky`.

## Outputs
Photos saved to `screenshots/photos/` (e.g., `photo_143022_3840x2160.png`), updated game clock in `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\SKSE\Plugins\SkyrimUnrealBridge.sky`.

## Key functions
apply_sky
photo
key_event_loop

## Depends on
start_bridge.py (for `ue_exec`)
ctypes
os
sys
time

## Gotchas
Requires Skyrim to be the active window
Hardcoded SKY file path: D:\SteamLibrary\...\SkyrimUnrealBridge.sky
Sky settings (time/weather) written directly to SKY file
Beep omitted if winsound module unavailable
F7 resets sky override via Unreal engine (not simple toggle)

Source: read, not executed.
