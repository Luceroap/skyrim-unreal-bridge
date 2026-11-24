## Purpose
Provides C++ utility functions for managing Unreal Editor views, mesh rendering initialization, rain field actor spawning, and pose manipulation for the Skyrim-Unreal bridge. Bridges Skyrim data with Unreal Engine's graphics systems while ensuring editor stability.

## How it is run
Not executed via command line; integrated into Unreal Engine workflows. Called by Python scripts (e.g., `unreal/SkyBridge/npc_live.py`, `area2/npc_live_before_cursor_frozen.py`) using `hasattr(unreal.SkyBridgeViewLibrary, "apply_pose")` before invoking methods. Blueprint nodes can also directly call these functions.

## Inputs
- `SetRemasterView`: Boolean (`bOn`)
- `EnsureMeshRenderable`: `UStaticMesh*` object
- `SpawnRainField`: `UStaticMesh*`, `UMaterialInterface*`, `int32`, `float`, `float`, `FVector`
- `ApplyPose`: `UPoseableMeshComponent*`, `TArray<FName>`, `TArray<FTransform>`

## Outputs
- `SetRemasterView`: Boolean (`true` if success)
- `EnsureMeshRenderable`: Boolean (`true` if render data initialized)
- `SpawnRainField`: `AActor*` (rain field actor)
- `ApplyPose`: `int32` (number of bones set)

## Key functions
SetRemasterView - Toggles immersive editor viewport mode.
EnsureMeshRenderable - Initializes mesh render data to prevent editor crashes.
SpawnRainField - Creates camera-wrapping rain effect actor.
ApplyPose - Applies bone transforms and pushes pose to renderer.

## Depends on
`Kismet/BlueprintFunctionLibrary.h`, `Components/PoseableMeshComponent.h`, `SkyBridgeViewLibrary.generated.h`

## Gotchas
- Must call `EnsureMeshRenderable` before assigning a mesh to avoid editor crashes.
- `ApplyPose` is required to refresh mesh pose in editor; `SetBoneTransformByName` alone leaves mesh in reference pose.
- `SpawnRainField` requires actor position snapped to `BoxSize` for correct camera wrapping.

Source: read, not executed.
