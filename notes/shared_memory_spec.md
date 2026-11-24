# Shared Memory Specification

## Shared Mappings

| Name                                     | Struct      | Writer         | Reader | Update Rate |
|------------------------------------------|-------------|----------------|--------|-------------|
| `Local\\SkyrimUnrealBridge_v1`           | `Packet`    | SKSE plugin    | Unreal | Frame rate  |
| `Local\\SkyrimUnrealBridge_world_v1`     | `WorldHeader` | SKSE plugin    | Unreal | ~1 Hz       |
| `Local\\SkyrimUnrealBridge_actors_v1`    | `ActorPose` | SKSE plugin    | Unreal | ~30 Hz      |
| `Local\\SkyrimUnrealBridge_gear_v1`      | `ActorGear` | SKSE plugin    | Unreal | ~1 Hz       |

## Packet Struct Fields

| Name                  | Type                  | Size (bytes) | Meaning                                 | Offset (computed - verify) |
|-----------------------|-----------------------|--------------|-----------------------------------------|----------------------------|
| magic                 | `uint32_t`            | 4            | Magic number 'SKUB'                     | 0                          |
| version               | `uint32_t`            | 4            | Schema version (3)                      | 4                          |
| seq                   | `uint32_t`            | 4            | Sequence number (odd = writer busy)     | 8                          |
| frame                 | `uint32_t`            | 4            | Frame counter                           | 12                         |
| playerPos             | `float[3]`            | 12           | Player position (X, Y, Z)               | 16                         |
| playerAngle           | `float[3]`            | 12           | Pitch, roll, yaw (radians)              | 28                         |
| camPos                | `float[3]`            | 12           | Camera position (X, Y, Z)               | 40                         |
| camRot                | `float[9]`            | 36           | Camera rotation matrix (row-major)      | 52                         |
| fovDeg                | `float`               | 4            | Field of view (degrees)                 | 88                         |
| gameHour              | `float`               | 4            | Current time of day (0-24)              | 92                         |
| gameDays              | `float`               | 4            | Total days passed                       | 96                         |
| weatherFormID         | `uint32_t`            | 4            | Weather form ID                         | 100                        |
| cellFormID            | `uint32_t`            | 4            | Cell form ID                            | 104                        |
| weatherEditorID       | `char[64]`            | 64           | Weather editor ID (e.g., "Clear")       | 108                        |
| cellName              | `char[64]`            | 64           | Current cell name                       | 172                        |
| worldspaceName        | `char[64]`            | 64           | Current worldspace name                 | 236                        |
| uiFlags               | `uint32_t`            | 4            | UI state flags                          | 300                        |
| health                | `float[2]`            | 8            | Current/max health                      | 304                        |
| magicka               | `float[2]`            | 8            | Current/max magicka                     | 312                        |
| stamina               | `float[2]`            | 8            | Current/max stamina                     | 320                        |
| rain                  | `float`               | 4            | Rain intensity                          | 328                        |
| snow                  | `float`               | 4            | Snow intensity                          | 332                        |
| cloudy                | `float`               | 4            | Cloudiness                              | 336                        |
| pleasant              | `float`               | 4            | Pleasantness (weather blend)            | 340                        |
| weatherPct            | `float`               | 4            | Weather transition percentage           | 344                        |
| lastWeatherFormID     | `uint32_t`            | 4            | Last weather form ID                    | 348                        |
| sunPos                | `float[3]`            | 12           | Sun position (X, Y, Z)                  | 352                        |
| sunColor              | `float[3]`            | 12           | Sun color (R, G, B)                     | 364                        |
| ambientColor          | `float[3]`            | 12           | Ambient color (R, G, B)                 | 376                        |
| fogColor              | `float[3]`            | 12           | Fog color (R, G, B)                     | 388                        |
| skyUpper              | `float[3]`            | 12           | Sky upper color (R, G, B)               | 400                        |
| horizon               | `float[3]`            | 12           | Horizon color (R, G, B)                 | 412                        |
| fogNear               | `float`               | 4            | Near fog distance                       | 424                        |
| fogFar                | `float`               | 4            | Far fog distance                        | 428                        |
| windSpeed             | `float`               | 4            | Wind speed                              | 432                        |
| crosshair             | `char[64]`            | 64           | Crosshair target (e.g., "Talk\tSigurd") | 436                        |

