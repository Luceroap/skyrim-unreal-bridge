// Shared-memory layout between the SKSE plugin (writer) and Unreal (reader).
// Mapping name: "Local\\SkyrimUnrealBridge_v1". Skyrim world coordinates (units, X east, Y north, Z up).
#pragma once
#include <cstdint>

namespace SkyBridge
{
	constexpr const wchar_t* kMappingName = L"Local\\SkyrimUnrealBridge_v1";
	constexpr std::uint32_t kMagic = 0x42554B53;  // 'SKUB'
	constexpr std::uint32_t kVersion = 3;

	// Packet::uiFlags
	constexpr std::uint32_t kUiShowSkyrim = 1u << 0;   // a menu, dialogue, loading screen or the main menu is up: show Skyrim's frame
	constexpr std::uint32_t kUiMainMenu = 1u << 1;
	constexpr std::uint32_t kUiLoading = 1u << 2;
	constexpr std::uint32_t kUiCombat = 1u << 3;
	constexpr std::uint32_t kUiSneaking = 1u << 4;
	constexpr std::uint32_t kUiWeaponDrawn = 1u << 5;
	constexpr std::uint32_t kUiInWorld = 1u << 6;      // player 3D loaded (the rest of the packet is live)

#pragma pack(push, 4)
	struct Packet
	{
		std::uint32_t magic;
		std::uint32_t version;
		std::uint32_t seq;  // seqlock: odd while writer is mid-update
		std::uint32_t frame;
		float playerPos[3];
		float playerAngle[3];  // pitch(x), roll(y), yaw(z) radians, Skyrim convention
		float camPos[3];
		float camRot[9];  // NiMatrix3 world rotation, row-major
		float fovDeg;
		float gameHour;  // 0..24
		float gameDays;  // days passed
		std::uint32_t weatherFormID;
		std::uint32_t cellFormID;
		char weatherEditorID[64];
		char cellName[64];
		char worldspaceName[64];
		// ---- version 2 (appended; a version 1 writer leaves these zero)
		std::uint32_t uiFlags;
		float health[2], magicka[2], stamina[2];   // current, maximum
		float rain, snow, cloudy, pleasant;        // weather classification blended over the weather transition (0..1)
		float weatherPct;                          // transition from lastWeather to currentWeather (0..1)
		std::uint32_t lastWeatherFormID;
		float sunPos[3];                           // sun disc world position (direction = sunPos - camPos)
		float sunColor[3], ambientColor[3], fogColor[3], skyUpper[3], horizon[3];   // Sky::skyColor, 0..1 linear-ish
		float fogNear, fogFar, windSpeed;
		// ---- version 3 (appended; older readers just ignore the tail)
		char crosshair[64];                        // what the crosshair points at: "<verb>\t<name>", e.g. "Talk\tSigurd" (empty if nothing)
	};
#pragma pack(pop)

	// ---- World stream (second mapping): every nearby placed object + active lights, updated ~1 Hz ----
	// Layout: WorldHeader | char models[kMaxModels][kModelLen] | WRef refs[kMaxRefs] | WLight lights[kMaxLights]
	constexpr const wchar_t* kWorldName = L"Local\\SkyrimUnrealBridge_world_v1";
	constexpr std::uint32_t kWorldMagic = 0x444C5257;  // 'WRLD'
	constexpr std::uint32_t kMaxModels = 4096, kMaxRefs = 16384, kMaxLights = 512, kModelLen = 128;
#pragma pack(push, 4)
	struct WorldHeader
	{
		std::uint32_t magic, version, seq, tick, nRefs, nModels, nLights, pad;
	};
	struct WRef
	{
		std::uint32_t id;      // reference form id
		std::uint32_t model;   // index into the model table (lower-case, '/' separators, relative to meshes/)
		float         pos[3];  // Skyrim world units
		float         rot[9];  // row-major world rotation R = Rx(-rx) * Ry(-ry) * Rz(-rz)
		float         scale;
		std::uint32_t flags;   // bit0: 3D currently loaded
	};
	struct WLight
	{
		float pos[3];
		float col[3];
		float radius, fade, dimmer;
	};
#pragma pack(pop)
	constexpr std::size_t kWorldModelsOff = sizeof(WorldHeader);
	constexpr std::size_t kWorldRefsOff = kWorldModelsOff + std::size_t(kMaxModels) * kModelLen;
	constexpr std::size_t kWorldLightsOff = kWorldRefsOff + std::size_t(kMaxRefs) * sizeof(WRef);
	constexpr std::size_t kWorldSize = kWorldLightsOff + std::size_t(kMaxLights) * sizeof(WLight);

