## Purpose
Enables mountain haze/cloud bands and night sky effects (moons, planets, aurora) in Unreal's live view. Configurable strength for haze; automatically activates at night or when forced via 'night' mode.

## How it is run
Command line: `python tools/sky_extras.py on [strength]`, `python tools/sky_extras.py night`, or `python tools/sky_extras.py off`. Referenced in `AGENT_BRIEFING.md` as a valid user command.

## Inputs
- `mode` (string): `on`, `night`, or `off`
- `strength` (float, optional): 0.0–2.0 (default 1.0)

## Outputs
Console messages (e.g., "bodies removed") and modifies Unreal Engine live session via UE code; no files or folders written.

## Key functions
mountain_mist.apply
mountain_mist.off
night_sky.apply
night_sky.remove

## Depends on
start_bridge (for `ue_exec`), `unreal/SkyBridge/mountain_mist.py`, `unreal/SkyBridge/night_sky.py`

## Gotchas
- Session-only; requires restarting the Unreal editor to reset.
- 'night' mode activates when time override is outside 5.5–20.5 hours (5:30AM–8:30PM).
- Strength defaults to 1.0 if not provided.
- 'off' mode removes moons/planets via `night_sky.remove()`.
- Uses `live._sky_override[0]` for night detection when override is active.

Source: read, not executed.
