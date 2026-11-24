#include "SkyBridgeViewLibrary.h"

#include "Engine/StaticMesh.h"
#include "StaticMeshResources.h"
#include "RenderingThread.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Materials/MaterialInterface.h"

#include "Components/PoseableMeshComponent.h"
#include "Engine/SkinnedAsset.h"
#include "ReferenceSkeleton.h"

// UPoseableMeshComponent::BoneSpaceTransforms is private; explicit instantiation may name private members.
namespace
{
	struct FBoneSpaceTag
	{
		using Type = TArray<FTransform> UPoseableMeshComponent::*;
		friend Type Get(FBoneSpaceTag);
	};
	template <typename Tag, typename Tag::Type Member>
	struct TRobMember
	{
		friend typename Tag::Type Get(Tag) { return Member; }
	};
	template struct TRobMember<FBoneSpaceTag, &UPoseableMeshComponent::BoneSpaceTransforms>;
}

#if WITH_EDITOR
#include "Editor.h"
#include "Framework/Application/SlateApplication.h"
#include "LevelEditor.h"
#include "Modules/ModuleManager.h"
#include "SLevelViewport.h"
#include "Widgets/SWindow.h"
#endif

bool USkyBridgeViewLibrary::SetRemasterView(bool bOn)
{
#if WITH_EDITOR
	if (!FSlateApplication::IsInitialized() || !FModuleManager::Get().IsModuleLoaded("LevelEditor"))
	{
		return false;
	}
	FLevelEditorModule& LevelEditor = FModuleManager::GetModuleChecked<FLevelEditorModule>("LevelEditor");
	TSharedPtr<SLevelViewport> Viewport = LevelEditor.GetFirstActiveLevelViewport();
	if (!Viewport.IsValid())
	{
		return false;
	}
	if (TSharedPtr<SWindow> Window = FSlateApplication::Get().FindWidgetWindow(Viewport.ToSharedRef()))
	{
		Window->SetWindowMode(bOn ? EWindowMode::WindowedFullscreen : EWindowMode::Windowed);
	}
	if (Viewport->IsImmersive() != bOn)
	{
		Viewport->MakeImmersive(bOn, false);
	}
	if (Viewport->IsViewportToolbarVisible() == bOn)
	{
		Viewport->ToggleViewportToolbarVisibility();
	}
	return true;
#else
	return false;
#endif
}

bool USkyBridgeViewLibrary::EnsureMeshRenderable(UStaticMesh* Mesh)
{
	if (!Mesh)
	{
		return false;
	}
#if WITH_EDITOR
	Mesh->WaitForPendingInitOrStreaming();
#endif
	FStaticMeshRenderData* RenderData = Mesh->GetRenderData();
	if (!RenderData || RenderData->LODResources.Num() == 0 || RenderData->LODResources[0].GetNumVertices() == 0)
	{
		return false;
	}
	if (!RenderData->IsInitialized())
	{
		Mesh->InitResources();
		FlushRenderingCommands();
	}
	return RenderData->IsInitialized();
}

AActor* USkyBridgeViewLibrary::SpawnRainField(UStaticMesh* Mesh, UMaterialInterface* Material, int32 Count, float BoxSize, float BoxHeight, FVector InstanceScale)
{
#if WITH_EDITOR
	UWorld* World = GEditor ? GEditor->GetEditorWorldContext().World() : nullptr;
	if (!World || !Mesh || !EnsureMeshRenderable(Mesh))
	{
		return nullptr;
	}
	AActor* Actor = World->SpawnActor<AActor>(AActor::StaticClass(), FTransform::Identity);
	if (!Actor)
	{
		return nullptr;
	}
	UInstancedStaticMeshComponent* Ism = NewObject<UInstancedStaticMeshComponent>(Actor, TEXT("RainStreaks"));
	Ism->SetMobility(EComponentMobility::Movable);
	Actor->SetRootComponent(Ism);
	Actor->AddInstanceComponent(Ism);
	Ism->SetStaticMesh(Mesh);
	Ism->SetMaterial(0, Material);
	Ism->SetCastShadow(false);
	Ism->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Ism->SetBoundsScale(2.0f);
	Ism->RegisterComponent();
	FRandomStream Rng(0x5EED);
	TArray<FTransform> Instances;
	Instances.Reserve(Count);
	for (int32 i = 0; i < Count; ++i)
	{
		const FVector P(Rng.FRandRange(-0.5f, 0.5f) * BoxSize, Rng.FRandRange(-0.5f, 0.5f) * BoxSize, Rng.FRandRange(-0.5f, 0.5f) * BoxHeight);
		Instances.Add(FTransform(FRotator::ZeroRotator, P, InstanceScale * Rng.FRandRange(0.7f, 1.3f)));
	}
	Ism->AddInstances(Instances, false);
	Actor->SetActorLabel(TEXT("SkyBridgeRain"));
	return Actor;
#else
	return nullptr;
#endif
}

int32 USkyBridgeViewLibrary::ApplyPose(UPoseableMeshComponent* Component, const TArray<FName>& Bones, const TArray<FTransform>& ComponentSpace)
{
	if (!Component || !Component->GetSkinnedAsset() || Bones.Num() != ComponentSpace.Num())
	{
		return 0;
	}
	const FReferenceSkeleton& Ref = Component->GetSkinnedAsset()->GetRefSkeleton();
	TArray<FTransform>& Local = Component->*Get(FBoneSpaceTag());
	const int32 Num = Ref.GetNum();
	if (Local.Num() != Num || Num == 0)
	{
		return 0;
	}
	TArray<int32> Given;
	Given.Init(INDEX_NONE, Num);
	for (int32 k = 0; k < Bones.Num(); ++k)
	{
		const int32 Index = Ref.FindBoneIndex(Bones[k]);
		if (Index != INDEX_NONE)
		{
			Given[Index] = k;
		}
	}
	TArray<FTransform> Space;
	Space.SetNum(Num);
	int32 Set = 0;
	for (int32 i = 0; i < Num; ++i)            // the reference skeleton lists parents before children
	{
		const int32 Parent = Ref.GetParentIndex(i);
		if (Given[i] != INDEX_NONE)
		{
			Space[i] = ComponentSpace[Given[i]];
			Space[i].NormalizeRotation();
			Local[i] = Parent >= 0 ? Space[i].GetRelativeTransform(Space[Parent]) : Space[i];
			++Set;
		}
		else
		{
			Space[i] = Parent >= 0 ? Local[i] * Space[Parent] : Local[i];
		}
	}
	Component->RefreshBoneTransforms();
	return Set;
}
