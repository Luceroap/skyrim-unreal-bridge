# Functions

| Function | Line | Description | Thread |
|----------|------|-------------|--------|
| CopyStr | N/A | Copies string with size limit | main thread |
| UiFlags | N/A | Computes UI flags from menus and player state | main thread |
| Stat | N/A | Computes actor value statistics (current/permanent) | main thread |
| Col | N/A | Converts NiColor to RGB float array | main thread |
| SampleWeather | N/A | Samples weather data from current sky | main thread |
| Sample | N/A | Collects player/camera/weather state to shared memory packet | main thread (via SKSE task) |
| AutoLoadLatestSave | N/A | Loads latest save game on flag file | main thread |
| DumpLightsImpl | N/A | Dumps active lights to file | main thread |
| GuardedCall | N/A | Wraps function call in SEH exception handling | main thread |
| IterateImpl | N/A | Iterates references in radius | main thread |
| IterateGuarded | N/A | Iterates with SEH exception handling | main thread |
| SafeIterate | N/A | Safely iterates references with SEH | main thread |
| DumpRefs | N/A | Dumps references and lights to files | main thread |
| AutoLoadRetryThread | N/A | Retries save load from main menu in separate thread | separate thread |
| ApplySkyCommands | N/A | Applies sky commands from file | main thread |
| ScanWorld | N/A | Scans live world to world shared memory | main thread (via SKSE task) |
| ScanActors | N/A | Scans actors to actor shared memory | main thread (via SKSE task) |
| ScanGear | N/A | Scans worn gear to gear shared memory | main thread (via SKSE task) |
| PumpThread | N/A | Schedules periodic tasks (main pump thread) | separate thread (detached) |
| NormalizeModel | N/A | Normalizes model paths (lowercase, '/' separators) | main thread |
| IsHelperMarker | N/A | Checks if model is invisible helper marker | main thread |
| RotFromAngles | N/A | Converts Euler angles to rotation matrix | main thread |
| CollectLightsImpl | N/A | Collects active lights for world stream | main thread |
| CollectLightsGuarded | N/A | Collects lights with SEH exception handling | main thread |
| IterateCellImpl | N/A | Iterates references in cell | main thread |
| GridCellGuarded | N/A | Guards grid cell iteration | main thread |
| InteriorCellGuarded | N/A | Guards interior cell iteration | main thread |
| WorldExtraRefsImpl | N/A | Collects extra references from worldspace | main thread |
| WorldExtraRefsGuarded | N/A | Guards extra reference collection | main thread |
| BoneNameIndex | N/A | Maps bone names to indices | main thread |
| MatToQuat | N/A | Converts rotation matrix to quaternion | main thread |
| CollectBones | N/A | Collects bone transforms from actor 3D tree | main thread |
| FillActorImpl | N/A | Fills actor pose structure with data | main thread |
| FillActorGuarded | N/A | Fills actor with SEH exception handling | main thread |
| ActorListImpl | N/A | Lists actors in active cell | main thread |
| ActorListGuarded | N/A | Guards actor list collection | main thread |
| OpenGearMapping | N/A | Opens gear shared memory mapping | main thread |
| OpenActorsMapping | N/A | Opens actors shared memory mapping | main thread |
| OpenWorldMapping | N/A | Opens world shared memory mapping | main thread |
| OpenMapping | N/A | Opens all shared memory mappings | main thread |
| SKSEPluginLoad | N/A | Plugin entry point (registers event listener) | main thread |

# Shared-Memory Blocks

- **World stream**: `SkyBridge::kWorldName` (mapped at `g_world`, used for live world data)
- **Actor stream**: `SkyBridge::kActorsName` (mapped at `g_actors`, used for actor poses)
- **Gear stream**: `SkyBridge::kGearName` (mapped at `g_gear`, used for worn gear data)
- **Packet**: `SkyBridge::kMappingName` (mapped at `g_packet`, main game state buffer)

# Files Read and Written

## Files Read
- `Data/SKSE/Plugins/SkyrimUnrealBridge.autoload`
- `Data/SKSE/Plugins/SkyrimUnrealBridge.autodump`
- `Data/SKSE/Plugins/SkyrimUnrealBridge.dump`
- `Data/SKSE/Plugins/SkyrimUnrealBridge.sky`

## Files Written
- `Data/SKSE/Plugins/SkyrimUnrealBridge.sky.out` (sky command results)
- `SkyrimUnrealBridge_lights.tsv` (in SKSE log directory)
- `SkyrimUnrealBridge_refs_all.tsv` (in SKSE log directory, cumulative)
- `SkyrimUnrealBridge_centers.txt` (in SKSE log directory, dump positions)
