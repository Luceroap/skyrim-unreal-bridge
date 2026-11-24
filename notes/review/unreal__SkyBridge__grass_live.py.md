# Review leads for unreal/SkyBridge/grass_live.py (UNVERIFIED)
L13 | bug | Hard-coded absolute path (AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2") | Path references user-specific directory and will break for other users/machines | Replace with relative path "area2" or config variable | high
L117 | memory | Unbounded actor growth in st["actors"] | Actors persist for all models ever loaded (never destroyed) | Destroy actors for models not in current tile set during updates | high
