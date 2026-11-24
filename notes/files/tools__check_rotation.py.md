## Purpose
Compares REFR rotation angles with the actual world rotation matrix from plugin dump data to validate consistency between expected and observed rotation transformations.

## How it is run
Command: `python tools/check_rotation.py <input.tsv>`. No other files in the project call this script (confirmed via `git grep` showing no matches).

## Inputs
TSV file with at least 22 columns per line; rotation angles in columns 7-9 (0-based), row-major world rotation matrix in columns 13-21 (0-based).

## Outputs
Console output showing:
- Count of references with loaded 3D rotations
- Pure-yaw reference counts (|rx|, |ry| < 1e-3)
- Error analysis for pure-yaw references (clockwise/counter-clockwise)
- Best Euler rotation order matches for tilted references (|rx| or |ry| > 0.02)

## Key functions
ypred_cw
ypred_ccw
err
Rx
Ry
Rz
mul
flat

## Depends on
Python standard libraries (sys, math, collections), input TSV file format.

## Gotchas
- Skips entries where column 11 equals "1".
- Pure-yaw references require |rx| < 1e-3 and |ry| < 1e-3.
- World rotation matrix comparison uses 0.02 error threshold.
- Processes world rotation matrix in row-major order.
- Tests all 6 Euler rotation orders with 8 sign combinations (2³).

Source: read, not executed.
