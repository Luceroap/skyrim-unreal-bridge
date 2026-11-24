# Review leads for unreal/SkyBridge/npc_live.py.part2 (UNVERIFIED)
L751 | perf | Sorting actors within RADIUS by distance every frame | O(n log n) operation per frame could become heavy with many actors | Replace with min-heap to track nearest MAX_NPCS actors during building | medium
L787 | perf | Building actor ID removal list from _state["actors"] | O(n) operation proportional to active actor count, which grows with gameplay | Use active set tracking during actor updates to avoid full rebuild | medium
L724 | bug | Condition `e.get("dist", 0.0) > 700` always false | Distances are capped at RADIUS (<=100m) but condition uses 700m | Remove redundant condition - poses always applied correctly | medium
L734 | robustness | Hard-coded path `os.path.join(EXPORT, "npc_%08x.fbx" % base)` | EXPORT path is global constant; changing directory breaks bridge | Store path in config with default value for user modification | low