## WorldHeader Struct Fields

| Name      | Type           | Size (bytes) | Meaning                       | Offset (computed - verify) |
|-----------|----------------|--------------|-------------------------------|----------------------------|
| magic     | `uint32_t`     | 4            | Magic number 'WRLD'           | 0                          |
| version   | `uint32_t`     | 4            | Schema version (3)            | 4                          |
| seq       | `uint32_t`     | 4            | Sequence number (odd = writer busy) | 8                         |
| tick      | `uint32_t`     | 4            | Game tick counter             | 12                         |
| nRefs     | `uint32_t`     | 4            | Number of references          | 16                         |
| nModels   | `uint32_t`     | 4            | Number of models              | 20                         |
| nLights   | `uint32_t`     | 4            | Number of lights              | 24                         |
| pad       | `uint32_t`     | 4            | Padding                       | 28                         |

## WRef Struct Fields

| Name   | Type             | Size (bytes) | Meaning                                  | Offset (computed - verify) |
|--------|------------------|--------------|------------------------------------------|----------------------------|
| id     | `uint32_t`       | 4            | Reference form ID                        | 0                          |
| model  | `uint32_t`       | 4            | Index into model table                   | 4                          |
| pos    | `float[3]`       | 12           | Position (X, Y, Z)                       | 8                          |
| rot    | `float[9]`       | 36           | Rotation matrix (row-major)              | 20                         |
| scale  | `float`          | 4            | Scale factor                             | 56                         |
| flags  | `uint32_t`       | 4            | 3D loaded (bit0)                         | 60                         |

## WLight Struct Fields

| Name      | Type             | Size (bytes) | Meaning                      | Offset (computed - verify) |
|-----------|------------------|--------------|------------------------------|----------------------------|
| pos       | `float[3]`       | 12           | Light position (X, Y, Z)     | 0                          |
| col       | `float[3]`       | 12           | Light color (R, G, B)        | 12                         |
| radius    | `float`          | 4            | Light radius                 | 24                         |
| fade      | `float`          | 4            | Fade intensity               | 28                         |
| dimmer    | `float`          | 4            | Dimmer intensity             | 32                         |

## ActorHeader Struct Fields

| Name        | Type           | Size (bytes) | Meaning                       | Offset (computed - verify) |
|-------------|----------------|--------------|-------------------------------|----------------------------|
| magic       | `uint32_t`     | 4            | Magic number 'ACTR'           | 0                          |
| version     | `uint32_t`     | 4            | Schema version (3)            | 4                          |
| seq         | `uint32_t`     | 4            | Sequence number (odd = writer busy) | 8                         |
| tick        | `uint32_t`     | 4            | Game tick counter             | 12                         |
| nActors     | `uint32_t`     | 4            | Number of actors              | 16                         |
| nBoneNames  | `uint32_t`     | 4            | Number of bone names          | 20                         |
| pad         | `uint32_t`     | 4            | Padding                       | 24                         |
| pad2        | `uint32_t`     | 4            | Padding                       | 28                         |

## ABone Struct Fields

| Name    | Type             | Size (bytes) | Meaning                             | Offset (computed - verify) |
|---------|------------------|--------------|-------------------------------------|----------------------------|
| name    | `uint16_t`       | 2            | Index into bone-name table          | 0                          |
| parent  | `int16_t`        | 2            | Parent bone index (-1=root)         | 4                          |
| pos     | `float[3]`       | 12           | Position (X, Y, Z)                  | 8                          |
| quat    | `float[4]`       | 16           | Rotation quaternion (x, y, z, w)    | 20                         |

## ActorPose Struct Fields

