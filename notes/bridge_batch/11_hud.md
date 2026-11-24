# HUD and menu focus transitions

Local-model review lead; NOT independently verified or applied.

## Finding
Game stops receiving input when Skyrim is not the active window and Unreal Editor is not visible

## Evidence
- remaster_watch.py:284 - visible = bool(in_world and user32.GetForegroundWindow() == sky)

## Suggested fix
Change condition to check if Skyrim is active or if Unreal Editor is active

## Validation needed
Check if Skyrim is active window or if Unreal Editor is active window when determining visibility
