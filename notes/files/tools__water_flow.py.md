## Purpose
Calculates downhill flow direction vectors for every water strip in `area2/water_quads.csv` using smoothed terrain height gradients. Computes unit direction vectors (`fx`, `fy`) and flow speed based on the negative gradient of terrain heights within wet cells, outputting results to `area2/water_flow.csv`.

## How it is run
Command: `python -I water_flow.py`  
Files calling it:  
- `tools/water_flow_run.py` (via its `"""python tools/ue_run.py tools/water_flow_run.py..."""` header)  
- Referenced in `COORDINATION.md` as a required step after regenerating `water_quads.csv`

## Inputs
- `area2/water_quads.csv` (water strip definitions with coordinates, count, height)  
- Terrain height data (`LAND VHGT`) processed from `dw.PLUGINS` directories via `distant_world` module

## Outputs
- `area2/water_flow.csv` (same line order as input; columns: `fx,fy,speed`)  
- Console output: "water cells", "land cells" counts and "wrote %d strips..." with speed percentiles

## Key functions
gauss(sig): Computes Gaussian kernel for blurring  
blur(a, sig): Applies Gaussian blur to 2D array  
gradient: Computes height gradient (d/dy, d/dx)  
main loop: Processes each water strip line  

## Depends on
- `distant_world.py` (imports `dw.ROOT`, `dw.PLUGINS`, `dw.read_water`)  
- `numpy` (arrays, gradients, blurring)  

## Gotchas
- Line counts between `water_quads.csv` and `water_flow.csv` must match  
- Do not call `remaster_materials.water_material(rebuild=True)` after execution  
- Requires valid `area2/water_quads.csv` generated before running  
- Uses `STEP=128.0` for terrain sampling (128-unit grid)  
- Fallback logic for strips without wet cells uses non-nan terrain values  

Source: read, not executed.
