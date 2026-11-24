## Purpose
This script tests interior key generation for Solitude, Riften, and Markarth interiors by processing their first, middle, and last entries in the `live.interiors` data structure.

## How it is run
Executed directly via command line: `python area2/test_interior.py`. No other project files reference or call this file (confirmed by empty `git grep` results).

## Inputs
- Filtered interior IDs from `live.interiors` matching prefixes "Solitude", "Riften", or "Markarth".
- Current state of `live.interiors` dictionary.

## Outputs
- Prints a list of tuples (edid, interior_key()) results to stdout.
- Modifies global state variables: `live.seen_ids`, `live._int_t`, `live._int_key`.

## Key functions
interior_key() - Generates key based on current interior state.

## Depends on
live.py (module defining `live.interiors` and state variables).

## Gotchas
- Requires at least one interior ID matching "Solitude", "Riften", or "Markarth"; crashes if none exist.
- Modifies global state variables (`seen_ids`, `_int_t`, `_int_key`) without recovery.
- Uses first (index 0), middle (index `len//2`), and last (index `-1`) entries from filtered list.
- Middle index calculation uses integer division (e.g., 4 entries → index 2).
- No error handling for empty `live.interiors` filtered list.

Source: read, not executed.
