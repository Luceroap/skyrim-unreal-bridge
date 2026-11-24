#include "SkyrimCameraActor.h"
#include "SkyNpcRuntime.h"
#include "Engine/Engine.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PointLight.h"
#include "Engine/World.h"
#include "Components/PointLightComponent.h"
#include "Engine/PostProcessVolume.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "GameFramework/PlayerController.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Windows/AllowWindowsPlatformTypes.h"
#include <windows.h>
#include "Windows/HideWindowsPlatformTypes.h"
#include "../../../../shared/BridgeShared.h"

ASkyrimCameraActor::ASkyrimCameraActor()
{
	PrimaryActorTick.bCanEverTick = true;
	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	RootComponent = Camera;
}

FName ASkyrimCameraActor::RuntimeAssetName(const char* Model)
{
	FString Name = UTF8_TO_TCHAR(Model ? Model : "");
	if (Name.EndsWith(TEXT(".nif"), ESearchCase::IgnoreCase)) Name.LeftChopInline(4, EAllowShrinking::No);
	Name.ReplaceInline(TEXT("/"), TEXT("_"));
	Name.ReplaceInline(TEXT("\\"), TEXT("_"));
	Name.ReplaceInline(TEXT(" "), TEXT("_"));
	return FName(*Name);
}

FVector ASkyrimCameraActor::RuntimePosition(const float* P, float Units)
{
	return FVector(P[1], P[0], P[2]) * Units;
}

FRotator ASkyrimCameraActor::RuntimeRotation(const float* R)
{
	// Same Skyrim -> Unreal basis conversion as the editor bridge: A = C * R * diag(1,-1,1).
	double RF[9];
	for (int32 Row = 0; Row < 3; ++Row)
	{
		for (int32 Col = 0; Col < 3; ++Col)
		{
			RF[Row * 3 + Col] = R[Row * 3 + Col] * (Col == 1 ? -1.0 : 1.0);
		}
	}
	auto At = [&](int32 Row, int32 Col) -> double { return RF[(Row == 0 ? 1 : Row == 1 ? 0 : 2) * 3 + Col]; };
	const FVector X(At(0, 0), At(1, 0), At(2, 0));
	const FVector Y(At(0, 1), At(1, 1), At(2, 1));
	const FVector Z(At(0, 2), At(1, 2), At(2, 2));
	return FMatrix(X, Y, Z, FVector::ZeroVector).Rotator();
}

bool ASkyrimCameraActor::ReadWorld(TArray<SkyBridge::WRef>& OutRefs, TArray<FString>& OutModels, TArray<SkyBridge::WLight>& OutLights)
{
	if (!WorldView)
	{
		WorldMapHandle = OpenFileMappingW(FILE_MAP_READ, false, SkyBridge::kWorldName);
		if (WorldMapHandle) WorldView = MapViewOfFile((HANDLE)WorldMapHandle, FILE_MAP_READ, 0, 0, 0);
		if (!WorldView) return false;
	}
	const auto* Header = reinterpret_cast<const volatile SkyBridge::WorldHeader*>(WorldView);
	SkyBridge::WorldHeader H{};
	TArray<SkyBridge::WRef> Refs;
	TArray<FString> Models;
	TArray<SkyBridge::WLight> Lights;
	for (int32 Try = 0; Try < 4; ++Try)
	{
		const uint32 S0 = Header->seq;
		if (S0 & 1u) continue;
		FMemory::Memcpy(&H, (const void*)WorldView, sizeof(H));
		if (H.magic != SkyBridge::kWorldMagic || H.seq != S0 || H.nRefs > SkyBridge::kMaxRefs ||
			H.nModels > SkyBridge::kMaxModels || H.nLights > SkyBridge::kMaxLights) return false;
		Models.SetNum(H.nModels);
		for (uint32 i = 0; i < H.nModels; ++i)
		{
			const char* Src = reinterpret_cast<const char*>(WorldView) + SkyBridge::kWorldModelsOff + size_t(i) * SkyBridge::kModelLen;
			Models[i] = UTF8_TO_TCHAR(Src);
		}
		Refs.SetNumUninitialized(H.nRefs);
		FMemory::Memcpy(Refs.GetData(), reinterpret_cast<const uint8*>(WorldView) + SkyBridge::kWorldRefsOff, size_t(H.nRefs) * sizeof(SkyBridge::WRef));
		Lights.SetNumUninitialized(H.nLights);
		FMemory::Memcpy(Lights.GetData(), reinterpret_cast<const uint8*>(WorldView) + SkyBridge::kWorldLightsOff, size_t(H.nLights) * sizeof(SkyBridge::WLight));
		if (S0 == Header->seq)
		{
			if (H.tick == LastWorldTick) return false;
			LastWorldTick = H.tick;
			OutRefs = MoveTemp(Refs); OutModels = MoveTemp(Models); OutLights = MoveTemp(Lights);
			return true;
		}
	}
	return false;
}

