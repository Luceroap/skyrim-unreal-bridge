#pragma once
#include "CoreMinimal.h"
#include "Components/SkeletalMeshComponent.h"
#include "SkyNpcMeshComponent.generated.h"

/** Skeletal mesh component whose bone pose is written directly (component space) by USkyNpcRuntime. It has no anim instance and
 *  does not tick; the pose goes through the normal skinned-mesh double buffer, so the renderer gets previous-frame bone
 *  transforms (skinned velocity for TSR/motion blur), which a PoseableMeshComponent does not provide. */
UCLASS()
class USkyNpcMeshComponent : public USkeletalMeshComponent
{
	GENERATED_BODY()
public:
	USkyNpcMeshComponent(const FObjectInitializer& Init);
	/** Component-space transform for every bone of the mesh (Num must equal the reference skeleton bone count). */
	bool SetPoseComponentSpace(const TArray<FTransform>& ComponentSpace);
};
