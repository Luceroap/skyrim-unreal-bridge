#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "SkyNpcRuntime.generated.h"

class USkyNpcMeshComponent;
class USkeletalMesh;
class UStaticMesh;

/** Standalone-runtime NPC layer: reads Local\SkyrimUnrealBridge_actors_v1 / _gear_v1 and drives one skeletal mesh actor per streamed
 *  actor (/Game/Npc/npc_<8 hex base id>). C++ port of unreal/SkyBridge/npc_live.py (pose math in its module docstring). */
UCLASS()
class USkyNpcRuntime : public UObject
{
	GENERATED_BODY()
public:
	/** Call every frame. CamSky = camera position in Skyrim units. */
	void Update(UWorld* World, const float* CamSky);
	void Shutdown();
	int32 NumActors() const;
	FString Describe() const;

	int32 MaxNpcs = 24;
	int32 CreatureSlots = 6;
	float RadiusUnits = 5200.f;

	UPROPERTY() TMap<FName, TObjectPtr<USkeletalMesh>> Meshes;
	UPROPERTY() TMap<FName, TObjectPtr<UStaticMesh>> WeaponMeshes;
	struct FImpl;
	TSharedPtr<FImpl> Impl;
};
