# Review leads for tools/npc_batch.py (UNVERIFIED)
L54 | perf | O(n^2) 'all' check on creature list during insertion | For 1000 creatures, 10^6 checks would occur | Replace 'all' with a set for O(1) lookups | high
L55 | memory | Full creature list accumulated without limit application | Memory usage scales with total NPCs (not just batch size) | Apply limit during list construction | high
L37 | cleanup | Redundant 'creature = {}' after line 25 | Duplicate assignment with no effect | Remove line 37 | medium
