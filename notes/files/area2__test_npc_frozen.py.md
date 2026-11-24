## Purpose
This script tests a frozen NPC animation system comparing three walker types: a static pose walker (frozen), a bind-walker (rotating limbs), and an animated walker. It records and analyzes gait cycles to verify synchronization between pose data and movement timing.

## How it is run
Run directly as a Python script: `python area2/test_npc_frozen.py`. No other files call it (git grep returned no references).

## Inputs
Internal state from `npc_live.py` via `nl._ingest`, calculated parameters (phase, x) in `bones_at`, hardcoded time values (e.g., 1.2s gait cycle).

## Outputs
Console prints showing limb angles for frozen (last 6 samples), bind-walker (last 6 samples), and animated walker (last 6 samples). Duration/speed metrics: "animated frozen=... loop dur 1.20 s (true 1.2) speed 100".

## Key functions
qax - Compute quaternion from axis-angle  
bones_at - Generate bone positions for walker types  
shown - Format limb angles for display  

## Depends on
`npc_live.py` (imports as `nl`), `math`, `sys`

## Gotchas
Hardcoded Windows path in sys.path: `r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge"`  
Modifies internal `npc_live` state via `nl._state` (not public API)  
Loop duration hard-coded as 1.2s (matches comment but uses `t / 1.2` internally)  
Uses `nl._ingest` directly (implementation detail)  
Relies on magic number `150` iterations (5s at 30Hz)  

Source: read, not executed.
