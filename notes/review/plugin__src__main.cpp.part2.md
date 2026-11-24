# Review leads for plugin/src/main.cpp.part2 (UNVERIFIED)
L860 | bug | Swallowing exceptions: `__except (EXCEPTION_EXECUTE_HANDLER) { return false; }` | Critical errors hidden without logging, causing silent failure | Log exception details and return false | high
L900 | perf | Redundant set creation: `std::unordered_set<RE::Actor*> seen;` | Unnecessary per-frame set allocation/deallocation (30Hz) | Move set to static and use clear() | high
L976 | perf | Repeated NormalizeModel: `const std::string m = NormalizeModel(mp);` | String normalization called multiple times for same path in gear processing | Cache normalized results in map | medium
L941 | perf | Unbounded armor addon loop: `for (auto* arma : skin->armorAddons)` | Potential O(n) processing per creature actor (1Hz) for skin addons | Limit to max 5 addons | medium
L965 | bug | Null pointer access: `if (!eq) continue;` | Missing validation for armor addon access in shield processing | Add null check before access | medium
