#include "SkyNpcRuntime.h"
#include "SkyNpcMeshComponent.h"
#include "SkyrimCameraActor.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Components/StaticMeshComponent.h"
#include "ReferenceSkeleton.h"
#include "Dom/JsonObject.h"
#include "Dom/JsonValue.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/PlatformTime.h"
#include "Windows/AllowWindowsPlatformTypes.h"
#include <windows.h>
#include "Windows/HideWindowsPlatformTypes.h"
#include "../../../../shared/BridgeShared.h"

DEFINE_LOG_CATEGORY_STATIC(LogSkyNpc, Log, All);

namespace
{
constexpr double U = 1.4287;     // cm per Skyrim unit
constexpr double FL[3] = { 1.0, -1.0, 1.0 };

// ---- tiny quaternion / matrix helpers (same conventions as npc_live.py: qmul(a,b) <-> matrix a*b, row-major 3x3)
struct FQ { double x = 0, y = 0, z = 0, w = 1; };
FQ QMul(const FQ& a, const FQ& b)
{
	return { a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y, a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
	         a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w, a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z };
}
FQ QConj(const FQ& a) { return { -a.x, -a.y, -a.z, a.w }; }
FQ QFlip(const FQ& a) { return { -a.x, a.y, -a.z, a.w }; }   // F R F, F = diag(1,-1,1)
void QRot(const FQ& q, const double* v, double* o)
{
	const double tx = 2 * (q.y * v[2] - q.z * v[1]), ty = 2 * (q.z * v[0] - q.x * v[2]), tz = 2 * (q.x * v[1] - q.y * v[0]);
	o[0] = v[0] + q.w * tx + q.y * tz - q.z * ty;
	o[1] = v[1] + q.w * ty + q.z * tx - q.x * tz;
	o[2] = v[2] + q.w * tz + q.x * ty - q.y * tx;
}
FQ QNlerp(const FQ& a, FQ b, double t)
{
	if (a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w < 0) { b.x = -b.x; b.y = -b.y; b.z = -b.z; b.w = -b.w; }
	FQ q{ a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t, a.w + (b.w - a.w) * t };
	double n = FMath::Sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w);
	if (n < 1e-12) return FQ();
	return { q.x / n, q.y / n, q.z / n, q.w / n };
}
void QToMat(const FQ& q, double* m)
{
	const double x = q.x, y = q.y, z = q.z, w = q.w;
	m[0] = 1 - 2 * (y * y + z * z); m[1] = 2 * (x * y - z * w); m[2] = 2 * (x * z + y * w);
	m[3] = 2 * (x * y + z * w); m[4] = 1 - 2 * (x * x + z * z); m[5] = 2 * (y * z - x * w);
	m[6] = 2 * (x * z - y * w); m[7] = 2 * (y * z + x * w); m[8] = 1 - 2 * (x * x + y * y);
}
FQ MatToQ(const double* m)
{
	FQ r; const double tr = m[0] + m[4] + m[8]; double s;
	if (tr > 0) { s = FMath::Sqrt(tr + 1.0) * 2; r.w = 0.25 * s; r.x = (m[7] - m[5]) / s; r.y = (m[2] - m[6]) / s; r.z = (m[3] - m[1]) / s; }
	else if (m[0] > m[4] && m[0] > m[8]) { s = FMath::Sqrt(1.0 + m[0] - m[4] - m[8]) * 2; r.w = (m[7] - m[5]) / s; r.x = 0.25 * s; r.y = (m[1] + m[3]) / s; r.z = (m[2] + m[6]) / s; }
	else if (m[4] > m[8]) { s = FMath::Sqrt(1.0 + m[4] - m[0] - m[8]) * 2; r.w = (m[2] - m[6]) / s; r.x = (m[1] + m[3]) / s; r.y = 0.25 * s; r.z = (m[5] + m[7]) / s; }
	else { s = FMath::Sqrt(1.0 + m[8] - m[0] - m[4]) * 2; r.w = (m[3] - m[1]) / s; r.x = (m[2] + m[6]) / s; r.y = (m[5] + m[7]) / s; r.z = 0.25 * s; }
	return r;
}
void MulTV(const double* m, const double* v, double* o)   // m^T * v
{
	o[0] = m[0] * v[0] + m[3] * v[1] + m[6] * v[2];
	o[1] = m[1] * v[0] + m[4] * v[1] + m[7] * v[2];
	o[2] = m[2] * v[0] + m[5] * v[1] + m[8] * v[2];
}

constexpr int32 NumLimbs = 6;
const TCHAR* LimbNames[NumLimbs] = { TEXT("NPC L UpperArm [LUar]"), TEXT("NPC R UpperArm [RUar]"), TEXT("NPC L Forearm [LLar]"),
                                     TEXT("NPC L Thigh [LThg]"), TEXT("NPC R Thigh [RThg]"), TEXT("NPC L Calf [LClf]") };

struct FRestBone { FString Name; FName UeName; double R[9]; double P[3]; bool bMinor = false; };
struct FRestSkeleton
{
	bool bLoaded = false;
	TArray<FRestBone> Bones;
	TMap<FString, int32> Index;
	int32 Limb[NumLimbs];
	FQ LimbQ0[NumLimbs];     // conj(quat(R0)) of each limb bone
};