void ASkyrimCameraActor::UpdateRuntimeWorld()
{
	TArray<SkyBridge::WRef> Refs;
	TArray<FString> Models;
	TArray<SkyBridge::WLight> Lights;
	if (!ReadWorld(Refs, Models, Lights)) return;
	TSet<uint32> Seen;
	int32 SpawnBudget = 24;
	for (const SkyBridge::WRef& Ref : Refs)
	{
		Seen.Add(Ref.id);
		const FVector Pos = RuntimePosition(Ref.pos, UnitsToCm);
		const FRotator Rot = RuntimeRotation(Ref.rot);
		if (AStaticMeshActor** Existing = RuntimeRefs.Find(Ref.id))
		{
			if (*Existing)
			{
				(*Existing)->SetActorLocationAndRotation(Pos, Rot, false, nullptr, ETeleportType::TeleportPhysics);
				(*Existing)->SetActorScale3D(FVector(Ref.scale));
			}
			continue;
		}
		if (SpawnBudget <= 0 || Ref.model >= uint32(Models.Num())) continue;
		FTCHARToUTF8 ModelUtf8(*Models[Ref.model]);
		const FString Asset = RuntimeAssetName(ModelUtf8.Get()).ToString();
		if (MissingRuntimeAssets.Contains(Asset)) continue;   // failed once already: do not retry LoadObject every tick
		const FString Path = FString::Printf(TEXT("/Game/Area2/%s.%s"), *Asset, *Asset);
		UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
		if (!Mesh)
		{
			MissingRuntimeAssets.Add(Asset);
			continue;
		}
		if (AStaticMeshActor* Actor = GetWorld()->SpawnActor<AStaticMeshActor>(Pos, Rot))
		{
			Actor->SetMobility(EComponentMobility::Movable);
			Actor->GetStaticMeshComponent()->SetStaticMesh(Mesh);
			Actor->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			Actor->SetActorScale3D(FVector(Ref.scale));
			RuntimeRefs.Add(Ref.id, Actor);
			--SpawnBudget;
		}
	}
	for (auto It = RuntimeRefs.CreateIterator(); It; ++It)
	{
		if (!Seen.Contains(It.Key()))
		{
			if (It.Value()) It.Value()->Destroy();
			It.RemoveCurrent();
		}
	}
	while (RuntimeLights.Num() > Lights.Num())
	{
		if (RuntimeLights.Last()) RuntimeLights.Last()->Destroy();
		RuntimeLights.Pop();
	}
	for (int32 i = 0; i < Lights.Num(); ++i)
	{
		APointLight* Light = RuntimeLights.IsValidIndex(i) ? RuntimeLights[i] : nullptr;
		if (!Light) Light = GetWorld()->SpawnActor<APointLight>(RuntimePosition(Lights[i].pos, UnitsToCm), FRotator::ZeroRotator);
		if (!Light) continue;
		if (!RuntimeLights.IsValidIndex(i)) RuntimeLights.Add(Light);
		Light->SetActorLocation(RuntimePosition(Lights[i].pos, UnitsToCm));
		Light->PointLightComponent->SetLightColor(FLinearColor(Lights[i].col[0], Lights[i].col[1], Lights[i].col[2]));
		Light->PointLightComponent->SetAttenuationRadius(FMath::Max(10.f, Lights[i].radius * UnitsToCm));
		Light->PointLightComponent->SetIntensity(60.f * FMath::Max(0.f, Lights[i].dimmer) * (0.5f + Lights[i].radius / 600.f));
		Light->PointLightComponent->SetCastShadows(i < 8);
	}
	bRuntimeWorldReady = true;
	Status = FString::Printf(TEXT("live frame %u, %d refs, %d lights"), LastWorldTick, RuntimeRefs.Num(), RuntimeLights.Num());
}

