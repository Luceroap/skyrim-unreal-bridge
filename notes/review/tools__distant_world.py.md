# Review leads for tools/distant_world.py (UNVERIFIED)
L16 | cleanup | Hard-coded Skyrim data path | Path "D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data" is Windows-specific and won't work on other OS or installations. | Use an environment variable (e.g., SKYRIM_DATA_PATH) or search for Skyrim's Data directory during runtime. | high