struct FSBone { float P[3] = {}; FQ Q; bool bValid = false; };
struct FSample
{
	double T = 0;
	double Rp[3] = {};
	FQ Rq;
	TArray<FSBone> B;        // indexed like FRestSkeleton::Bones
};
using FSamplePtr = TSharedPtr<FSample>;

struct FLimbRel { FQ Q[NumLimbs]; bool bValid[NumLimbs] = {}; };

struct FPlanBone { int32 Rest = 0; int32 Bone = 0; double D[3] = {}; FQ H; bool bMinor = false; };

struct FHist { double T = 0; double Rp[3] = {}; FQ Rq; FSamplePtr Pose; };

struct FEntry
{
	uint32 Id = 0, Base = 0;
	FString Key, SkelKey;
	TWeakObjectPtr<AActor> Actor;
	TWeakObjectPtr<USkyNpcMeshComponent> Comp;
	TWeakObjectPtr<AStaticMeshActor> Weapon;
	FString WeaponPath;
	TArray<FTransform> RefCS, Local, Space;
	TArray<FVector> RestScale;
	TArray<FPlanBone> Plan;
	TArray<FHist> Hist;
	double Dist = 0, Scale = 1, ScaleSet = 1, Dt = 0.033, Rt = -1, RtWall = 0, PosedT = -1e9, Speed = 0, LpT = 0, LpP[3] = {};
	bool bHasLp = false;
	int32 Frozen = -1;       // -1 unknown, 0 animated, 1 frozen
	FLimbRel Limbs;
	FSamplePtr Snap, Shown;
	bool bWeaponNode = false; float WP[3] = {}; FQ WQ;
};

constexpr SIZE_T ActorPoseSize = sizeof(SkyBridge::ActorPose);
}

struct USkyNpcRuntime::FImpl
{
	HANDLE ActorsMap = nullptr; const uint8* ActorsView = nullptr;
	HANDLE GearMap = nullptr; const uint8* GearView = nullptr;
	uint32 LastSeq = 0xFFFFFFFFu;
	double LastPoll = 0, LastGear = 0;
	TArray<uint8> Buf;
	TArray<uint8> NameTable;
	TArray<FString> Names;
	TMap<FString, int32> NameToIdx;
	TMap<FString, FRestSkeleton> Rests;
	TMap<FString, TArray<int32>> NameMaps;      // skeleton key -> stream name index -> rest bone index
	TSet<FName> BadBase;                        // meshes missing / without skeleton / without rest pose
	TMap<uint32, FEntry> Entries;
	TMap<FString, FSamplePtr> Templates;        // "<key>|1" moving, "<key>|0" idle
	TMap<uint32, uint32> GearFlags;             // id -> weaponFlags
	TMap<uint32, FString> GearWeapon;           // id -> right-hand weapon model
	FString LastStatus;
};

// ------------------------------------------------------------------------------------------------ helpers
static FString SkelKeyOf(const SkyBridge::ActorPose& A)
{
	FString S = UTF8_TO_TCHAR(A.skeleton);
	if (S.IsEmpty() || S.StartsWith(TEXT("actors/character/"))) return (A.flags & SkyBridge::kActorFemale) ? TEXT("female") : TEXT("male");
	FString K; bool bSep = false;
	for (TCHAR C : S.ToLower())
	{
		if ((C >= 'a' && C <= 'z') || (C >= '0' && C <= '9')) { if (bSep && !K.IsEmpty()) K += TEXT("_"); bSep = false; K.AppendChar(C); }
		else bSep = true;
	}
	return K;
}

static bool IsHuman(const SkyBridge::ActorPose& A)
{
	FString S = UTF8_TO_TCHAR(A.skeleton);
	return S.IsEmpty() || S.StartsWith(TEXT("actors/character/"));
}

static FString UeBoneName(const FString& N)
{
	FString R = N; R.ReplaceInline(TEXT(" "), TEXT("-")); R.ReplaceInline(TEXT("["), TEXT("_")); R.ReplaceInline(TEXT("]"), TEXT("_"));
	return R;
}