	// ---- Actor pose stream (third mapping): every loaded actor's skeleton (named NiNodes), ~30 Hz ----
	// Layout: ActorHeader | char boneNames[kMaxBoneNames][kBoneNameLen] | ActorPose actors[kMaxActors]
	// Seqlock like the world stream (seq odd while writing). Bone transforms are WORLD space in Skyrim units:
	// position + rotation quaternion (x,y,z,w) derived from the NiNode world rotation matrix. Bones are listed in
	// depth-first order of the actor's 3D tree, so parents precede children (ABone::parent indexes this actor's list).
	constexpr const wchar_t* kActorsName = L"Local\\SkyrimUnrealBridge_actors_v1";
	constexpr std::uint32_t kActorsMagic = 0x52544341;  // 'ACTR'
	constexpr std::uint32_t kMaxActors = 96, kMaxBones = 320, kMaxBoneNames = 512, kBoneNameLen = 40, kSkelLen = 96;
	constexpr std::uint32_t kActorIsPlayer = 1u << 0, kActorDead = 1u << 1, kActorFemale = 1u << 2, kActorWeaponDrawn = 1u << 3;
#pragma pack(push, 4)
	struct ActorHeader
	{
		std::uint32_t magic, version, seq, tick, nActors, nBoneNames, pad, pad2;
	};
	struct ABone
	{
		std::uint16_t name;     // index into the bone-name table
		std::int16_t  parent;   // index into this actor's bone list, -1 for the root
		float         pos[3];   // world position
		float         quat[4];  // world rotation x,y,z,w
	};  // 32 bytes
	struct ActorPose
	{
		std::uint32_t id;       // reference form id
		std::uint32_t baseId;   // base NPC_ form id
		std::uint32_t flags;    // kActor*
		std::uint32_t nBones;
		float         pos[3];   // reference position
		float         yaw;      // radians
		float         scale;
		char          skeleton[kSkelLen];  // race skeleton nif (lower-case, '/' separators, relative to meshes/)
		char          name[48];            // display name
		ABone         bones[kMaxBones];
	};
#pragma pack(pop)
	constexpr std::size_t kActorNamesOff = sizeof(ActorHeader);
	constexpr std::size_t kActorPosesOff = kActorNamesOff + std::size_t(kMaxBoneNames) * kBoneNameLen;
	constexpr std::size_t kActorsSize = kActorPosesOff + std::size_t(kMaxActors) * sizeof(ActorPose);

	// ---- Gear stream (fourth mapping, ~1 Hz): the armor/clothing each actor currently wears ----
	// Layout: GearHeader | ActorGear gear[kMaxActors]  (same actor order as the pose stream is NOT guaranteed: match by `id`)
	// Each path is an armor-addon model for the actor's race/sex (lower-case, '/' separators, relative to meshes/), skinned to the same skeleton.
	constexpr const wchar_t* kGearName = L"Local\\SkyrimUnrealBridge_gear_v1";
	constexpr std::uint32_t kGearMagic = 0x52414547;  // 'GEAR'
	constexpr std::uint32_t kMaxGear = 24, kGearPathLen = 112, kGearSwapLen = 200;
#pragma pack(push, 4)
	struct GearHeader
	{
		std::uint32_t magic, version, seq, tick, nActors, pad, pad2, pad3;
	};
	struct ActorGear
	{
		std::uint32_t id;      // reference form id (matches ActorPose::id)
		std::uint32_t baseId;
		std::uint32_t n;       // number of valid paths
		std::uint32_t flags;   // bit2 female (as in ActorPose)
		std::uint32_t faceId;  // NPC whose baked FaceGen head this actor uses (== baseId for named NPCs; differs for generated actors such as guards)
		std::uint32_t weaponFlags;  // bit0: right-hand item present, bit1: left-hand item present, bit2: left item is a shield (skinned armor addon)
		std::uint32_t wornSlots;    // OR of the biped slot masks of all worn armor (bit1 = Hair slot 31, bit0 = Head 30, bit11 = LongHair 41): helmets hide the baked hair
		std::uint32_t creature;     // 1 = non-humanoid (own skeleton): `paths` are the body-skin addon models of the actor/race, not worn armor
		char          paths[kMaxGear][kGearPathLen];
		char          weapons[2][kGearPathLen];  // [0] right hand, [1] left hand: model paths (weapons are rigid meshes, attach to the WEAPON / SHIELD nodes)
		char          swaps[kMaxGear][kGearSwapLen];  // per gear path: "shapeName=texture/path.dds;..." texture overrides (e.g. city guard colours on a shared armor mesh)
	};
#pragma pack(pop)
	constexpr std::size_t kGearSize = sizeof(GearHeader) + std::size_t(kMaxActors) * sizeof(ActorGear);
}
