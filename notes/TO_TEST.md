# To test in game (for Agent 1)

Written 2026-11-04 by the Cursor materials session. Nothing below has been seen on screen: this session wrote code and data
only (no Skyrim, no UnrealEditor). Tick items off or note what you saw under each one, then add a line to `AGENT_LOG.md`.

## What changed (short)
- `M_SkyMaster` gained per-material parameters: `RoughnessMatte`/`RoughnessGloss` (replace the fixed 0.9/0.3 from the spec mask),
  `DetailRoughness`, `Metalness` (x spec mask), `Specular`, `ClothFuzz`, `BaseTint`, `SubsurfaceTint` (was a fixed constant),
  `WetResponse`, `Puddles`, `SnowCover`, and a second detail layer (`DetailNormalMap2`/`DetailColorMap2`/`DetailTiling2`/
  `DetailSplit`, static switch `SpecMaskedDetail`) blended in where Skyrim's spec mask is high (metal plates, studs, buckles).
  World defaults reproduce the old look exactly.
- Every NPC/creature texture gets a material kind (`unreal/SkyBridge/npc_material_types.py`): cloth, fur, leather,
  leather_armor, metal_armor, jewelry, skin, skin_beast, eye, mouth, hair, creature_fur/hide/skin/scale, chitin, bone,
  creature_metal. Each kind has its own roughness range, metalness, specular, detail texture, shading model and weather response.
- New detail textures in `area2/tex`: `leatherdetail`, `metaldetail`, `skindetail` (+ `_n`), from `tools/leather_detail.py`,
  `tools/metal_detail.py`, `tools/skin_detail.py` (fabric stays `tools/fabric_detail.py`).
- Eyes: opaque, glossy (roughness 0.04-0.06), no detail grain, slightly darkened (`BaseTint` 0.9). Before, they went through
  `npc_hair` and were two-sided foliage cut-outs with clip 0.4.
- Skin: subsurface profile asset `SP_SkySkin` (beast races `SP_SkySkinBeast`), pore detail, skin roughness/specular, no snow,
  only light wet darkening. Mouth: wet, glossy, darker.
- Hair (`M_SkyHair` is rebuilt in place once): per-strand brightness and roughness variation, `Backlit` 0.6. Brow/lash cards on
  M_SkyMaster get a warm transmission tint instead of the green foliage one.
- Cloth and fur use UE's Cloth shading model (sheen). Body parts never get puddles (`Puddles` 0).

## How to load it
The first `npc_live` material pass after this edit rebuilds M_SkyMaster and M_SkyHair once (shader compile: expect a hitch of
roughly a minute), then re-applies every NPC material because the `remaster_materials.py` stamp changed.
1. Before launching: `python tools/npc_material_coverage.py`. It must print `self-test: ... OK` and `0 missing detail textures`.
2. Launch the normal way (play.py). Watch the editor log for `[SkyMaterials] upgrading M_SkyMaster graph`, `built M_SkyMaster`,
   `upgrading M_SkyHair graph`, and for any `npc material ... failed`, `subsurface profile`, or `detail texture ... missing` lines.
   Please paste any of those into AGENT_LOG.
3. If the master fails to compile, the material shows the default grey checker: send me the shader error from the log.

## Checks (Whiterun, daytime first, then overcast/rain, then night with a torch)
1. **World unchanged.** Roads, walls, rocks, wet puddles and snow on mountains look exactly as before (defaults reproduce the
   old graph). Any change on non-NPC surfaces is a bug.
2. **Eyes.** Close up on Aela, Ysolda, Olfina (anuketh eyes) and a vanilla-eyed NPC (Sigurd, Jon): eyes solid (no see-through
   holes or black patches), small sharp highlight from the sun or a torch, whites not glowing.
3. **Skin.** Faces and hands: soft light bleeding at the shadow edge, red-ish glow through ears against the sun, fine pores
   only within ~3 m. Not waxy, not plastic. Note whether `SP_SkySkin` exists in /Game/Area2Tex (if it does not, the log line
   says why and skin falls back to the engine default profile; still fine).
4. **Leather vs cloth vs metal**, side by side:
   - Cloth (farm clothes, robes, Ysolda's dress): woven texture up close, matte, soft sheen at grazing angles.
   - Leather (boots, gloves, belts; hide armor on guards / Aela): pebbled grain and creases, semi-gloss.
   - Metal (iron armor, steel helmets, draugr armor): metal plates reflective and clearly different from the leather straps
     on the same piece; hammer marks and scratches up close.
   - Amulets (Mara amulet on NPCs that have it): shiny metal.
5. **Hair.** Hair-tinted NPCs (Jenassa, Lillith): strands vary a little in brightness, rim glow when backlit by the sun, no
   flat dyed look. Brows/lashes: no green tint in backlight.
6. **Weather.** In rain: cloth darkens strongly, leather a bit, skin barely, **no mirror puddles or ripple rings on heads,
   shoulders or hoods**. In snowfall: some snow on shoulders/hoods, none on faces or eyes.
7. **Creatures.** Highland cow (Whiterun pen): matte fur with soft sheen. Dragon (if one spawns): scaly, semi-gloss, snow on
   its back in snow weather. Skeleton: dry bone, not shiny.
8. **Performance.** Note NPC tick and frame time before/after if you have numbers; armor with `SpecMaskedDetail` samples two
   extra textures.

## Known gaps (data, not material code)
From `python tools/npc_material_coverage.py`:
- The Mara amulet appears in the gear stream for 0001a692, 0001a6d7, 000b9982 but is not in their built meshes (npc_build drops it).
- 8 armor textures have no `_s` spec map (studded armor, `f_/m_cuirasslight`, Whiterun Stormcloak cuirass/helm). They get one
  leather layer and no metalness, so studs and buckles stay matte. Restore the spec maps and the metal/leather split works.
- 25 aliased gear textures (`farmclothes03_torsof_d`, `merchantclothes_bootsm_d`, ...) have no `_n`. `tools/npc_tex_alias.py`
  only renames the diffuse map, so these pieces lose their normal maps.
- The draugr skeleton is extracted but no draugr mesh is built yet.