static FRestSkeleton& LoadRest(USkyNpcRuntime::FImpl& I, const FString& Key)
{
	if (FRestSkeleton* Found = I.Rests.Find(Key)) return *Found;
	FRestSkeleton& R = I.Rests.Add(Key);
	for (int32 k = 0; k < NumLimbs; ++k) R.Limb[k] = INDEX_NONE;
	const FString File = FString::Printf(TEXT("area2/npc/skin/skeleton_%s.json"), *Key);
	const FString Cands[2] = { FPaths::Combine(FPaths::ProjectDir(), File), FPaths::Combine(TEXT("C:/Users/Aidan/SkyrimUnrealBridge"), File) };
	FString Text;
	for (const FString& C : Cands) if (FFileHelper::LoadFileToString(Text, *C)) break;
	TArray<TSharedPtr<FJsonValue>> Arr;
	if (Text.IsEmpty() || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text), Arr))
	{
		UE_LOG(LogSkyNpc, Warning, TEXT("no rest pose for skeleton '%s'"), *Key);
		return R;
	}
	for (const TSharedPtr<FJsonValue>& V : Arr)
	{
		const TSharedPtr<FJsonObject>* O = nullptr;
		if (!V->TryGetObject(O) || !O) continue;
		FRestBone B;
		B.Name = (*O)->GetStringField(TEXT("name"));
		const TArray<TSharedPtr<FJsonValue>>* Rot = nullptr; const TArray<TSharedPtr<FJsonValue>>* Pos = nullptr;
		if (!(*O)->TryGetArrayField(TEXT("rot"), Rot) || Rot->Num() < 9 || !(*O)->TryGetArrayField(TEXT("pos"), Pos) || Pos->Num() < 3) continue;
		for (int32 i = 0; i < 9; ++i) B.R[i] = (*Rot)[i]->AsNumber();
		for (int32 i = 0; i < 3; ++i) B.P[i] = (*Pos)[i]->AsNumber();
		B.UeName = FName(*UeBoneName(B.Name));
		static const TCHAR* Minor[] = { TEXT("Finger"), TEXT("Toe"), TEXT("Breast"), TEXT("Butt"), TEXT("Belly"), TEXT("Anus"), TEXT("Pussy"), TEXT("Genitals") };
		for (const TCHAR* M : Minor) if (B.Name.Contains(M)) { B.bMinor = true; break; }
		R.Index.Add(B.Name, R.Bones.Num());
		R.Bones.Add(B);
	}
	for (int32 k = 0; k < NumLimbs; ++k)
		if (const int32* Ix = R.Index.Find(LimbNames[k])) { R.Limb[k] = *Ix; R.LimbQ0[k] = QConj(MatToQ(R.Bones[*Ix].R)); }
	R.bLoaded = R.Bones.Num() > 0;
	UE_LOG(LogSkyNpc, Log, TEXT("rest pose '%s': %d bones"), *Key, R.Bones.Num());
	return R;
}

static FLimbRel LimbRel(const FSample& S, const FRestSkeleton& R)
{
	FLimbRel L; const FQ Rc = QConj(S.Rq);
	for (int32 k = 0; k < NumLimbs; ++k)
		if (R.Limb[k] != INDEX_NONE && S.B[R.Limb[k]].bValid) { L.Q[k] = QMul(Rc, S.B[R.Limb[k]].Q); L.bValid[k] = true; }
	return L;
}

static double LimbChange(const FLimbRel& A, const FLimbRel& B)   // largest angle (deg); -1 if fewer than 4 shared limbs
{
	int32 N = 0; double Best = 0;
	for (int32 k = 0; k < NumLimbs; ++k)
	{
		if (!A.bValid[k] || !B.bValid[k]) continue;
		++N;
		const double D = A.Q[k].x * B.Q[k].x + A.Q[k].y * B.Q[k].y + A.Q[k].z * B.Q[k].z + A.Q[k].w * B.Q[k].w;
		Best = FMath::Max(Best, FMath::RadiansToDegrees(2.0 * FMath::Acos(FMath::Min(1.0, FMath::Abs(D)))));
	}
	return N >= 4 ? Best : -1.0;
}

static bool IsBind(const FSample& S, const FRestSkeleton& R)   // every limb at the same angle from its rest pose: un-animated skeleton
{
	const FQ Rc = QConj(S.Rq); double Mn = 1e9, Mx = -1e9; int32 N = 0;
	for (int32 k = 0; k < NumLimbs; ++k)
	{
		if (R.Limb[k] == INDEX_NONE || !S.B[R.Limb[k]].bValid) continue;
		const double W = QMul(QMul(Rc, S.B[R.Limb[k]].Q), R.LimbQ0[k]).w;
		const double Ang = FMath::RadiansToDegrees(2.0 * FMath::Acos(FMath::Min(1.0, FMath::Abs(W))));
		Mn = FMath::Min(Mn, Ang); Mx = FMath::Max(Mx, Ang); ++N;
	}
	return N >= 4 && (Mx - Mn) < 6.0;
}

static FSamplePtr Blend(const FSamplePtr& A, const FSamplePtr& B, double F)
{
	if (A == B || F <= 0.0) return A;
	if (F >= 1.0) return B;
	FSamplePtr O = MakeShared<FSample>();
	O->T = A->T;
	for (int32 i = 0; i < 3; ++i) O->Rp[i] = A->Rp[i] + (B->Rp[i] - A->Rp[i]) * F;
	O->Rq = QNlerp(A->Rq, B->Rq, F);
	O->B.SetNum(A->B.Num());
	for (int32 i = 0; i < A->B.Num(); ++i)
	{
		const FSBone& a = A->B[i]; const FSBone& b = B->B.IsValidIndex(i) ? B->B[i] : a;
		FSBone& o = O->B[i];
		if (!a.bValid || !b.bValid) { o = a.bValid ? a : b; continue; }
		o.bValid = true;
		for (int32 k = 0; k < 3; ++k) o.P[k] = a.P[k] + (b.P[k] - a.P[k]) * (float)F;
		o.Q = QNlerp(a.Q, b.Q, F);
	}
	return O;
}

