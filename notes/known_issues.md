# Known Issues

| issue | where stated | status | suggested owner |
|-------|--------------|--------|-----------------|
| Camera motion mirroring: exact axis direction/scale not measured | README.md | open | Unreal python |
| Doors still do not open in Unreal (nif animation, not streamed) | README.md | open | plugin |
| Models failing to convert: `genericbannerred01`, `hangingrabbit01`, `spelltomerestorationlowpoly`, `basicbook05` | README.md | open | converter |
| Plugin drops "marker" models (e.g., craft stations like `furniture/blacksmithforgemarkerwr.nif`) | COORDINATION.md | open | plugin |
| Converter misses PBR diffuse maps for NPC textures (pine/aspen/reach trees) | COORDINATION.md | open | converter |
| Converter drops vertex alpha for decals (moss sheets fade edges incorrectly) | COORDINATION.md | open | converter |
| Models with spaces in names (e.g., `clutter/dining set/x.nif`) cause import failures | COORDINATION.md | open | converter |
| projected_snow.txt missing (no real data for snow on terrain) | COORDINATION.md | open | converter |
| Tree LOD for distant trees (billboards at horizon) not implemented | COORDINATION.md | open | converter |
| NPC hair tint (Skyrim's hair color not applied to textures) | COORDINATION.md | open | converter |
| Facial animation data (lip sync, expression/morph weights) not streamed | COORDINATION.md | open | plugin |
| Rain roof occlusion (`rain_occlusion.update` not hooked) | COORDINATION.md | open | Unreal python |
