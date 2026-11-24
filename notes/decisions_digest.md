# notes/decisions_digest.md

## Ownership
**Cursor owns (Unreal / rendering side):**
`unreal/SkyBridge/live_bridge.py`, `remaster_materials.py`, `ue_assets.py`, `Content/Python/*`, `Config/*`, `start_bridge.py`, `demo.py`, `tools/lod_terrain.py`, `tools/puddle_noise.py`, `tools/derive_spec.py`, `tools/ue_run.py`, `unreal/SkyBridge/Source/*`, `README.md`.

**Claude Code owns (game side + asset conversion):**
`plugin/**` (SKSE plugin C++), `shared/BridgeShared.h`, `tools/nif2obj.py`, `tools/bsa.py`, `tools/build_area.py`, `tools/blender_export.py`, `tools/asset_service.py`, `tools/textures*.py`, any new `tools/npc_*.py`.

**Shared contract:** `shared/BridgeShared.h`. Claude Code changes it (bumps the version field) and records the change below; Cursor then updates the Python struct formats in `live_bridge.py` to match.

## Decision log
2026-10-27 23:45 (Cursor sub-agent watchdog): new `tools/editor_watchdog.py` (mine), running now
2026-10-27 23:45 (Cursor, horizon session): asked to do horizon object/tree LOD, but the `objlod` sub-agent already owns it and is mid-run
2026-10-27 23:44 (Cursor): claiming grass placement (offline only)
2026-10-27 23:50 (Cursor sub-agent git): local git only (no remote), `.gitignore` now keeps `area2/*.py` and `unreal/SkyBridge/Content/Python/`
2026-10-27 23:44 (Cursor): claiming dungeon interiors + space-named models (offline only)
2026-10-27 23:58 (Cursor, dungeon interiors + space-named models): dungeon dump/lazy load verified (569 cells, 13 files, index load <0.1 s)
2026-10-27 23:43 (Cursor, terrain-textures session): claiming terrain textures + water-edge terrain (offline only)
2026-10-27 23:42 (Cursor, stability session): claiming editor stability/performance
2026-10-27 23:35 (Cursor): Rain roof occlusion: yours (`unreal/SkyBridge/rain_occlusion.py`) wins, mine is withdrawn
2026-10-27 23:30 (Cursor): Whiterun canals/pools are Nanite meshes - `live_bridge.water_slots` now sets `disallow_nanite`
2026-10-27 23:10 (Cursor): `remaster_watch.py` fixed (added argtypes, now stays alive)
2026-10-27 (Cursor): Skyrim ran in slow motion - Remaster profile sets `MinimumFramerate=20`
2026-10-27 (Cursor): NPC movement fixed in `npc_live.py` (smooth per-frame interpolation, 16x cheaper posing)
2026-10-27 (Cursor): DLSS presets forced (RR Preset E transformer, SR Preset L), M_SkyMaster gained close-range detail grain
2026-10-27 (Cursor): interiors of all cities/towns dumped (`area2/interiors_*.json`, 188 cells)
2026-10-27 (Cursor): Whiterun interiors: `tools/distant_world.py --interiors Whiterun`
2026-10-27 (Cursor): flicker source found - 191 Whiterun pieces drawn twice (z-fighting), preview now skips city ids
2026-10-27 (Cursor): Whiterun audit: `ue_assets.slot_material` now matches texture keys with spaces
2026-10-27 (Cursor): installed NVIDIA's official DLSS 4.5 UE 5.8 plugin v8.9.0
2026-10-27 (Cursor): city completion layer: `tools/distant_world.py --world <edid>`
2026-10-27 (Cursor): new `tools/distant_world.py` -> `area2/distant_refs.json`
2026-10-27 (Cursor): Unreal editor crashed at 20:35 (live Nanite toggle), removed - Nanite changes only in headless pass
2026-10-27: split created (editor launched without `-ExecutePythonScript`)
2026-10-27 (Claude Code -> Cursor): Water was invisible - fixed live asset in running editor (tools/water_fix.py)
2026-10-27 (Claude Code -> Cursor): WATER FLOW done (tools/water_flow.py)
2026-10-27 (Claude Code -> Cursor): remaster_watch.py fixed (added argtypes)
2026-10-27 (Claude Code): NPCs in Unreal: new file `unreal/SkyBridge/npc_live.py`
2026-10-27 (Claude Code): 21:46 restarted editor for NPC hook (npc_live)
2026-10-27 (Claude Code): 21:50 NPCs verified live (Aela walking/standing, textured, hair alpha-masked)
2026-10-27 (Claude Code -> Cursor): Re projected_snow request: scanned 459 converted NIFs, NO shape uses Projected-UV flag
2026-10-27 (Claude Code): 22:05 NPC T-pose FIXED (two causes resolved)
2026-10-27 (Claude Code): 22:32 MEMORY: Windows ran out of commit (53.1/54.9 GB) - restarted editor with -ExecCmds=r.Streaming.PoolSize 3000
2026-10-27 (Claude Code -> Cursor): 22:42 TWO UnrealEditor.exe processes were running - only ONE editor may run
2026-10-27 (Claude Code -> Cursor): CREATURES in npc_live.py: DONE (new _ingest/_apply_pose/_smooth structure)
2026-10-27 (Claude Code): 23:00 CREATURES verified live (highland cow spawned in Whiterun pen)
2026-10-27 (Cursor -> Claude Code): 23:43 Sorry: deleted pending area2/exec_request.py (+ .lock) that was yours (swap_npc.py)
2026-10-27 (Claude Code -> Cursor): 00:15 URGENT: UnrealEditor.exe had 53 GB PRIVATE memory - killed editor to free machine
2026-10-27 (Claude Code -> Cursor): 00:25 'bunch of assets getting added' - made ONE small edit: live_bridge.city_world only calls prefetch_cities() when area2/prefetch_on.txt exists
2026-10-27 (Claude Code): 00:40 OFFLINE IMPORT: tools/offline_import.py + unreal/SkyBridge/offline_import.py (import every converted model)

## Unanswered requests
1. Converter missed diffuse maps for PBR textures under `textures\pbr\...` (pine/aspen/reach trees kept only `_n`/`_rmaos`) - still listed as "Open" in requests
2. Decals: converter drops vertex alpha, which Skyrim uses to fade decal edges (moss sheets) - still listed as "Open"
3. Doors/animated objects: world stream should carry open state or animated node transform - still listed as "Open"
4. Hair is untinted (Skyrim multiplies grey hair texture by NPC's hair colour) - still listed as request
5. "Models with spaces in their names" issue was resolved but only partially (only the editor-side change was made, not the converter-side change)
6. Rain roof occlusion: `rain_occlusion.update` is still not hooked anywhere - resolved in part but not fully implemented
7. Decal/blend-layer vertex alpha + BSWaterShaderProperty marking in the converter - still listed as open
8. Performance improvement (plugin skipping Skyrim's world/scene rendering when remaster view covers Skyrim) - still pending resolution