void ASkyrimCameraActor::BeginPlay()
{
	Super::BeginPlay();
	if (APlayerController* PC = GetWorld()->GetFirstPlayerController())
	{
		PC->SetViewTarget(this);
	}
}

void ASkyrimCameraActor::EndPlay(const EEndPlayReason::Type Reason)
{
	if (Npcs) Npcs->Shutdown();
	if (View) UnmapViewOfFile(View);
	if (MapHandle) CloseHandle((HANDLE)MapHandle);
	if (WorldView) UnmapViewOfFile(WorldView);
	if (WorldMapHandle) CloseHandle((HANDLE)WorldMapHandle);
	View = MapHandle = WorldView = WorldMapHandle = nullptr;
	Super::EndPlay(Reason);
}

void ASkyrimCameraActor::SpawnDemoWorld(const FVector& Foot)
{
	UWorld* W = GetWorld();
	// The editor bridge creates these layers before it streams props.  The packaged
	// runtime has no Python bootstrap, so create the same landscape layers here or
	// streamed objects appear to float in the sky.
	auto SpawnLandscape = [W](const TCHAR* AssetName, const TCHAR* MaterialPath, bool bShadow) -> AStaticMeshActor*
	{
		const FString Path = FString::Printf(TEXT("/Game/Area2/%s.%s"), AssetName, AssetName);
		UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
		if (!Mesh) return nullptr;
		AStaticMeshActor* Actor = W->SpawnActor<AStaticMeshActor>(FVector::ZeroVector, FRotator(0.f, 90.f, 0.f));
		if (!Actor) return nullptr;
		Actor->SetMobility(EComponentMobility::Static);
		Actor->GetStaticMeshComponent()->SetStaticMesh(Mesh);
		Actor->GetStaticMeshComponent()->SetCastShadow(bShadow);
		if (MaterialPath && MaterialPath[0] != TEXT('\0'))
		{
			if (UMaterialInterface* Material = LoadObject<UMaterialInterface>(nullptr, MaterialPath))
				Actor->GetStaticMeshComponent()->SetMaterial(0, Material);
		}
		return Actor;
	};
	SpawnLandscape(TEXT("terrain"), TEXT("/Game/Area2/M_Terrain2.M_Terrain2"), true);
	SpawnLandscape(TEXT("lodterrain"), nullptr, true);
	SpawnLandscape(TEXT("lodwater"), TEXT("/Game/Area2Tex/M_SkyWater.M_SkyWater"), false);
	// Real placements read from Skyrim.esm by tools/esm_refs.py: name,x,y,z,rx,ry,rz,scale (Skyrim units / radians).
	TArray<FString> Lines;
	FString Audit;
	FFileHelper::LoadFileToStringArray(Lines, *FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), TEXT("../../area2/placements.csv")));
	for (const FString& Line : Lines)
	{
		TArray<FString> F; Line.ParseIntoArray(F, TEXT(","));
		if (F.Num() < 8) continue;
		const FString Path = FString::Printf(TEXT("/Game/Area2/%s.%s"), *F[0], *F[0]);
		UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
		if (!Mesh) continue;
		const FVector Pos = FVector(FCString::Atof(*F[2]), FCString::Atof(*F[1]), FCString::Atof(*F[3])) * UnitsToCm;  // Skyrim X/Y swapped into UE
		// Rotation. The game's own 3D data shows R = Rx(-rx) * Ry(-ry) * Rz(-rz) (Skyrim space, right-handed, standard matrices).
		// Meshes were imported through Blender/FBX with Y mirrored (F = diag(1,-1,1)) and positions swap X/Y (C), so the UE
		// orientation is A = C * R * F^-1, which is a proper rotation. For pure yaw this equals yaw = skyrim yaw + 90 deg.
		const double rx = FCString::Atod(*F[4]), ry = FCString::Atod(*F[5]), rz = FCString::Atod(*F[6]);
		auto RX = [](double a) { const double c = FMath::Cos(a), s = FMath::Sin(a); return TArray<double>{ 1,0,0, 0,c,-s, 0,s,c }; };
		auto RY = [](double a) { const double c = FMath::Cos(a), s = FMath::Sin(a); return TArray<double>{ c,0,s, 0,1,0, -s,0,c }; };
		auto RZ = [](double a) { const double c = FMath::Cos(a), s = FMath::Sin(a); return TArray<double>{ c,-s,0, s,c,0, 0,0,1 }; };
		auto Mul = [](const TArray<double>& A, const TArray<double>& B) { TArray<double> M; M.SetNumZeroed(9);
			for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) for (int k = 0; k < 3; ++k) M[i*3+j] += A[i*3+k] * B[k*3+j]; return M; };
		const TArray<double> R = Mul(Mul(RX(-rx), RY(-ry)), RZ(-rz));
		TArray<double> RF = R;                                 // R * diag(1,-1,1): negate column 1
		for (int i = 0; i < 3; ++i) RF[i*3+1] = -RF[i*3+1];
		auto At = [&](int r, int c) { return RF[(r == 0 ? 1 : r == 1 ? 0 : 2) * 3 + c]; };   // C swaps rows 0 and 1
		const FVector XA(At(0,0), At(1,0), At(2,0)), YA(At(0,1), At(1,1), At(2,1)), ZA(At(0,2), At(1,2), At(2,2));
		const FRotator Rot = FMatrix(XA, YA, ZA, FVector::ZeroVector).Rotator();
		const float Yaw = Rot.Yaw;
		AStaticMeshActor* Act = W->SpawnActor<AStaticMeshActor>(Pos, Rot);
		Act->SetMobility(EComponentMobility::Movable);
		Act->GetStaticMeshComponent()->SetStaticMesh(Mesh);
		Act->SetActorScale3D(FVector(FCString::Atof(*F[7])));
		Act->GetStaticMeshComponent()->UpdateBounds();
		const FBoxSphereBounds& B = Act->GetStaticMeshComponent()->Bounds;   // exported for tools/verify_unreal.py (compared with the game's bounds)
		Audit += FString::Printf(TEXT("%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n"), *F[0], Pos.X, Pos.Y, Pos.Z, B.Origin.X, B.Origin.Y, B.Origin.Z, B.SphereRadius);
		UE_LOG(LogTemp, Warning, TEXT("SkyBridge: placed %s at %s yaw %.1f"), *F[0], *Pos.ToString(), Yaw);
	}
	FFileHelper::SaveStringToFile(Audit, *FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), TEXT("../../area2/ue_actors.csv")));
	// Lights recorded from the game's renderer (plugin -> area2/lights.tsv: x y z r g b radius fade dimmer slot), Skyrim units, 0-1 colours.
	{
		TArray<FString> LL;
		FFileHelper::LoadFileToStringArray(LL, *FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), TEXT("../../area2/lights.tsv")));
		int32 NumLights = 0;
		for (const FString& L : LL)
		{
			if (L.IsEmpty() || L.StartsWith(TEXT("#")) || L.StartsWith(TEXT("x"))) continue;
			TArray<FString> F; L.ParseIntoArray(F, TEXT("\t"));
			if (F.Num() < 9) continue;
			const FVector P = FVector(FCString::Atof(*F[1]), FCString::Atof(*F[0]), FCString::Atof(*F[2])) * UnitsToCm;
			const FLinearColor Col(FCString::Atof(*F[3]), FCString::Atof(*F[4]), FCString::Atof(*F[5]));
			const float Radius = FCString::Atof(*F[6]) * UnitsToCm, Dimmer = FCString::Atof(*F[8]);
			if (Radius < 10.f || Dimmer <= 0.f) continue;
			if (APointLight* PL = W->SpawnActor<APointLight>(P, FRotator::ZeroRotator))
			{
				PL->SetMobility(EComponentMobility::Movable);
				UPointLightComponent* C = PL->PointLightComponent;
				C->SetLightColor(Col);
				C->SetAttenuationRadius(Radius);
				C->SetIntensity(LightIntensityScale * Dimmer * (0.5f + Radius / 300.f));
				C->SetSourceRadius(6.f);
				C->SetCastShadows(NumLights < 24);
				++NumLights;
			}
		}
		UE_LOG(LogTemp, Warning, TEXT("SkyBridge: spawned %d lights"), NumLights);
	}
	// Water: one cell-sized plane per exterior cell that has a water height (tools/esm_water.py -> area2/water.csv: gx,gy,height).
	{
		TArray<FString> WLines;
		FFileHelper::LoadFileToStringArray(WLines, *FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), TEXT("../../area2/water.csv")));
		UStaticMesh* PlaneMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Plane.Plane"));
		UMaterialInterface* WaterMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Area2Tex/M_Water.M_Water"));
		for (const FString& WL : WLines)
		{
			TArray<FString> F; WL.ParseIntoArray(F, TEXT(","));
			if (F.Num() < 3 || !PlaneMesh) continue;
			const float GX = FCString::Atof(*F[0]), GY = FCString::Atof(*F[1]), H = FCString::Atof(*F[2]);
			const FVector Pos = FVector((GY + 0.5f) * 4096.f, (GX + 0.5f) * 4096.f, H) * UnitsToCm;
			AStaticMeshActor* Wa = W->SpawnActor<AStaticMeshActor>(Pos, FRotator::ZeroRotator);
			Wa->SetMobility(EComponentMobility::Movable);
			Wa->GetStaticMeshComponent()->SetStaticMesh(PlaneMesh);
			if (WaterMat) Wa->GetStaticMeshComponent()->SetMaterial(0, WaterMat);
			Wa->GetStaticMeshComponent()->SetCastShadow(false);
			Wa->SetActorScale3D(FVector(4096.f * UnitsToCm / 100.f, 4096.f * UnitsToCm / 100.f, 1.f));
		}
	}
	UE_LOG(LogTemp, Warning, TEXT("SkyBridge: demo world around %s"), *Foot.ToString());
	// Ground plane + light
	if (false)  // flat fallback floor, replaced by the real terrain mesh (placements.csv row "terrain")
	if (UStaticMesh* Plane = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Plane.Plane")))
	{
		AStaticMeshActor* G = W->SpawnActor<AStaticMeshActor>(Foot - FVector(0, 0, 400.f), FRotator::ZeroRotator);
		G->SetMobility(EComponentMobility::Movable);
		G->GetStaticMeshComponent()->SetStaticMesh(Plane);
		G->SetActorScale3D(FVector(400.f, 400.f, 1.f));
	}
	// Sun driven by the in-game hour (UpdateSky), real sky atmosphere, height fog driven by the weather, auto-exposure.
	Sun = W->SpawnActor<ADirectionalLight>(Foot + FVector(0, 0, 5000), FRotator(-45.f, 0.f, 0.f));
	if (Sun)
	{
		Sun->SetMobility(EComponentMobility::Movable);
		Sun->GetLightComponent()->SetIntensity(10.f);
		Cast<UDirectionalLightComponent>(Sun->GetLightComponent())->SetAtmosphereSunLight(true);
	}
	W->SpawnActor<ASkyAtmosphere>(FVector::ZeroVector, FRotator::ZeroRotator);
	Moon = W->SpawnActor<ADirectionalLight>(Foot + FVector(0, 0, 5000), FRotator(-40.f, 200.f, 0.f));
	if (Moon)
	{
		Moon->SetMobility(EComponentMobility::Movable);
		Moon->GetLightComponent()->SetIntensity(0.f);
		Cast<UDirectionalLightComponent>(Moon->GetLightComponent())->ForwardShadingPriority = 0;
	}
	Fog = W->SpawnActor<AExponentialHeightFog>(Foot, FRotator::ZeroRotator);
	if (APostProcessVolume* PP = W->SpawnActor<APostProcessVolume>(Foot, FRotator::ZeroRotator))
	{
		PP->bUnbound = true;
		PP->Settings.bOverride_AutoExposureMinBrightness = true; PP->Settings.AutoExposureMinBrightness = 1.0f;
		PP->Settings.bOverride_AutoExposureMaxBrightness = true; PP->Settings.AutoExposureMaxBrightness = 8.f;
		PP->Settings.bOverride_AutoExposureBias = true; PP->Settings.AutoExposureBias = 0.3f;
	}
	if (ASkyLight* S = W->SpawnActor<ASkyLight>(Foot + FVector(0, 0, 5000), FRotator::ZeroRotator))
	{
		S->GetLightComponent()->SetMobility(EComponentMobility::Movable);
		S->GetLightComponent()->bRealTimeCapture = true;
		S->GetLightComponent()->SetIntensity(3.0f);
	}
}

