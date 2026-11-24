# External Commands Catalog

| File:Line | Executable | Main Arguments | Purpose |
|-----------|------------|----------------|---------|
| area2/cap.py:10 | python | ue_run.py, npc_capture.py, 60 | Run NPC capture script for 60 seconds |
| demo.py:11 | powershell | -NoProfile -Command | Execute PowerShell commands |
| demo.py:24 | python | -I, asset_service.py | Start asset service background process |
| demo.py:28 | python | -I, tamriel_terrain.py, --serve | Start terrain server mode |
| demo.py:32 | python | start_bridge.py, --no-overlay, --skyrim-only | Start bridge without overlay for Skyrim |
| demo.py:48 | python | -I, asset_service.py | Start asset service in background |
| demo.py:60 | python | start_bridge.py, --remaster | Start bridge in remaster mode |
| play.py:23 | tasklist | /FI "IMAGENAME eq " + exe | Check if process is running |
| play.py:28 | taskkill | /F, /IM [process] | Force-kill process |
| play.py:32 | powershell | -NoProfile -Command | Execute PowerShell commands |
| play.py:36 | taskkill | /F, /PID [pid] | Kill process by PID |
| play.py:41 | powershell | -NoProfile -Command | Execute PowerShell commands |
| play.py:46 | python | -I, npc_autobuild.py | Run NPC autobuild background process |
| play.py:79 | tasklist | /FI "IMAGENAME eq SkyrimSE.exe", /FO CSV, /NH | Get Skyrim process info as CSV |
| play.py:112 | tasklist | /FI "IMAGENAME eq UnrealEditor.exe", /NH | Check UnrealEditor process |
| play.py:118 | python | start_bridge.py, --no-overlay, --skyrim-only | Start bridge without overlay |
| play.py:124 | UnrealEditor.exe | SkyBridge.uproject, -windowed, -ResX=1600, -ResY=900 | Run Unreal Editor for SkyBridge project |
| play.py:135 | powershell | -NoProfile -Command | Execute PowerShell commands |
| play.py:138 | python | -I, npc_autobuild.py | Run NPC autobuild in background |
| play.py:149 | python | start_bridge.py, --remaster | Start bridge in remaster mode |
| start_bridge.py:17 | tasklist | /FI "IMAGENAME eq " + exe | Check if process is running |
| start_bridge.py:231 | powershell | -NoProfile -Command | Execute PowerShell commands |
| start_bridge.py:240 | taskkill | /F, /PID [pid] | Kill process by PID |
| start_bridge.py:242 | pyw | remaster_watch.py | Run remaster watch background process |
| start_bridge.py:249 | taskkill | /F, /PID [pid] | Kill process by PID |
| start_bridge.py:269 | python | -I, -c "import ctypes..." | Test DLL loading |
| start_bridge.py:460 | skse64_loader.exe | (none) | Launch SKSE loader |
| start_bridge.py:464 | taskkill | /F, /IM SkyrimSELauncher.exe | Kill Bethesda launcher |
| start_bridge.py:480 | UnrealEditor.exe | SkyBridge.uproject, -game, -windowed, -ResX=1280, -ResY=720 | Run Unreal in game mode |
| tools/asset_service.py:45 | python | -W ignore, -I, build_area.py, DATA, area_json, AREA | Build area assets |
| tools/asset_service.py:46 | python | -W ignore, -I, textures.py, DATA, AREA | Process textures |
| tools/asset_service.py:47 | python | -W ignore, -I, textures_pbr.py, DATA, AREA | Process PBR textures |
| tools/asset_service.py:48 | blender.exe | -b, -P, blender_export.py, --, obj, export | Export assets via Blender |
| tools/auto_build.py:18 | (variable) | cmd | Generic build automation |
| tools/auto_build.py:25 | tasklist | /FI "IMAGENAME eq " + exe | Check if process is running |
| tools/auto_build.py:58 | taskkill | /F, /IM UnrealEditor.exe | Kill UnrealEditor process |
| tools/auto_build.py:72 | UnrealEditor.exe | UPROJECT, -game, -windowed, -ResX=1280, -ResY=720 | Launch Unreal Editor for build |
| tools/editor_watchdog.py:226 | (variable) | cmd | Launch background processes |
| tools/editor_watchdog.py:228 | (variable) | cmd | Launch background processes |
| tools/editor_watchdog.py:241 | python | start_bridge.py, --remaster | Start bridge in remaster mode |
| tools/editor_watchdog.py:255 | powershell | -NoProfile -Command | Execute PowerShell commands |
| tools/editor_watchdog.py:276 | powershell | -NoProfile -Command | Execute PowerShell commands |
| tools/editor_watchdog.py:285 | taskkill | /F, /PID [pid] | Kill process by PID |
| tools/grass_placement.py:520 | blender.exe | -b, -P, grass_blender.py, -- | Process grass placement via Blender |
| tools/grass_placement.py:563 | blender.exe | -b, -P, grass_blender.py, -- | Process grass placement via Blender |
| tools/land_terrain.py:464 | blender.exe | -b, -P, blender_export.py, --, --blender | Process terrain via Blender |
| tools/land_terrain.py:465 | blender.exe | -b, -P, blender_export.py, --, --blender | Process terrain via Blender |
| tools/land_terrain.py:468 | blender.exe | -b, --blender-obj | Export terrain objects via Blender |
| tools/land_textures.py:581 | blender.exe | -b, -P, script, -- | Process textures via Blender |
| tools/lod_horizon_preview.py:136 | blender.exe | -b, -P, blender_export.py, -- | Generate LOD horizon preview |
| tools/lod_objects.py:418 | blender.exe | -b, -P, blender_export.py, -- | Process LOD objects via Blender |
| tools/lod_objects.py:419 | blender.exe | -b, -P, blender_export.py, -- | Process LOD objects via Blender |
| tools/npc_autobuild.py:10 | tasklist | /FI "IMAGENAME eq SkyrimSE.exe" | Check Skyrim process |
| tools/npc_autobuild.py:15 | python | -I, npc_batch.py, 3, --autobuild | Run NPC batch build with 3 threads |
| tools/npc_batch.py:75 | python | -I, npc_build_creature.py, base, skel, g | Build NPC creature |
| tools/npc_batch.py:80 | python | -I, npc_build.py, base, sex, --face=%08x, --slots=%x, g | Build NPC |
| tools/npc_build.py:21 | python | -W ignore, -I, ... | Run NPC build scripts |
| tools/npc_build.py:103 | blender.exe | -b, -P, npc_blender.py, --, skin, sex, fbx, face_json | Process NPC skin with Blender |
| tools/npc_build_creature.py:21 | python | -W ignore, -I, ... | Run NPC creature build |
| tools/npc_build_creature.py:92 | blender.exe | -b, -P, npc_blender.py, --, skin, key, fbx, --creature | Process NPC creature skin with Blender |
| tools/offline_import.py:40 | cmd.exe | PROJ, -run=pythonscript, -script=SCRIPT, -unattended, -nullrhi, -nosplash | Run Unreal Engine for offline import |
| tools/offline_import.py:41 | cmd.exe | PROJ, -run=pythonscript, ... | Run Unreal Engine for offline import |
| tools/perf_gpu_share.py:12 | tasklist | /fo csv, /nh | Get process list for performance monitoring |
| tools/perf_gpu_share.py:28 | powershell | -NoProfile -Command | Execute PowerShell commands |
| tools/run_local_queue.py:39 | git | (command line args) | Execute Git operations |
| tools/run_local_queue.py:76 | (shell) | spec[4:] | Execute shell commands |
| tools/shutdown_after_import.py:18 | powershell | -NoProfile -Command | Execute PowerShell commands |
| tools/shutdown_after_import.py:43 | taskkill | /F, /IM [exe] | Kill process |
| tools/shutdown_after_import.py:51 | shutdown | /s, /t 120, /c "Skyrim/Unreal asset import finished: shutting down. Cancel with: shutdown /a" | Shut down system after import |
| tools/skyrim_lightweight.py:28 | tasklist | /FI "IMAGENAME eq SkyrimSE.exe" | Check Skyrim process |
| tools/skyrim_plugins.py:16 | tasklist | /FI "IMAGENAME eq SkyrimSE.exe" | Check Skyrim process |
| tools/tamriel_terrain.py:276 | blender.exe | -b, -P, blender_export.py, -- | Process terrain via Blender
