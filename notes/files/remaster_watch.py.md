## Purpose
Runs alongside the remaster view (started by `start_bridge.py --remaster`), drawing a Skyrim-style HUD above Unreal. Shows Skyrim's interface for menus, loading screens, and the main menu while hiding Unreal.

## How it is run
The script is launched as a background process (windowless) by `start_bridge.py` when the `--remaster` flag is used. Command: `pythonw remaster_watch.py` or equivalent from project root. It's started in `start_bridge.py` at line 242 via `subprocess.Popen`.

## Inputs
- Memory-mapped file "Local\\SkyrimUnrealBridge_v1" containing packet data (versions 2 and 3)
- Packet format (version 2: `PKT_FMT`; version 3: `PKT_FMT_V3`)
- Window visibility status (whether Skyrim is the active window)
- Skyrim's position/rotation data (v[13:22] in packets)
- UI state flags (v[30] in packets)
- Health/magicka/stamina values (v[31:37] in packets)
- Activation prompt text (v[64] in version 3 packets)

## Outputs
- Transparent, click-through, always-on-top window displaying:
  - Compass showing player heading
  - Health/magicka/stamina bars (with color coding)
  - Crosshair at center of screen
  - Activation prompt text (e.g., "E Talk / Aela the Huntress")
- The window shows/hides based on game state (only visible in-world)

## Key functions
Packet.read() - Reads memory-mapped packets
Hud.frame() - Main rendering loop
Hud.draw_compass() - Draws compass
Hud.draw_bars() - Draws health bars
Hud.draw_prompt() - Draws activation prompt
Sprite.update() - Renders image to window
Sprite.show() - Shows/hides window
main() - Main control loop

## Depends on
start_bridge.py (imported for window finding)
ctypes (for Windows API access)
struct (for packet unpacking)
PIL (Image, ImageDraw, ImageFont)
sys, time (standard operations)

## Gotchas
- Previously had 64-bit HDC overflow issue fixed by adding explicit ctypes argtypes
- Can cause high memory usage (up to 53 GB PRIVATE memory in UnrealEditor)
- Requires Skyrim and UnrealEditor to be running to function
- Had terminal window issue that was fixed by using pythonw
- Crashes if Skyrim or editor closes (exits cleanly)

Source: read, not executed.
