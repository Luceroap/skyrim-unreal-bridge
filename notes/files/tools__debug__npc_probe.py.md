## Purpose
This script is a debugging tool for verifying the import of NPC skeletal meshes from FBX files into Unreal Engine. It tests the FBX import process, checks mesh properties like skeleton assignment, and enumerates poseable components.

## How it is run
Run directly as a Python script via Unreal Engine's Python console or command-line interpreter. No other project files call this script, as confirmed by the empty `git grep` result for `"npc_probe\.py"`.

## Inputs
Hardcoded FBX file path: `C:\Users\Aidan\SkyrimUnrealBridge\area2\npc\export\npc_000cdd72.fbx`.

## Outputs
Console output showing:
- Imported asset paths (e.g., `[...] /Game/Npc/npc_000cdd72`)
- Mesh type and class (`Mesh`, `SkeletalMesh`)
- Skeleton reference path
- First 12 material slot names
- List of poseable classes/methods related to skeletal meshes

## Key functions
- FbxImportUI setup
- AssetImportTask execution
- Mesh skeleton access
- Material slot enumeration
- Poseable class/method discovery
- Asset loading

## Depends on
`unreal` module (Unreal Engine Python API), specifically `FbxImportUI`, `AssetImportTask`, and `SkeletalMesh` properties.

## Gotchas
- Hard-coded FBX path (`npc_000cdd72.fbx`) must exist
- Requires Unreal Engine's Python API
- No error handling for missing FBX file
- Outputs debug data directly to console
- Not intended for production use

Source: read, not executed.
