## Purpose
The SkyBridge module serves as the entry point for the Skyrim-to-Unreal bridge plugin, initializing the module during Unreal Engine startup to enable integration between Skyrim and Unreal.

## How it is run
Automatically loaded by Unreal Engine at startup (no command-line arguments). Confirmed via `git grep` with no references to `SkyBridge.cpp` in other files.

## Inputs
Module class `FDefaultGameModuleImpl`, module name `SkyBridge`, display name `"SkyBridge"` (directly passed to `IMPLEMENT_PRIMARY_GAME_MODULE`).

## Outputs
No files, folders, or shared memory written; module solely registers plugin integration with the engine.

## Key functions
IMPLEMENT_PRIMARY_GAME_MODULE

## Depends on
Modules/ModuleManager.h

## Gotchas
- The module name must exactly match `SkyBridge` as declared in `IMPLEMENT_PRIMARY_GAME_MODULE`.
- No user logic implemented beyond module declaration.
- Not referenced by any other source files (confirmed by `git grep`).
- Automatically loaded during engine startup without user configuration.
- No input/output handling implemented.

Source: read, not executed.
