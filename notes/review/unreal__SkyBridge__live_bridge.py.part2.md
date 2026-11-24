# Review leads for unreal/SkyBridge/live_bridge.py.part2 (UNVERIFIED)
L584 | perf | Building occupied set from reference data | O(n) per frame with n large (thousands of references) | Cache and update set only when reference data changes | high
L640 | perf | O(n^2) duplicate check for spawn requests | Checks all actors per spawn request (e.g., `any(d["model"] == model and ... for d in self.actors.values())`) | Replace with spatial grid for O(1) lookups | high
L748 | perf | Looping over all seen IDs for interior voting | Counts votes per interior over thousands of objects every frame | O(n) per frame | Maintain incremental vote counts | high
L1025 | perf | Reading debug_flags.txt every frame | Unnecessary disk I/O per frame | Cache flags and reload on file change | medium
L1045 | perf | Reading exec_request.py every frame | Unnecessary disk I/O per frame | Check file existence once per frame and delete after processing | medium