static double PoseGap(double Dist) { return Dist < 1500 ? 1.0 / 60 : (Dist < 3000 ? 1.0 / 30 : 1.0 / 15); }

static FRotator ActorRot(const FQ& Q)
{
	double M[9]; QToMat(Q, M);
	float Mf[9]; for (int32 i = 0; i < 9; ++i) Mf[i] = (float)M[i];
	return ASkyrimCameraActor::RuntimeRotation(Mf);
}

static FVector ActorPos(const double* Rp)
{
	const float P[3] = { (float)Rp[0], (float)Rp[1], (float)Rp[2] };
	return ASkyrimCameraActor::RuntimePosition(P, (float)U);
}

// Builds the reference pose, the per-bone plan and the buffers of a freshly spawned entry.
static bool PrepareEntry(USkyNpcRuntime::FImpl& I, FEntry& E, USkeletalMesh* Mesh)
{
	const FRestSkeleton& Rest = LoadRest(I, E.SkelKey);
	if (!Rest.bLoaded) return false;
	const FReferenceSkeleton& Ref = Mesh->GetRefSkeleton();
	const int32 N = Ref.GetNum();
	if (N <= 0) return false;
	const TArray<FTransform>& RefPose = Ref.GetRefBonePose();
	E.RefCS.SetNum(N); E.RestScale.SetNum(N);
	for (int32 i = 0; i < N; ++i)       // parents come before children
	{
		const int32 P = Ref.GetParentIndex(i);
		E.RefCS[i] = P >= 0 ? RefPose[i] * E.RefCS[P] : RefPose[i];
		E.RestScale[i] = E.RefCS[i].GetScale3D();
	}
	E.Local = RefPose; E.Space = E.RefCS;
	E.Plan.Reset();
	for (int32 r = 0; r < Rest.Bones.Num(); ++r)
	{
		const FRestBone& B = Rest.Bones[r];
		const int32 Bi = Ref.FindBoneIndex(B.UeName);
		if (Bi == INDEX_NONE) continue;
		const FQuat RB = E.RefCS[Bi].GetRotation(); const FVector T = E.RefCS[Bi].GetTranslation();
		const FQ qRB0{ RB.X, RB.Y, RB.Z, RB.W };
		FPlanBone P; P.Rest = r; P.Bone = Bi; P.bMinor = B.bMinor;
		P.H = QMul(QFlip(QConj(MatToQ(B.R))), qRB0);
		const double c[3] = { FL[0] * T.X - U * B.P[0], FL[1] * T.Y - U * B.P[1], FL[2] * T.Z - U * B.P[2] };
		MulTV(B.R, c, P.D);                 // d = R0^T c
		E.Plan.Add(P);
	}
	return E.Plan.Num() > 8;
}

// Writes the pose into the component (port of npc_live._apply_pose + SkyBridgeViewLibrary::ApplyPose).
static void ApplyPose(FEntry& E, const FSample& S, bool bFar)
{
	USkyNpcMeshComponent* C = E.Comp.Get();
	if (!C || !C->GetSkinnedAsset()) return;
	const FQ Qa = QFlip(QConj(S.Rq));
	double Rr[9]; QToMat(S.Rq, Rr);
	double M[9];                             // F * Rroot^T
	for (int32 r = 0; r < 3; ++r) for (int32 c = 0; c < 3; ++c) M[r * 3 + c] = Rr[c * 3 + r] * FL[r];
	const double Ks = U / FMath::Max(0.01, E.Scale);
	const int32 N = E.Space.Num();
	TBitArray<> Given(false, N);
	for (const FPlanBone& P : E.Plan)
	{
		if (bFar && P.bMinor) continue;
		const FSBone& B = S.B[P.Rest];
		if (!B.bValid) continue;
		double V[3]; QRot(B.Q, P.D, V);
		const double W[3] = { V[0] + Ks * (B.P[0] - S.Rp[0]), V[1] + Ks * (B.P[1] - S.Rp[1]), V[2] + Ks * (B.P[2] - S.Rp[2]) };
		const FQ R = QMul(Qa, QMul(QFlip(B.Q), P.H));
		const FVector Loc(M[0] * W[0] + M[1] * W[1] + M[2] * W[2], M[3] * W[0] + M[4] * W[1] + M[5] * W[2], M[6] * W[0] + M[7] * W[1] + M[8] * W[2]);
		FQuat Q(R.x, R.y, R.z, R.w); Q.Normalize();
		E.Space[P.Bone] = FTransform(Q, Loc, E.RestScale[P.Bone]);
		Given[P.Bone] = true;
	}
	const FReferenceSkeleton& Ref = C->GetSkinnedAsset()->GetRefSkeleton();
	for (int32 i = 0; i < N; ++i)
	{
		const int32 Par = Ref.GetParentIndex(i);
		if (Given[i]) E.Local[i] = Par >= 0 ? E.Space[i].GetRelativeTransform(E.Space[Par]) : E.Space[i];
		else E.Space[i] = Par >= 0 ? E.Local[i] * E.Space[Par] : E.Local[i];
	}
	C->SetPoseComponentSpace(E.Space);
}

