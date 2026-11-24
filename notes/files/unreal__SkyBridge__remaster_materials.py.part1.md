## Purpose
One master material for every Skyrim surface, with per-texture material instances (MI_<key>). This replaces old per-texture materials (M_<key>), reducing shader compilation. M_SkyMaster supports wetness, snow, and special texture mappings from Skyrim.

## How it is run
Headless via UnrealEditor-Cmd.exe:  
UnrealEditor-Cmd.exe SkyBridge.uproject -run=pythonscript -script=unreal/SkyBridge/remaster_materials.py  
Called by live_bridge.py and npc_live.py (confirmed in COORDINATION.md).

## Inputs
- Texture files in area2/tex/ (color, normal, masks, linear formats)
- Hardcoded project path: C:\Users\Aidan\SkyrimUnrealBridge\area2
- Existing Unreal Engine assets and project structure

## Outputs
- Material assets in /Game/Area2/ (M_SkyMaster, M_RainCurtain, M_RainDrops, M_NightSky, M_SkyWater, M_SkyHair)
- Material instance assets (MI_<key> for each texture key)
- lodwater.fbx mesh imported at /Game/Area2/lodwater

## Key functions
master: Builds the master material graph
rain_material: Creates rain curtain material
night_sky_material: Creates night sky material
instance_for: Creates material instances from textures
configure: Sets material properties per texture type
water_material: Configures water material

## Depends on
- live_bridge.py (caller)
- npc_live.py (caller)
- water_flow_apply.py (imported for water material)
- area2/tex/ texture files (with specific naming)

## Gotchas
- Hardcoded Windows path C:\Users\Aidan\SkyrimUnrealBridge (not platform-agnostic)
- Decal textures use special alpha handling
- Foliage textures require two-sided shading model
- Snow coverage uses altitude-based calculation
- Requires exact texture naming conventions
Source: read, not executed.
