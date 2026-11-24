## Purpose
Provides view-related utilities for the Skyrim-to-Unreal bridge, managing editor viewport states, ensuring mesh renderability, spawning instanced mesh effects, and applying bone poses to poseable meshes. Handles editor-specific operations and mesh initialization.

## How it is run
Called from Python scripts (e.g., referenced in `HANDOFF_FOR_CURSOR.md` as `USkyBridgeViewLibrary::SetRemasterView`), not via direct command line. Other files: `HANDOFF_FOR_CURSOR.md` (Python integration).

## Inputs
- `UStaticMesh*` (mesh handle)
- `UMaterialInterface*` (material)
- `int32 Count`, `float BoxSize`, `float BoxHeight` (spawn parameters)
- `TArray<FName> Bones`, `TArray<FTransform> ComponentSpace` (pose data)
- `bool bOn` (viewport toggle)

## Outputs
- `bool` (success/failure)
- `AActor*` (spawned rain field actor)
- Modified mesh component data (bone transforms, render state)

## Key functions
SetRemasterView - Toggles editor viewport between immersive and windowed modes.  
EnsureMeshRenderable - Verifies static mesh initialization for rendering.  
SpawnRainField - Creates randomized instanced mesh actors for rain effects.  
ApplyPose - Applies bone transforms to poseable mesh using reference skeleton order.

## Depends on
- `Engine/StaticMesh.h`, `Components/PoseableMeshComponent.h` (Unreal Engine headers)  
- `Editor/LevelEditor.h` (editor module)  
- Private member `UPoseableMeshComponent::BoneSpaceTransforms` (accessed via namespace hack)

## Gotchas
- Editor-only functionality (`WITH_EDITOR` guards)  
- Uses namespace hack to access private `BoneSpaceTransforms` member  
- Fixed seed `0x5EED` in `SpawnRainField` randomness (not truly random)  
- Calls `FlushRenderingCommands()` in `EnsureMeshRenderable`  
- Pose application assumes reference skeleton order (parents before children)  
Source: read, not executed.
