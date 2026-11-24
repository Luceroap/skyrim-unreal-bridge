# Review leads for unreal/SkyBridge/remaster_materials.py.part2 (UNVERIFIED)
L624 | perf | Repeated disk reads for texture lists | `_lines("decal_textures.txt")` is called per material instance | Preload file contents into sets at module level | high
L842 | robustness | Dangerous exec of local script | `exec(open(...).read(), ...)` poses security risk | Replace with direct module import | medium
L636 | bug | Silent exception swallowing | `try: ... except Exception as e: log(...)` hides critical material configuration failures | Rethrow exception or halt processing | medium