void ASkyrimCameraActor::UpdateSky(float Hour, const FString& WeatherId)
{
	if (!Sun) return;
	// Sun path: rises in the east (6h), south at noon, sets in the west (18h). In UE space north = +X, east = +Y,
	// and a directional light shines along its forward vector, so the light travels west->east after noon.
	// Skyrim days run roughly 5:30 -> 20:30 (sunrise to sunset); outside that the sun sits just below the horizon.
	const float Rise = 5.5f, SetH = 20.5f;
	const float T = (Hour - Rise) / (SetH - Rise);
	const bool bDay = T > 0.f && T < 1.f;
	const float Elev = bDay ? 70.f * FMath::Sin(PI * T) : -25.f;               // degrees above the horizon
	const float Yaw = bDay ? (T - 0.5f) * 2.f * 90.f : 0.f;
	Sun->SetActorRotation(FRotator(-Elev, Yaw, 0.f));
	if (Moon)  // simple moonlight: a dim blue directional light that is NOT the atmosphere sun, only active at night
	{
		Moon->GetLightComponent()->SetIntensity(bDay ? 0.f : 0.8f);
		Moon->GetLightComponent()->SetLightColor(FLinearColor(0.55f, 0.65f, 1.f));
	}

	// Weather -> light/fog multipliers from the editor id (e.g. "CloudyDLC2", "SkyrimOvercastRain", "SkyrimStormSnow", "SkyrimFog").
	const FString W = WeatherId.ToLower();
	float SunMul = 1.f, FogDensity = 0.002f;
	if (W.Contains(TEXT("fog")))                       { SunMul = 0.35f; FogDensity = 0.025f; }
	else if (W.Contains(TEXT("rain")) || W.Contains(TEXT("storm"))) { SunMul = 0.3f; FogDensity = 0.012f; }
	else if (W.Contains(TEXT("snow")) || W.Contains(TEXT("blizzard"))) { SunMul = 0.45f; FogDensity = 0.015f; }
	else if (W.Contains(TEXT("overcast")) || W.Contains(TEXT("cloud"))) { SunMul = 0.6f; FogDensity = 0.004f; }
	const float Day = FMath::Clamp(Elev / 12.f, 0.f, 1.f);                    // fade the sun out around the horizon
	Sun->GetLightComponent()->SetIntensity(bDay ? FMath::Max(0.05f, 10.f * SunMul * Day) : 0.f);
	if (Fog) Fog->GetComponent()->SetFogDensity(FogDensity);
}

