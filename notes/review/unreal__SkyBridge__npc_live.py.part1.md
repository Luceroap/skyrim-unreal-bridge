# Review leads for unreal/SkyBridge/npc_live.py.part1 (UNVERIFIED)
L346-349 | memory | Unbounded mesh cache grows without bound | Eventually exhausts memory with many NPCs | Implement LRU cache with max size (e.g., 100) | high
L190-191 | perf | Repeated directory existence check | Causes repeated disk I/O per slot | Cache directory existence check | medium
L194-195 | perf | Repeated directory scan for texture in `_png_for_slot` | Causes repeated disk I/O per slot per actor | Cache texture lookup per slot | medium
L319-327 | perf | Synchronous asset import on main thread | Causes frame hitches when NPCs first appear | Use background import or async import | medium
