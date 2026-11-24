# NPC mesh and actor lifetime

Local-model review lead; NOT independently verified or applied.

## Finding
Stale actors not cleaned up when characters leave the scene

## Evidence
- unreal/SkyBridge/npc_live.py:789 - if _state["actors"][aid].get("weapon"):

## Suggested fix
Add a check for 'actor' in the actor entry before destroying it

## Validation needed
Check that actors are properly destroyed when they leave the scene, ensuring no stale references remain
