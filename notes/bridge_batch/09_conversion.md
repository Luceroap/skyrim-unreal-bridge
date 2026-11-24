# Asset conversion failure recovery

Local-model review lead; NOT independently verified or applied.

## Finding
Missing success marker in asset conversion process

## Evidence
- tools/asset_service.py:51 - ok = os.path.exists(os.path.join(AREA, "export", n + ".fbx"))

## Suggested fix
Add a success marker to the READY file after successful conversion

## Validation needed
Check if the editor reads READY.txt for completed assets and verify that the conversion process correctly marks assets as ready
