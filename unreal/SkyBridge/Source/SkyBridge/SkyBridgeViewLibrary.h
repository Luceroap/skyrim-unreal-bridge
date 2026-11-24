#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "Components/PoseableMeshComponent.h"
#include "SkyBridgeViewLibrary.generated.h"

UCLASS()
class USkyBridgeViewLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	// Editor window fullscreen on its current monitor + immersive level viewport without toolbar, or back to normal.
	UFUNCTION(BlueprintCallable, Category = "SkyBridge")
	static bool SetRemasterView(bool bOn);

	// True if the mesh has initialized render data (initializing it if needed); assigning one without crashes the editor.
	UFUNCTION(BlueprintCallable, Category = "SkyBridge")
	static bool EnsureMeshRenderable(UStaticMesh* Mesh);

	// Actor with Count instances of Mesh scattered in a BoxSize x BoxSize x BoxHeight box (rain streaks). The material wraps
	// them around the camera and animates the fall; keep the actor at the camera position snapped to BoxSize.
	UFUNCTION(BlueprintCallable, Category = "SkyBridge")
	static AActor* SpawnRainField(UStaticMesh* Mesh, UMaterialInterface* Material, int32 Count, float BoxSize, float BoxHeight, FVector InstanceScale);

	// Sets the component-space transforms of the named bones in one pass (bones not listed keep their pose relative to
	// their parent) and pushes the pose to the renderer. A PoseableMeshComponent only refreshes its rendered pose from its
	// own tick, which never runs in the editor world, so SetBoneTransformByName alone leaves the mesh in its reference pose.
	// Returns the number of bones set.
	UFUNCTION(BlueprintCallable, Category = "SkyBridge")
	static int32 ApplyPose(UPoseableMeshComponent* Component, const TArray<FName>& Bones, const TArray<FTransform>& ComponentSpace);
};
