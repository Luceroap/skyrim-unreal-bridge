# C++ declarations (regex, approximate)

## plugin/src/PCH.h  (6 lines)

## plugin/src/main.cpp  (1156 lines)
- 198  namespace fs
- 286  namespace fs
- 402  namespace fs
- 507  struct WorldScratch
- 25  `CopyStr(char* dst, std::size_t cap, const char* src)`
- 39  `UiFlags(RE::PlayerCharacter* player)`
- 63  `Stat(RE::PlayerCharacter* player, RE::ActorValue av, float out[2])`
- 70  `Col(const RE::NiColor& c, float out[3])`
- 72  `SampleWeather(SkyBridge::Packet* p, RE::Sky* sky)`
- 101  `Sample()`
- 196  `AutoLoadLatestSave()`
- 217  `DumpLightsImpl()`
- 277  `SafeIterate(RE::TES* tes, RE::TESObjectREFR* origin, float radius, F* f)`
- 281  `IterateGuarded(tes, origin, radius, f, [](void* c, RE::TESObjectREFR* r)`
- 283  `DumpRefs()`
- 400  `ApplySkyCommands()`
- 459  `PumpThread()`
- 514  `NormalizeModel(const char* path)`
- 527  `IsHelperMarker(const std::string& m)`
- 540  `RotFromAngles(float rx, float ry, float rz, float out[9])`
- 555  `CollectLightsImpl(WorldScratch* s)`
- 573  `CollectLightsGuarded(WorldScratch* s)`
- 643  `ScanWorld()`
- 758  `BoneNameIndex(const char* name)`
- 773  `MatToQuat(const RE::NiMatrix3& m, float q[4])`
- 798  `CollectBones(RE::NiAVObject* o, int parent, SkyBridge::ActorPose* ap, int depth)`
- 830  `FillActorImpl(RE::Actor* a, SkyBridge::ActorPose* ap)`
- 854  `FillActorGuarded(RE::Actor* a, SkyBridge::ActorPose* ap)`
- 864  `ActorListImpl(std::vector<RE::Actor*>* out)`
- 876  `ActorListGuarded(std::vector<RE::Actor*>* out)`
- 888  `ScanActors()`
- 923  `FillGearImpl(RE::Actor* a, SkyBridge::ActorGear* g)`
- 1023  `FillGearGuarded(RE::Actor* a, SkyBridge::ActorGear* g)`
- 1033  `ScanGear()`
- 1062  `OpenGearMapping()`
- 1079  `OpenActorsMapping()`
- 1096  `OpenWorldMapping()`
- 1113  `OpenMapping()`

## shared/BridgeShared.h  (152 lines)
- 5  namespace SkyBridge
- 22  struct Packet
- 60  struct WorldHeader
- 64  struct WRef
- 73  struct WLight
- 95  struct ActorHeader
- 99  struct ABone
- 106  struct ActorPose
- 131  struct GearHeader
- 135  struct ActorGear

## unreal/SkyBridge/Source/SkyBridge/SkyBridge.cpp  (3 lines)

## unreal/SkyBridge/Source/SkyBridge/SkyBridgeGameMode.cpp  (34 lines)

## unreal/SkyBridge/Source/SkyBridge/SkyBridgeGameMode.h  (15 lines)
- 8  class ASkyBridgeGameMode

## unreal/SkyBridge/Source/SkyBridge/SkyBridgeViewLibrary.cpp  (174 lines)
- 16  struct FBoneSpaceTag
- 22  struct TRobMember
- 24  `Get(Tag)`

## unreal/SkyBridge/Source/SkyBridge/SkyBridgeViewLibrary.h  (33 lines)
- 8  class USkyBridgeViewLibrary

## unreal/SkyBridge/Source/SkyBridge/SkyrimCameraActor.cpp  (281 lines)

## unreal/SkyBridge/Source/SkyBridge/SkyrimCameraActor.h  (38 lines)
- 9  class ASkyrimCameraActor
