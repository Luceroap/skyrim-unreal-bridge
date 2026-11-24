# Review leads for tools/asset_service.py (UNVERIFIED)
L29 | perf | repeated disk reads of requests.txt | reads full file every loop iteration causing redundant I/O | use file seek/tail or incremental tracking | high
L50 | memory | unbounded 'done' set growth | 'done' set grows indefinitely without cleanup | persist to disk or prune historical entries | high
L7 | bug | hard-coded Steam path | assumes Skyrim at D:\SteamLibrary\... | use config/environment variable | medium
L48 | bug | hard-coded Blender path | assumes Blender at D:\blender.exe | use system PATH or config | medium
