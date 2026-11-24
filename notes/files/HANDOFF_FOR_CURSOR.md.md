## Purpose
This file serves as the primary project overview for the SkyrimUnrealBridge project. It details the architecture, recent fixes, open issues, and run instructions to guide developers. It is explicitly required reading before README.md and COORDINATION.md.

## How it is run
This is a documentation file, not executable code. It is read by developers and referenced by other files (e.g., AGENTS.md, COORDINATION.md) but never run. No project scripts call it directly.

## Inputs
None (static documentation file with no runtime inputs).

## Outputs
None (static documentation file with no runtime outputs).

## Key functions
USkyBridgeViewLibrary::SetRemasterView
USkyBridgeViewLibrary::EnsureMeshRenderable
USkyBridgeViewLibrary::SpawnRainField
remaster_materials.configure
update_sky
live_bridge.py
build_environment
update_sky
remaster_watch.py
large_refs_preview.py

## Depends on
None (this is a documentation file, not code).

## Gotchas
- The C++ plugin build requires a stub .NET SDK registry key (HKCU\SOFTWARE\Microsoft\Microsoft SDKs\NETFXSDK\4.6.2).
- Large references (WRLD RNAM) are missing from streams until plugin visits `worldSpace->largeRefData.formIDCellMap`.
- Plugin DLL cannot be copied while Skyrim runs; `start_bridge.py` handles installation during Skyrim start.
- Remaster view causes black screen if activated while Skyrim is at main menu (renders midnight).
- Terrain LOD conversion requires sinking terrain 60 units and skipping detailed cells.

Source: read, not executed.
