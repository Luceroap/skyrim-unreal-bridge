## Purpose
Identifies duplicate actors in Skyrim's city, preview, and streamed actor data based on mesh name and rounded location coordinates. Helps detect inconsistencies in actor placement during scene rendering.

## How it is run
Command: `python area2/probe_dup.py`  
No other files call it (git grep for "probe_dup.py" found no results).

## Inputs
- `live.city` (dict: actor IDs → actor data)
- `live.preview` (dict: actor IDs → actor data)
- `live.actors` (dict: actor IDs → actor data)

## Outputs
- Console output showing:
  - Lengths of city, preview, and streamed actor sets
  - Overlap counts between city/preview, city/streamed, preview/streamed
  - Number of duplicate groups (mesh + location)
  - Group distribution (e.g., `(('city', 'preview'), 5)`)

## Key functions
key() - computes hashable location/mesh key from actor data

## Depends on
live.py (provides `live` object attributes), collections (for `Counter`)

## Gotchas
- Requires `live` module to provide `city`, `preview`, and `actors` attributes
- Uses rounded coordinates (x/20, y/20, z/20), risking false duplicates for nearby actors
- Depends on `static_mesh_component.static_mesh` existing in actor data
- Fails if any actor lacks `get_actor_location()` method
- Relies on `live.actors` data structure matching expected format

Source: read, not executed.
