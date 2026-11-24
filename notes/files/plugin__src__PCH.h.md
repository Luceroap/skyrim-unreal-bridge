## Purpose
The file serves as a precompiled header (PCH) for the SkyrimUnrealBridge plugin, accelerating compilation by pre-processing common dependencies. It includes the Skyrim engine (RE/Skyrim.h) and SKSE modding framework (SKSE/SKSE.h) headers.

## How it is run
Not executed directly. Included in C++ source files (e.g., `main.cpp`, `plugin.cpp`) via `#include "PCH.h"`. Verified via `git grep -n "PCH\.h" -- *.cpp`.

## Inputs
Headers from `RE/Skyrim.h` and `SKSE/SKSE.h` (project-specific, required for Skyrim/SE integration).

## Outputs
Precompiled header file (e.g., `PCH.h.gch`) generated during compiler execution, stored in build artifacts (not visible in source tree).

## Key functions
None; this is a header file. Contains no executable functions.

## Depends on
`RE/Skyrim.h`, `SKSE/SKSE.h` (core engine and modding API headers).

## Gotchas
- The `using namespace std::literals;` may conflict with other string literal usages in large projects.  
- Missing RE/SKSE headers will cause compilation failure.  
- Must be updated if RE/SKSE API changes.  
- Precompiled header regeneration required after modifying included headers.  
- Not compatible with non-C++ source files (e.g., `.py`/`.md`).

Source: read, not executed.