void ASkyrimCameraActor::Tick(float Dt)
{
	Super::Tick(Dt);
	// Debug: -SkyBridgeCam=x,y,z,yawDeg,pitchDeg[,hour] (Skyrim coordinates, yaw clockwise from north) bypasses the live stream.
	FString CamArg;
	if (FParse::Value(FCommandLine::Get(), TEXT("SkyBridgeCam="), CamArg))
	{
		TArray<FString> C; CamArg.ParseIntoArray(C, TEXT(";"));   // x;y;z;yaw;pitch[;hour]  (commas are not safe in UE command lines)
		if (C.Num() >= 5)
		{
			const float X = FCString::Atof(*C[0]), Y = FCString::Atof(*C[1]), Z = FCString::Atof(*C[2]);
			const float Yaw = FMath::DegreesToRadians(FCString::Atof(*C[3])), Pitch = FMath::DegreesToRadians(FCString::Atof(*C[4]));
			const FVector SkyFwd(FMath::Sin(Yaw) * FMath::Cos(Pitch), FMath::Cos(Yaw) * FMath::Cos(Pitch), -FMath::Sin(Pitch));
			const FVector Fwd(SkyFwd.Y, SkyFwd.X, SkyFwd.Z);
			SetActorLocationAndRotation(FVector(Y, X, Z) * UnitsToCm, Fwd.Rotation());
			Camera->SetFieldOfView(90.f);
			if (!bWorldSpawned) { bWorldSpawned = true; SpawnDemoWorld(FVector(Y, X, Z) * UnitsToCm); }
			UpdateSky(C.Num() >= 6 ? FCString::Atof(*C[5]) : 12.f, TEXT("clear"));
			if (GEngine) GEngine->AddOnScreenDebugMessage(1, 0.f, FColor::Yellow, TEXT("DEBUG CAMERA"));
			return;
		}
	}
	if (!View)
	{
		MapHandle = OpenFileMappingW(FILE_MAP_READ, false, SkyBridge::kMappingName);
		if (MapHandle) View = MapViewOfFile((HANDLE)MapHandle, FILE_MAP_READ, 0, 0, sizeof(SkyBridge::Packet));
		if (!View) { Status = TEXT("waiting for Skyrim"); return; }
	}
	SkyBridge::Packet P;
	for (int Try = 0; Try < 4; ++Try)  // seqlock read
	{
		const uint32 S0 = ((volatile SkyBridge::Packet*)View)->seq;
		FMemory::Memcpy(&P, View, sizeof(P));
		if (!(S0 & 1) && S0 == ((volatile SkyBridge::Packet*)View)->seq) break;
	}
	if (P.magic != SkyBridge::kMagic || P.frame == 0) { Status = TEXT("connected, no data yet"); return; }

	// Skyrim (right-handed: X east, Y north, Z up) -> UE (left-handed: X fwd, Y right, Z up): swap X and Y.
	auto Conv = [](float X, float Y, float Z) { return FVector(Y, X, Z); };
	const FVector Pos = Conv(P.camPos[0], P.camPos[1], P.camPos[2]) * UnitsToCm;
	// UNVERIFIED: assumes forward = column 1 and up = column 2 of the NiCamera world rotation. Check in-game (README).
	const FVector Fwd = Conv(P.camRot[1], P.camRot[4], P.camRot[7]);
	const FVector Up = Conv(P.camRot[2], P.camRot[5], P.camRot[8]);
	SetActorLocationAndRotation(Pos, FRotationMatrix::MakeFromXZ(Fwd, Up).Rotator());
	if (P.fovDeg > 1.f) Camera->SetFieldOfView(P.fovDeg);
	if (!bWorldSpawned)
	{
		bWorldSpawned = true;
		SpawnDemoWorld(Conv(P.playerPos[0], P.playerPos[1], P.playerPos[2]) * UnitsToCm);
	}

	GameHour = P.gameHour;
	Weather = FString(UTF8_TO_TCHAR(P.weatherEditorID));
	UpdateSky(GameHour, Weather);
	Cell = FString(UTF8_TO_TCHAR(P.cellName));
	Status = FString::Printf(TEXT("live frame %u"), P.frame);
	UpdateRuntimeWorld();
	if (!Npcs) Npcs = NewObject<USkyNpcRuntime>(this);
	Npcs->Update(GetWorld(), P.camPos);
	if (Npcs->NumActors() > 0) Status += FString::Printf(TEXT(" | %s"), *Npcs->Describe());
	if (GEngine) GEngine->AddOnScreenDebugMessage(1, 0.f, FColor::Green,
		FString::Printf(TEXT("Skyrim: %s | %.2fh | %s | %s"), *Status, GameHour, *Weather, *Cell));
}


// rebuild variant 1 2026-10-27T17:12:48.9817260-07:00

// rebuild variant 2 2026-10-27T17:12:58.3335519-07:00

// rebuild variant 3 2026-10-27T17:13:07.4882435-07:00

// rebuild variant 4 2026-10-27T17:13:16.6504462-07:00

// rebuild variant 5 2026-10-27T17:13:25.7953651-07:00

// rebuild variant 6 2026-10-27T17:13:35.0023811-07:00
