#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Camera/CameraComponent.h"
#include "../../../../shared/BridgeShared.h"
#include "SkyrimCameraActor.generated.h"

/** Place one in a level. Reads the Skyrim shared-memory packet each tick and moves its camera to match. */
UCLASS()
class ASkyrimCameraActor : public AActor
{
	GENERATED_BODY()
public:
	ASkyrimCameraActor();
	virtual void BeginPlay() override;
	virtual void Tick(float Dt) override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;

	UPROPERTY(VisibleAnywhere) UCameraComponent* Camera;
	/** Skyrim unit -> cm (1 unit ~ 1.4287 cm). */
	UPROPERTY(EditAnywhere) float UnitsToCm = 1.4287f;
	/** Multiplier for lights recorded from the game (candela). Tune by eye against Skyrim. */
	UPROPERTY(EditAnywhere) float LightIntensityScale = 400.f;
	UPROPERTY(VisibleAnywhere) FString Status;
	UPROPERTY(VisibleAnywhere) float GameHour = 0;
	UPROPERTY(VisibleAnywhere) FString Weather;
	UPROPERTY(VisibleAnywhere) FString Cell;
	static FName RuntimeAssetName(const char* Model);
	static FRotator RuntimeRotation(const float* R);
	static FVector RuntimePosition(const float* P, float UnitsToCm);
private:
	UPROPERTY() class USkyNpcRuntime* Npcs = nullptr;
	UPROPERTY() class ADirectionalLight* Sun = nullptr;
	UPROPERTY() class ADirectionalLight* Moon = nullptr;
	UPROPERTY() class AExponentialHeightFog* Fog = nullptr;
	void UpdateSky(float Hour, const FString& WeatherId);
	void UpdateRuntimeWorld();
	bool ReadWorld(TArray<SkyBridge::WRef>& OutRefs, TArray<FString>& OutModels, TArray<SkyBridge::WLight>& OutLights);
	/** Places the exported Whiterun meshes in a ring around the player's first seen position (demo set dressing; not real Whiterun placement). */
	void SpawnDemoWorld(const FVector& PlayerPosCm);
	bool bWorldSpawned = false;
	void* MapHandle = nullptr;
	void* View = nullptr;
	void* WorldMapHandle = nullptr;
	void* WorldView = nullptr;
	TMap<uint32, class AStaticMeshActor*> RuntimeRefs;
	TArray<class APointLight*> RuntimeLights;
	TSet<FString> MissingRuntimeAssets;
	uint32 LastWorldTick = 0;
	bool bRuntimeWorldReady = false;
};
