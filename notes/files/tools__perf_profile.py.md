## Purpose
Switches the live Unreal Engine view to a pre-defined performance profile, adjusting rendering settings to prioritize speed over visual quality. Provides four profiles ("fast", "faster", "fastest") for different performance levels and reverts to normal settings with "everyday".

## How it is run
Command: `python tools/perf_profile.py [fast|faster|fastest|everyday]`
Called from:
- AGENT_BRIEFING.md (line 33) as example command
- tools/make_local_queue.py (line 204) as part of tool list

## Inputs
Single command-line argument: `fast`, `faster`, `fastest`, or `everyday` (defaults to `fast` if omitted).

## Outputs
- Unreal Engine console settings adjusted (session-only, reset on editor restart)
- Prints `profile applied: [level]` to console
- For `everyday`: executes `tools/max_quality.py --off`
- Attempts to destroy actors in `SkyBridge/Fire` level folder (ignores errors)

## Key functions
ue_exec
execute_console_command
get_all_level_actors

## Depends on
start_bridge
tools/max_quality.py

## Gotchas
- Settings reset immediately upon restarting Unreal editor
- All profiles except "everyday" cap frame rate at 45 FPS via `t.MaxFPS 45`
- "everyday" mode runs `tools/max_quality.py --off` to restore normal settings
- Script ignores errors when destroying actors in `SkyBridge/Fire`
- Default profile uses "fast" if no argument provided

Source: read, not executed.
