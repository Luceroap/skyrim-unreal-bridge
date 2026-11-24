#include "SkyBridgeGameMode.h"
#include "SkyrimCameraActor.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"

ASkyBridgeGameMode::ASkyBridgeGameMode()
{
	DefaultPawnClass = nullptr;
}

void ASkyBridgeGameMode::BeginPlay()
{
	Super::BeginPlay();
	UWorld* W = GetWorld();
	W->SpawnActor<ASkyrimCameraActor>(FVector::ZeroVector, FRotator::ZeroRotator);

	// Reference grid around the Skyrim origin (cm). Off by default now that real terrain exists; set to true for debugging.
	const bool bDrawDebugGrid = false;
	if (!bDrawDebugGrid) return;
	const float Ext = 50000.f, Step = 500.f;
	for (float v = -Ext; v <= Ext; v += Step)
	{
		const FColor C = FMath::IsNearlyZero(v) ? FColor::Red : FColor(80, 80, 80);
		DrawDebugLine(W, FVector(v, -Ext, 0), FVector(v, Ext, 0), C, true, -1.f, 0, 4.f);
		DrawDebugLine(W, FVector(-Ext, v, 0), FVector(Ext, v, 0), FMath::IsNearlyZero(v) ? FColor::Blue : C, true, -1.f, 0, 4.f);
	}
	for (int i = -5; i <= 5; ++i)
	{
		DrawDebugLine(W, FVector(i * 5000, 20000, 0), FVector(i * 5000, 20000, 3000), FColor::Green, true, -1.f, 0, 20.f);
		DrawDebugLine(W, FVector(20000, i * 5000, 0), FVector(20000, i * 5000, 3000), FColor::Yellow, true, -1.f, 0, 20.f);
	}
}
