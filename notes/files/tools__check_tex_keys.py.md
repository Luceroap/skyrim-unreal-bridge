## Purpose
Reports mesh materials with ambiguous texture keys (where multiple DDS textures match a material's naming convention) and detects diffuse texture files sharing the same base filename across different folders. This helps prevent conflicts in Unreal Engine asset referencing.

## How it is run
Command line: `python tools/check_tex_keys.py`. No other project files call this script (confirmed via `git grep` only showing the usage message within the script itself).

## Inputs
- Texture keys from `area2/tex/*.png` (excluding keys ending in `_n`, `_rmaos`, or `_s`)
- Material files from `area2/obj/*.mtl`

## Outputs
Prints to console:
- Count of ambiguous materials (with top 40 examples)
- Count of duplicate base filenames across folders (with top 30 examples)
- Formatted lists of affected materials and texture paths

## Key functions
glob.glob  
re.match  
collections.defaultdict  
os.path.splitext  
print (results)  

## Depends on
Standard Python modules: collections, glob, os, re

## Gotchas
- Hardcoded 'area2' directory name (breaks if renamed)
- Excludes texture keys ending with `_n`, `_rmaos`, `_s`
- Only processes `.png` files in `area2/tex`
- Uses Windows path separators (`\`) in string replacements
- Case-insensitive matching may cause unexpected behavior

Source: read, not executed.