// New stream sample for an actor: choose the pose to show and append to its history (port of npc_live._ingest).
static void Ingest(USkyNpcRuntime::FImpl& I, FEntry& E, const FSamplePtr& Cur, const FRestSkeleton& Rest, double Now, float ActorScale)
{
	E.Scale = ActorScale > 0.01f ? ActorScale : 1.0;
	const FVector CurRp(Cur->Rp[0], Cur->Rp[1], Cur->Rp[2]);
	if (!E.bHasLp)
	{
		E.bHasLp = true; E.LpT = Now; FMemory::Memcpy(E.LpP, Cur->Rp, sizeof(E.LpP)); E.Speed = 0; E.Limbs = LimbRel(*Cur, Rest);
	}
	else if (Now - E.LpT >= 0.25)
	{
		E.Speed = FVector::Dist(CurRp, FVector(E.LpP[0], E.LpP[1], E.LpP[2])) / (Now - E.LpT);
		E.LpT = Now; FMemory::Memcpy(E.LpP, Cur->Rp, sizeof(E.LpP));
		const FLimbRel L = LimbRel(*Cur, Rest);
		const double Ch = LimbChange(E.Limbs, L);
		E.Frozen = Ch >= 0 ? (Ch < 0.5 ? 1 : 0) : -1;
		E.Limbs = L;
	}
	const bool bMoving = E.Speed > 25.0;
	// Skyrim stops animating actors it is not drawing: bind pose if never drawn, else frozen in the last pose. Keep the actor's
	// last real pose, or borrow a natural one from another animated actor of the same skeleton.
	FSamplePtr Pose = Cur;
	const FString TplMove = E.SkelKey + TEXT("|1"), TplIdle = E.SkelKey + TEXT("|0");
	if (IsBind(*Cur, Rest) || (bMoving && E.Frozen == 1))
	{
		FSamplePtr* T = I.Templates.Find(bMoving ? TplMove : TplIdle);
		FSamplePtr* TIdle = I.Templates.Find(TplIdle);
		FSamplePtr Pick = bMoving ? (T ? *T : nullptr) : E.Snap;
		if (!Pick) Pick = E.Snap;
		if (!Pick && T) Pick = *T;
		if (!Pick && TIdle) Pick = *TIdle;
		if (Pick) Pose = Pick;
	}
	else
	{
		E.Snap = Cur;
		I.Templates.Add(bMoving ? TplMove : TplIdle, Cur);
	}
	if (E.Hist.Num())
	{
		const FHist& L = E.Hist.Last();
		const double Gap = Now - L.T;
		if (Gap < 0.25) E.Dt = 0.8 * E.Dt + 0.2 * Gap;
		if (FVector::Dist(CurRp, FVector(L.Rp[0], L.Rp[1], L.Rp[2])) > 300.0) E.Hist.Reset();   // teleport / load door
	}
	FHist H; H.T = Now; FMemory::Memcpy(H.Rp, Cur->Rp, sizeof(H.Rp)); H.Rq = Cur->Rq; H.Pose = Pose;
	E.Hist.Add(H);
	if (E.Hist.Num() > 16) E.Hist.RemoveAt(0, E.Hist.Num() - 16, EAllowShrinking::No);
}

// Per rendered frame: place the actor between its last two stream samples (shown ~one stream interval late) and pose the limbs.
static void Smooth(FEntry& E, double Now)
{
	if (!E.Hist.Num() || !E.Actor.IsValid() || !E.Comp.IsValid()) return;
	const double Delay = FMath::Min(0.2, FMath::Max(0.04, 1.6 * E.Dt));
	const double Newest = E.Hist.Last().T;
	if (E.Rt < 0 || FMath::Abs(Newest - E.Rt) > 1.0) E.Rt = Newest - Delay;
	else
	{
		const double Rate = FMath::Clamp(1.0 + (Newest - E.Rt - Delay) / (2.0 * Delay), 0.0, 2.0);
		E.Rt = FMath::Min(Newest, E.Rt + (Now - E.RtWall) * Rate);
	}
	E.Rt = FMath::Max(E.Rt, E.Hist[0].T);
	E.RtWall = Now;
	int32 i = 0;
	while (i + 1 < E.Hist.Num() && E.Hist[i + 1].T <= E.Rt) ++i;
	const FHist& A = E.Hist[i];
	const FHist* B = &A; double F = 0;
	if (i + 1 < E.Hist.Num() && E.Rt > A.T) { B = &E.Hist[i + 1]; F = FMath::Min(1.0, (E.Rt - A.T) / FMath::Max(1e-4, B->T - A.T)); }
	double Rp[3]; for (int32 k = 0; k < 3; ++k) Rp[k] = A.Rp[k] + (B->Rp[k] - A.Rp[k]) * F;
	const FQ Rq = QNlerp(A.Rq, B->Rq, F);
	E.Actor->SetActorLocationAndRotation(ActorPos(Rp), ActorRot(Rq), false, nullptr, ETeleportType::TeleportPhysics);
	if (FMath::Abs(E.Scale - E.ScaleSet) > 0.01) { E.Actor->SetActorScale3D(FVector(E.Scale)); E.ScaleSet = E.Scale; }
	if (Now - E.PosedT < PoseGap(E.Dist) * 0.9) return;
	if (F <= 0.0 && A.Pose == E.Shown) return;
	const FSamplePtr P = F > 0.0 ? Blend(A.Pose, B->Pose, F) : A.Pose;
	ApplyPose(E, *P, E.Dist > 700);
	E.Shown = F > 0.0 ? FSamplePtr() : P;
	E.PosedT = Now;
}

