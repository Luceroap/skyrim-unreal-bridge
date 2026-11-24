#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "SkyBridgeGameMode.generated.h"

/** Spawns the Skyrim-mirroring camera and a debug reference grid so camera motion is visible in an empty map. */
UCLASS()
class ASkyBridgeGameMode : public AGameModeBase
{
	GENERATED_BODY()
public:
	ASkyBridgeGameMode();
	virtual void BeginPlay() override;
};
