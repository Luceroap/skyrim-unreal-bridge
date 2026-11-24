# World actor creation and cleanup

Local-model review lead; NOT independently verified or applied.

## Finding
Duplicated actor spawning due to incomplete cleanup of preview actors

## Evidence
- unreal/SkyBridge/live_bridge.py:578 - for rid in [r for r in self.preview if r in seen]:
- unreal/SkyBridge/live_bridge.py:579 - self.preview.pop(rid).destroy_actor()
- unreal/SkyBridge/live_bridge.py:591 - for rid in [r for r in self.preview if r in self._preview_pos and taken(self._preview_pos[r])]:

## Suggested fix
Replace preview cleanup with direct actor destruction and remove preview entries

## Validation needed
Verify that preview actors are properly destroyed when their references are seen in the stream, and that no duplicate actors remain after stream updates.
