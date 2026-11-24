# Instructions for ChatGPT / Codex: optimize the Skyrim -> Unreal bridge

Work ONLY in `C:\Users\Aidan\SkyrimUnrealBridge`. Write everything (replies, file names, folder names, code comments, commit messages, chat title) in plain English using only ASCII letters, digits, `_` and `-`. Never use Chinese or any other non-English characters in file names.

## The project
A running Skyrim SE (1.6.1170, SKSE 2.2.6, game at `D:\SteamLibrary\steamapps\common\Skyrim Special Edition`) streams its world to Unreal Engine 5.8, which draws it as a remaster: Skyrim is the "brain" (camera, time, weather, loaded objects, lights, actor skeleton poses), Unreal is the renderer. Read `README.md`, `COORDINATION.md` and `HANDOFF_FOR_CURSOR.md` first.

## What works
Live camera/time/weather/lights/world objects, terrain, mountains, trees, water (flows downhill), NPCs and creatures with their own heads/hair/armor posed from Skyrim's skeletons, one-click launcher (`Play.bat`, `python play.py`, stop with `python play.py --stop`), headless bulk importer (`python tools\offline_import.py`, Skyrim + editor closed).

## Your task: make it light enough to run
1. The Unreal editor's memory grows without limit (reached 50 GB; commit 88/91 GB; the PC froze). Find the cause by starting the editor and switching the add-on layers on one at a time (`area2\addons.txt`, `area2\debug_flags.txt` flags: nocam, noimport, noworld, nodistant, nonpc) and watching `UnrealEditor.exe` private memory every 30 s. Fix or cap the layer that grows. Memory in use after 20 minutes must stay under 20 GB.
2. Reduce CPU/GPU cost of the live editor without losing what is listed under "What works".
3. Report numbers before and after (memory GB, frames per second, import count per minute).

## Hard rules
- Do not install, download or run software from the internet. Do not create accounts or enter passwords. Do not change Windows security settings (Smart App Control etc.).
- Back up any game file before editing it (`C:\Users\Aidan\SkyrimBackups`). Do not minimize Skyrim (that crashed Community Shaders).
- Only ONE `UnrealEditor.exe` may run at a time. Check `tasklist | find "UnrealEditor"` first. Skyrim pauses when another window has focus.
- Git is local only (no remote, never push). Commit only the files you changed with a clear message; never `git add -A`, reset, checkout, stash or clean.
- Other agents may edit files in this folder: read `COORDINATION.md`, only edit files you own or ask under "Requests".
- Plugin DLL (`plugin\`, `shared\BridgeShared.h`) is built with `cmake --build build --config Release`; check the build succeeded before copying it to `Data\SKSE\Plugins`.