| Name           | Type                     | Size (bytes) | Meaning                                  | Offset (computed - verify) |
|----------------|--------------------------|--------------|------------------------------------------|----------------------------|
| id             | `uint32_t`               | 4            | Actor form ID                            | 0                          |
| baseId         | `uint32_t`               | 4            | Base NPC form ID                         | 4                          |
| flags          | `uint32_t`               | 4            | Actor state (kActor*)                    | 8                          |
| nBones         | `uint32_t`               | 4            | Number of bones                          | 12                         |
| pos            | `float[3]`               | 12           | Reference position (X, Y, Z)             | 16                         |
| yaw            | `float`                  | 4            | Rotation yaw (radians)                   | 28                         |
| scale          | `float`                  | 4            | Scale factor                             | 32                         |
| skeleton       | `char[96]`               | 96           | Race skeleton NIF path                   | 36                         |
| name           | `char[48]`               | 48           | Display name                             | 132                        |
| bones          | `ABone[kMaxBones]`       | 10240        | Bone transforms (320 bones * 32 bytes)   | 180                        |

## GearHeader Struct Fields

| Name      | Type           | Size (bytes) | Meaning                       | Offset (computed - verify) |
|-----------|----------------|--------------|-------------------------------|----------------------------|
| magic     | `uint32_t`     | 4            | Magic number 'GEAR'           | 0                          |
| version   | `uint32_t`     | 4            | Schema version (3)            | 4                          |
| seq       | `uint32_t`     | 4            | Sequence number (odd = writer busy) | 8                         |
| tick      | `uint32_t`     | 4            | Game tick counter             | 12                         |
| nActors   | `uint32_t`     | 4            | Number of actors              | 16                         |
| pad       | `uint32_t`     | 4            | Padding                       | 20                         |
| pad2      | `uint32_t`     | 4            | Padding                       | 24                         |
| pad3      | `uint32_t`     | 4            | Padding                       | 28                         |

## ActorGear Struct Fields

| Name            | Type                         | Size (bytes) | Meaning                                      | Offset (computed - verify) |
|-----------------|------------------------------|--------------|----------------------------------------------|----------------------------|
| id              | `uint32_t`                   | 4            | Actor form ID                                | 0                          |
| baseId          | `uint32_t`                   | 4            | Base NPC form ID                             | 4                          |
| n               | `uint32_t`                   | 4            | Number of valid paths                        | 8                          |
| flags           | `uint32_t`                   | 4            | Actor flags (kActor*)                        | 12                         |
| faceId          | `uint32_t`                   | 4            | FaceGen head form ID                         | 16                         |
| weaponFlags     | `uint32_t`                   | 4            | Weapon presence flags                        | 20                         |
| wornSlots       | `uint32_t`                   | 4            | Worn slot mask (biped slots)                 | 24                         |
| creature        | `uint32_t`                   | 4            | 1 = non-humanoid (owns skeleton)             | 28                         |
| paths           | `char[kMaxGear][kGearPathLen]` | 2688        | Armor/clothing model paths                   | 32                         |
| weapons         | `char[2][kGearPathLen]`      | 224          | Weapon paths (right, left)                   | 2720                       |
| swaps           | `char[kMaxGear][kGearSwapLen]` | 4800         | Texture override data (e.g., colors)         | 2944                       |

## Python Files Reading Mappings

| Mapping Name                             | Python Files (Readers)                                                                 |
|------------------------------------------|--------------------------------------------------------------------------------------|
| `Local\\SkyrimUnrealBridge_v1`           | area2/probe_player.py, area2/probe_state.py, play.py, remaster_watch.py, start_bridge.py, tools/debug/walk_check.py, tools/debug/walk_check_lib.py, tools/read_bridge.py, unreal/SkyBridge/live_bridge.py |
| `Local\\SkyrimUnrealBridge_world_v1`     | tools/read_world.py, tools/stream_coverage.py, unreal/SkyBridge/live_bridge.py        |
| `Local\\SkyrimUnrealBridge_actors_v1`    | area2/npc_live_before_cursor.py, area2/npc_live_before_cursor_frozen.py, tools/npc_batch.py, tools/read_actors.py, unreal/SkyBridge/npc_live.py |
| `Local\\SkyrimUnrealBridge_gear_v1`      | area2/npc_live_before_cursor.py, area2/npc_live_before_cursor_frozen.py, tools/npc_batch.py, tools/read_gear.py, unreal/SkyBridge/npc_live.py |