static const uint8* OpenView(HANDLE& H, const wchar_t* Name, SIZE_T Size)
{
	if (!H) H = OpenFileMappingW(FILE_MAP_READ, false, Name);
	if (!H) return nullptr;
	return (const uint8*)MapViewOfFile(H, FILE_MAP_READ, 0, 0, Size);
}

// ------------------------------------------------------------------------------------------------ USkyNpcRuntime
int32 USkyNpcRuntime::NumActors() const { return Impl.IsValid() ? Impl->Entries.Num() : 0; }
FString USkyNpcRuntime::Describe() const { return Impl.IsValid() ? Impl->LastStatus : FString(); }

void USkyNpcRuntime::Shutdown()
{
	if (!Impl.IsValid()) return;
	for (auto& KV : Impl->Entries)
	{
		if (AActor* A = KV.Value.Actor.Get()) A->Destroy();
		if (AActor* W = KV.Value.Weapon.Get()) W->Destroy();
	}
	Impl->Entries.Reset();
}

void USkyNpcRuntime::Update(UWorld* World, const float* CamSky)
{
	if (!World) return;
	if (!Impl.IsValid()) Impl = MakeShared<FImpl>();
	FImpl& I = *Impl;
	const double Now = FPlatformTime::Seconds();
	if (!I.ActorsView) { I.ActorsView = OpenView(I.ActorsMap, SkyBridge::kActorsName, SkyBridge::kActorsSize); if (!I.ActorsView) return; }

	// 1) new stream sample (checked at most 60 Hz; the stream itself is ~30 Hz)
	const volatile uint32* SeqPtr = (const volatile uint32*)(I.ActorsView + 8);
	if (Now - I.LastPoll >= 1.0 / 60.0 && *SeqPtr != I.LastSeq && !(*SeqPtr & 1))
	{
		I.LastPoll = Now;
		bool bOk = false; int32 nA = 0, nNames = 0; uint32 S0 = 0;
		for (int32 Try = 0; Try < 4 && !bOk; ++Try)
		{
			S0 = *SeqPtr; if (S0 & 1) continue;
			const SkyBridge::ActorHeader* Hd = (const SkyBridge::ActorHeader*)I.ActorsView;
			if (Hd->magic != SkyBridge::kActorsMagic) break;
			nA = (int32)FMath::Min<uint32>(Hd->nActors, SkyBridge::kMaxActors);
			nNames = (int32)FMath::Min<uint32>(Hd->nBoneNames, SkyBridge::kMaxBoneNames);
			const SIZE_T Bytes = SkyBridge::kActorPosesOff + (SIZE_T)nA * ActorPoseSize;
			I.Buf.SetNumUninitialized((int32)Bytes, EAllowShrinking::No);
			FMemory::Memcpy(I.Buf.GetData(), I.ActorsView, Bytes);
			bOk = (*SeqPtr == S0);
		}
		if (bOk)
		{
			I.LastSeq = S0;
			const uint8* Tbl = I.Buf.GetData() + SkyBridge::kActorNamesOff;
			const int32 TblBytes = nNames * SkyBridge::kBoneNameLen;
			if (I.NameTable.Num() != TblBytes || FMemory::Memcmp(I.NameTable.GetData(), Tbl, TblBytes) != 0)
			{
				I.NameTable.SetNumUninitialized(TblBytes); FMemory::Memcpy(I.NameTable.GetData(), Tbl, TblBytes);
				I.Names.Reset(); I.NameToIdx.Reset(); I.NameMaps.Reset();
				for (int32 n = 0; n < nNames; ++n)
				{
					char Tmp[SkyBridge::kBoneNameLen + 1]; FMemory::Memcpy(Tmp, Tbl + n * SkyBridge::kBoneNameLen, SkyBridge::kBoneNameLen); Tmp[SkyBridge::kBoneNameLen] = 0;
					I.Names.Add(UTF8_TO_TCHAR(Tmp)); I.NameToIdx.Add(I.Names.Last(), n);
				}
			}
			// gear (~1 Hz): right-hand weapons
			if (Now - I.LastGear > 1.0)
			{
				I.LastGear = Now;
				if (!I.GearView) I.GearView = OpenView(I.GearMap, SkyBridge::kGearName, SkyBridge::kGearSize);
				if (I.GearView)
				{
					const SkyBridge::GearHeader* GH = (const SkyBridge::GearHeader*)I.GearView;
					const int32 nG = (int32)FMath::Min<uint32>(GH->nActors, SkyBridge::kMaxActors);
					I.GearFlags.Reset(); I.GearWeapon.Reset();
					for (int32 g = 0; g < nG; ++g)
					{
						const SkyBridge::ActorGear* AG = (const SkyBridge::ActorGear*)(I.GearView + sizeof(SkyBridge::GearHeader) + (SIZE_T)g * sizeof(SkyBridge::ActorGear));
						I.GearFlags.Add(AG->id, AG->weaponFlags);
						char Tmp[SkyBridge::kGearPathLen + 1]; FMemory::Memcpy(Tmp, AG->weapons[0], SkyBridge::kGearPathLen); Tmp[SkyBridge::kGearPathLen] = 0;
						I.GearWeapon.Add(AG->id, UTF8_TO_TCHAR(Tmp));
					}
				}
			}

			// choose actors: nearest first, up to CreatureSlots creatures before the townsfolk
			struct FCand { double D; int32 Ix; };
			TArray<FCand> Creatures, Humans;
			for (int32 a = 0; a < nA; ++a)
			{
				const SkyBridge::ActorPose* A = (const SkyBridge::ActorPose*)(I.Buf.GetData() + SkyBridge::kActorPosesOff + (SIZE_T)a * ActorPoseSize);
				if ((A->flags & SkyBridge::kActorIsPlayer) || A->nBones < 8) continue;
				const double D = FVector::Dist(FVector(A->pos[0], A->pos[1], A->pos[2]), FVector(CamSky[0], CamSky[1], CamSky[2]));
				if (D > RadiusUnits) continue;
				(IsHuman(*A) ? Humans : Creatures).Add({ D, a });
			}
			auto ByDist = [](const FCand& L, const FCand& R) { return L.D < R.D; };
			Creatures.Sort(ByDist); Humans.Sort(ByDist);
			TArray<FCand> Order;
			for (int32 k = 0; k < Creatures.Num() && k < CreatureSlots; ++k) Order.Add(Creatures[k]);
			for (const FCand& C : Humans) Order.Add(C);
			for (int32 k = CreatureSlots; k < Creatures.Num(); ++k) Order.Add(Creatures[k]);

			TSet<uint32> Keep; int32 Loaded = 0;
			for (const FCand& C : Order)
			{
				if (Keep.Num() >= MaxNpcs) break;
				const SkyBridge::ActorPose* A = (const SkyBridge::ActorPose*)(I.Buf.GetData() + SkyBridge::kActorPosesOff + (SIZE_T)C.Ix * ActorPoseSize);
				const FString Key = FString::Printf(TEXT("npc_%08x"), A->baseId);
				const FName KeyName(*Key);
				if (I.BadBase.Contains(KeyName)) continue;
				FEntry* E = I.Entries.Find(A->id);
				if (!E)
				{
					TObjectPtr<USkeletalMesh>* Cached = Meshes.Find(KeyName);
					USkeletalMesh* Mesh = Cached ? Cached->Get() : nullptr;
					if (!Mesh)
					{
						if (Loaded >= 1) continue;            // one (slow) synchronous load per sample
						++Loaded;
						Mesh = LoadObject<USkeletalMesh>(nullptr, *FString::Printf(TEXT("/Game/Npc/%s.%s"), *Key, *Key));
						if (!Mesh || !Mesh->GetSkeleton())    // a skeleton-less mesh trips the engine's AssetSkeletonObj assertion
						{
							UE_LOG(LogSkyNpc, Log, TEXT("%s: no mesh/skeleton, skipped"), *Key);
							I.BadBase.Add(KeyName); continue;
						}
						Meshes.Add(KeyName, Mesh);
					}
					FEntry NE; NE.Id = A->id; NE.Base = A->baseId; NE.Key = Key; NE.SkelKey = SkelKeyOf(*A);
					if (!PrepareEntry(I, NE, Mesh)) { UE_LOG(LogSkyNpc, Warning, TEXT("%s: no usable rest pose (%s)"), *Key, *NE.SkelKey); I.BadBase.Add(KeyName); continue; }
					FActorSpawnParameters SP; SP.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
					AActor* Act = World->SpawnActor<AActor>(AActor::StaticClass(), FTransform::Identity, SP);
					if (!Act) continue;
					USkyNpcMeshComponent* Comp = NewObject<USkyNpcMeshComponent>(Act, TEXT("NpcMesh"));
					Comp->SetMobility(EComponentMobility::Movable);
					Comp->SetSkeletalMesh(Mesh);
					Comp->SetCastShadow(true);
					Act->SetRootComponent(Comp);
					Act->AddInstanceComponent(Comp);
					Comp->RegisterComponent();
					NE.Actor = Act; NE.Comp = Comp;
					E = &I.Entries.Add(A->id, MoveTemp(NE));
					UE_LOG(LogSkyNpc, Log, TEXT("spawned %s (%s, %d plan bones)"), *Key, *E->SkelKey, E->Plan.Num());
				}
				Keep.Add(A->id);
				E->Dist = C.D;
				// stream -> sample
				const FRestSkeleton& Rest = *I.Rests.Find(E->SkelKey);
				TArray<int32>* NM = I.NameMaps.Find(E->SkelKey);
				if (!NM)
				{
					NM = &I.NameMaps.Add(E->SkelKey); NM->Init(INDEX_NONE, I.Names.Num());
					for (int32 n = 0; n < I.Names.Num(); ++n) if (const int32* Ix = Rest.Index.Find(I.Names[n])) (*NM)[n] = *Ix;
				}
				FSamplePtr S = MakeShared<FSample>();
				S->T = Now; S->B.SetNum(Rest.Bones.Num());
				const int32* pNpc = I.NameToIdx.Find(TEXT("NPC")); const int32 NodeNpc = pNpc ? *pNpc : -1;
				const int32* pSkel = I.NameToIdx.Find(TEXT("skeleton.nif")); const int32 NodeSkel = pSkel ? *pSkel : -1;
				const int32* pWeap = I.NameToIdx.Find(TEXT("WEAPON")); const int32 NodeWeapon = pWeap ? *pWeap : -1;
				const int32 nb = (int32)FMath::Min<uint32>(A->nBones, SkyBridge::kMaxBones);
				const SkyBridge::ABone* RootB = nullptr;
				E->bWeaponNode = false;
				for (int32 b = 0; b < nb; ++b)
				{
					const SkyBridge::ABone& AB = A->bones[b];
					if (AB.name == NodeNpc) RootB = &AB;
					else if (!RootB && AB.name == NodeSkel) RootB = &AB;
					if (AB.name == NodeWeapon) { E->bWeaponNode = true; for (int32 k = 0; k < 3; ++k) E->WP[k] = AB.pos[k]; E->WQ = { AB.quat[0], AB.quat[1], AB.quat[2], AB.quat[3] }; }
					if (AB.name < NM->Num() && (*NM)[AB.name] != INDEX_NONE)
					{
						FSBone& SB = S->B[(*NM)[AB.name]];
						SB.bValid = true; for (int32 k = 0; k < 3; ++k) SB.P[k] = AB.pos[k];
						SB.Q = { AB.quat[0], AB.quat[1], AB.quat[2], AB.quat[3] };
					}
				}
				if (!RootB) RootB = &A->bones[0];          // creatures: first bone of the tree
				for (int32 k = 0; k < 3; ++k) S->Rp[k] = RootB->pos[k];
				S->Rq = { RootB->quat[0], RootB->quat[1], RootB->quat[2], RootB->quat[3] };
				Ingest(I, *E, S, Rest, Now, A->scale);

				// right-hand weapon (rigid mesh on the WEAPON node, only while drawn)
				const uint32* WF = I.GearFlags.Find(A->id); const FString* WP = I.GearWeapon.Find(A->id);
				const bool bWant = WF && WP && !WP->IsEmpty() && E->bWeaponNode && (A->flags & SkyBridge::kActorWeaponDrawn) && (*WF & 1) && !(*WF & 4);
				if (!bWant) { if (AActor* W = E->Weapon.Get()) W->Destroy(); E->Weapon = nullptr; E->WeaponPath.Reset(); }
				else
				{
					const FName WName = ASkyrimCameraActor::RuntimeAssetName(TCHAR_TO_UTF8(**WP));
					TObjectPtr<UStaticMesh>* WC = WeaponMeshes.Find(WName);
					if (!WC && !I.BadBase.Contains(WName))
					{
						UStaticMesh* WM = LoadObject<UStaticMesh>(nullptr, *FString::Printf(TEXT("/Game/Area2/%s.%s"), *WName.ToString(), *WName.ToString()));
						if (WM) WC = &WeaponMeshes.Add(WName, WM); else I.BadBase.Add(WName);
					}
					if (WC && WC->Get())
					{
						AStaticMeshActor* WA = E->Weapon.Get();
						if (!WA || E->WeaponPath != *WP)
						{
							if (WA) WA->Destroy();
							WA = World->SpawnActor<AStaticMeshActor>();
							if (WA) { WA->SetMobility(EComponentMobility::Movable); WA->GetStaticMeshComponent()->SetStaticMesh(WC->Get()); WA->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision); }
							E->Weapon = WA; E->WeaponPath = *WP;
						}
						if (WA)
						{
							const double Wp[3] = { E->WP[0], E->WP[1], E->WP[2] };
							WA->SetActorLocationAndRotation(ActorPos(Wp), ActorRot(E->WQ), false, nullptr, ETeleportType::TeleportPhysics);
						}
					}
				}
			}
			for (auto It = I.Entries.CreateIterator(); It; ++It)
			{
				if (!Keep.Contains(It.Key()))
				{
					if (AActor* Act = It.Value().Actor.Get()) Act->Destroy();
					if (AActor* W = It.Value().Weapon.Get()) W->Destroy();
					It.RemoveCurrent();
				}
			}
			I.LastStatus = FString::Printf(TEXT("%d npcs (%d streamed)"), I.Entries.Num(), nA);
		}
	}

	// 2) every frame: smooth + pose
	for (auto& KV : I.Entries) Smooth(KV.Value, Now);
}
