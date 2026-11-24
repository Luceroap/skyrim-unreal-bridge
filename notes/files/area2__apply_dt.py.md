## Purpose
Applies display-related tweaks to Skyrim's configuration by merging new settings into a backup profile. Modifies the main display settings file while preserving existing configurations not explicitly overridden.

## How it is run
Command line: `python apply_dt.py`  
No other files found to call it (git grep output contained no matches).

## Inputs
- `sb.DISPLAY_TWEAKS` (path to `SSEDisplayTweaks.ini`)
- `sb.PROFILE_BACKUP` (path to JSON backup file)
- `sb.REMASTER_PROFILE[sb.DISPLAY_TWEAKS]` (new settings dictionary)

## Outputs
- Timestamped backup of `SSEDisplayTweaks.ini` (e.g., `SSEDisplayTweaks.ini.20231005-123456`)
- Updated JSON profile backup file at `sb.PROFILE_BACKUP`
- Prints lines matching `MinimumFramerate`, `FramerateLimit=`, or `DynamicMaxTimeScaling` from the original config

## Key functions
sb.set_ini - Modifies INI file settings  
json.load - Reads profile backup JSON  
json.dump - Writes updated profile backup  
shutil.copy2 - Creates timestamped file backup  
print - Verifies config lines before modification

## Depends on
- `start_bridge.py` (imports as `sb` for path variables and helper functions)

## Gotchas
- Creates timestamped backups in the same directory as the profile backup
- Only applies new settings not already present in the original config
- Verifies specific framerate-related lines before applying changes
- Updates the JSON profile backup atomically
- Relies entirely on `sb.set_ini` for INI file modification

Source: read, not executed.
