#include "SkyNpcMeshComponent.h"

USkyNpcMeshComponent::USkyNpcMeshComponent(const FObjectInitializer& Init) : Super(Init)
{
	PrimaryComponentTick.bCanEverTick = false;
	PrimaryComponentTick.bStartWithTickEnabled = false;
	bEnableUpdateRateOptimizations = false;
	bPerBoneMotionBlur = true;
	SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

bool USkyNpcMeshComponent::SetPoseComponentSpace(const TArray<FTransform>& ComponentSpace)
{
	TArray<FTransform>& Dst = GetEditableComponentSpaceTransforms();
	if (Dst.Num() == 0 || Dst.Num() != ComponentSpace.Num()) return false;
	FMemory::Memcpy(Dst.GetData(), ComponentSpace.GetData(), sizeof(FTransform) * Dst.Num());
	bNeedToFlipSpaceBaseBuffers = true;
	FinalizeBoneTransform();          // flips the double buffer: previous pose stays available for velocity
	UpdateChildTransforms();
	UpdateBounds();
	MarkRenderTransformDirty();
	MarkRenderDynamicDataDirty();
	return true;
}
