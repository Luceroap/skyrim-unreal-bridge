## Purpose
Captures three NPC images from Skyrim at a specified distance using NPC names and composites them into a single output image. The script automates the process of triggering captures via external tools and stitching images together.

## How it is run
Command line: `python area2/cap.py "Aela,Carlotta" 230 body`. Called from the main workflow as documented in `README.md` (line 326).

## Inputs
- `names`: Comma-separated NPC names (e.g., `Aela,Carlotta`)
- `dist`: Numeric distance value (e.g., `230`)
- `prefix`: Output filename prefix (e.g., `body`)

## Outputs
- `area2/body_all.png` (combined image)
- `area2/<prefix>_0.png`, `area2/<prefix>_1.png`, `area2/<prefix>_2.png` (intermediate images)
- `area2/npc_step.txt` (status communication for external processes)

## Key functions
step(s) - Writes state to npc_step.txt and triggers external capture
image stitching - Combines images into a single RGB file
thumbnail resizing - Scales output to 1400x700 max dimensions

## Depends on
`tools/ue_run.py`, `area2/npc_capture.py`, PIL, os, subprocess, sys, time

## Gotchas
- Hardcoded 1.5s sleep after setup step before capturing
- Inputs converted to RGB, losing transparency
- Output constrained to fixed thumbnail dimensions (1400x700)
- Skips missing intermediate images (0-2)
- Requires external synchronization via npc_step.txt

Source: read, not executed.
