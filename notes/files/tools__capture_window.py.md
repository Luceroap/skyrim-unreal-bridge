## Purpose
Captures the visible contents of a window (e.g., Skyrim's game window) even when obscured by other windows, using Windows API `PrintWindow`. Designed for use in the Skyrim-to-Unreal bridge to extract visual data for further processing.

## How it is run
Command line: `python capture_window.py <exe> <out.png>`. Called by `HANDOFF_FOR_CURSOR.md` (line 138) as part of the project's workflow.

## Inputs
- First argument: Exact process name matching the target window (e.g., `Skyrim`).
- Second argument: Output filename (e.g., `capture.png`).

## Outputs
- PNG image file saved at specified path (e.g., `capture.png`), containing RGB pixel data.

## Key functions
find_window - Finds window handle by process name  
GetWindowRect - Retrieves window dimensions  
PrintWindow - Captures window contents to device context  
CreateCompatibleBitmap - Creates memory-compatible bitmap  
GetBitmapBits - Extracts pixel data from bitmap  
Image.frombuffer - Converts raw pixel data to image

## Depends on
- `start_bridge.py` (for `find_window`)
- `PIL.Image` (for image processing)

## Gotchas
- Minimized windows cannot be captured (window must be visible).
- Output image is saved as RGB (not RGBA).
- Hardcoded project path `C:\Users\Aidan\SkyrimUnrealBridge` may fail if directory structure changes.
- Requires Windows OS (uses `ctypes.windll` and Windows API).
- `PrintWindow` flag `2` captures only visible window content (may fail for some window types).

Source: read, not executed.
