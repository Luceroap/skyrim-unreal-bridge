# Review leads for tools/tamriel_terrain.py (UNVERIFIED)
L34 | robustness | hard-coded Blender path | the path "D:\\blender.exe" is not portable and will fail on non-Windows systems or if Blender is installed elsewhere | use an environment variable or a configuration | low
L180 | memory | unbounded cache for texture images in `Baker.src` | `src` cache grows without bound, potentially using all memory for large texture sets | limit cache size with `collections.OrderedDict` and maxsize | medium
L321 | perf | repeated disk read for whiterun_cells() | called per chunk, but the file is static during the run | cache the result | medium
