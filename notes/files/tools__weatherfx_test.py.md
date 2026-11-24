## Purpose
Live test driver for weather effects in the Skyrim-Unreal bridge project. Allows temporary modification of weather parameters (snow, rain, wind) and control of the weather system state via MODE settings.

## How it is run
Command: `python tools/ue_run.py tools/weatherfx_test.py 120`. The only file calling it is `ue_run.py` (confirmed via `git grep` with no other file references).

## Inputs
- `MODE`: String ("on", "off", or "rebuild")
- `FORCE`: Dictionary with keys `snow`, `rain`, `wind` (e.g., `{"snow": 1.0, "rain": None, "wind": 0.3}`)

## Outputs
- Console messages (e.g., "test tick on, FORCE { ... }")
- Updates to Unreal's weather system via the `live` instance
- Clears weather system state when `MODE = "off"`

## Key functions
weather_fx.clear
weather_fx.build
weather_fx.install_test_tick
importlib.reload

## Depends on
weather_fx.py
unreal (Unreal Engine module)

## Gotchas
- Rain set to `None` uses Skyrim's weather system instead of test value
- `MODE = "off"` permanently removes test tick and clears all weather data
- `MODE = "rebuild"` regenerates all weather materials from scratch
- Requires global `live` instance variable (not defined in this file)
- Command line argument `120` (passed to `ue_run.py`) controls test duration

Source: read, not executed.
