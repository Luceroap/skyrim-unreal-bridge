# Local model triage

Date: 2026-10-30

The local model reports were reviewed against the current source. They are analysis aids, not proof that a fix is safe.

## Keep and use

- `notes/REVIEW_LEADS_VERIFIED.md` is the consolidated lead list.
- `notes/manual_test_checklist.md` is the regression checklist for the full-game renderer.
- `notes/memory_code_map.md` identifies current memory controls and their call sites.
- `notes/live_bridge_layers.md` maps renderer layers to their runtime controls.
- `notes/known_issues.md` records remaining full-game gaps.
- `notes/decisions_digest.md` records ownership and prior decisions.

## Confirmed useful leads

- The editor reads `area2/debug_flags.txt` on every editor tick. Cache the file contents and reload only when its modification time changes.
- The runtime reads terrain readiness data in the Tamriel update path. Cache the readiness set and reload only when the file changes.
- Runtime memory growth must be measured separately for loaded actors, mesh cache entries, imported Unreal packages, and the asset service process.
- Prefetch must remain opt-in and must never compete with assets required by the current Skyrim cell.
- `grass_live.py` is not active in the current `area2/addons.txt`, so its reported actor leak is not the current editor leak unless that layer is enabled.

## Rejected or already handled leads

- The launcher already checks for a running Unreal editor and closes duplicate editors before starting.
- Preview actor cleanup already destroys and removes entries in the current world-stream path.
- The memory governor already limits unload batches and removes unused mesh cache entries. This does not prove that all retained Unreal packages are collectible, so runtime measurement is still required.
- The atmosphere capture scan is periodic, not a per-frame scan in the current code.
- Suggestions to increase actor limits or change shared-memory layouts require plugin-owner review and must not be applied from a local model report alone.
- Suggestions to enable FBX texture imports conflict with the project material pipeline and are not accepted without an asset-pipeline test.

## Next verification order

1. Run with all optional layers disabled and record memory, FPS, CPU, GPU, and import rate.
2. Enable one layer at a time: world, distant, Tamriel terrain, NPCs, and optional add-ons.
3. Repeat the 20 minute test with prefetch disabled, then with controlled on-demand travel.
4. Apply only fixes that reduce measured growth without breaking cell transitions, interiors, NPCs, or menus.
