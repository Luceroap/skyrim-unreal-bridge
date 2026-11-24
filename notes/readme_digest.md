# notes/readme_digest.md

QUICK START: Python command to start Skyrim + Unreal + overlay.
Skyrim SE -> Unreal Engine 5 bridge: SKSE plugin streams player data to Unreal.
Status (2026-10-27): Git, CMake, vcpkg, Epic Games Launcher, Unreal 5.8 installed; plugin builds and streams data; Unreal project compiles.
Version control: Local git repo only; .gitignore excludes generated data and Unreal binaries.
Run it: Start Skyrim via skse64_loader.exe, run read_bridge.py to print live values, launch Unreal.
Rebuild: Plugin uses CMake; Unreal module uses Build.bat.
Gotchas: Smart App Control blocks DLLs; .NET SDK registry key; uninstall plugin by deleting DLL.
Mesh pipeline (tools/): Steps to convert meshes from Skyrim to Unreal.
Known state at last test: Skyrim frame counter not advancing, firewall prompt for Unreal.
Full-area rebuild (current state): Tools read Skyrim.esm for references, build area, import meshes.
One-step start: `start_bridge.ps1` starts Skyrim via SKSE.
Overlay mode (compare Unreal against Skyrim): overlay.ps1 makes Unreal window borderless, click-through, transparent.
Latest additions: Area widened, terrain has vertex colors + ground texture, alpha-masked materials.
Alignment verification and live-dump workflow: Plugin dumps loaded references to TSV for comparison.
Extending coverage (automatic): Plugin records loaded references as you move, auto-rebuilds Unreal scene.
Live editor fixes (2026-10-27 evening): Fixed rotation order, debug hook, remaster view.
Crash fix (important): Plugin handles cell list iteration faults gracefully.
Photoreal lighting pass (2026-10-27 night): Unreal uses physically based setup with Lumen, volumetric clouds.
Performance: Input latency reduced from 113ms to 45ms, flicker fixed, upscaling textures.
Menus, HUD, weather: Menus show Skyrim's frames, weather follows Skyrim data.
Real mountains/trees: Mountains converted from Skyrim terrain LOD, rain rendered.
Complete cities: Cities fully converted from Skyrim data, including interiors.
Flicker fix: Duplicates skipped, night sky implemented.
Whiterun interiors: Interiors fully converted from Skyrim data.
DLSS: DLSS 4.5 plugin for UE 5.8, fixes for black planters/canals.
Terminal windows: remaster_watch.py runs hidden to prevent Skyrim from pausing.
Slow-motion: Fixed by adjusting Skyrim's game clock settings.
Smooth NPC movement: NPCs now move smoothly instead of jumping.
NPCs: Real poses, correct materials for hair/eyes/clothes.
Sharper picture: DLSS models optimized, close-range detail added.
Canal water: Canals have water now, activation prompt drawn.

Contradiction with HANDOFF_FOR_CURSOR.md:
README.md says: "One-step start: `start_bridge.ps1` starts Skyrim via SKSE (auto-loads your newest save), waits for live data, then opens Unreal."
HANDOFF_FOR_CURSOR.md says: "One-click launcher: `demo.py` (desktop shortcut 'Skyrim Unreal Demo', also `Launch_Demo.bat`)."
