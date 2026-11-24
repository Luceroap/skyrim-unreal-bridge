# Offline import completion reporting

Local-model review lead; NOT independently verified or applied.

## Finding
Failed imports are not counted as failures in the final summary, leading to false success reports.

## Evidence
- unreal/SkyBridge/offline_import.py:45 - say("models finished: %d imported, %d failed, %d still to import" % (done, failed, len(todo) - done - failed))

## Suggested fix
Replace 'len(todo) - done - failed' with 'len(todo) - done' in the final summary message.

## Validation needed
Run offline_import.py with a known failing model (e.g., missing FBX) and verify the 'failed' count matches the actual failures in the log.
