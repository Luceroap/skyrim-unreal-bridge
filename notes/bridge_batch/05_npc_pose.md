# NPC animation and T-pose handling

Local-model review lead; NOT independently verified or applied.

## Finding
Stale pose handling fails when an actor is not drawn (outside camera view) for more than 2.5 seconds, causing the skeleton to revert to bind pose instead of maintaining the last valid pose.

## Evidence
- unreal/SkyBridge/npc_live.py:527 - Skyrim stops animating actors it is not drawing (outside its camera view, occluded, far away): the skeleton is the bind pose (T/A pose)
- unreal/SkyBridge/npc_live.py:529 - Keep the last real pose of that actor, or borrow a natural one from another animated actor of the same sex.
- unreal/SkyBridge/npc_live.py:530 - if _is_bind(bones, rest, rq) or (moving and entry.get("frozen")):

## Suggested fix
Replace the condition in line 530 to also check if the actor was previously animated (not in bind pose) before reverting to bind pose.

## Validation needed
Check if the actor's 'frozen' state is properly maintained when outside camera view for more than 2.5 seconds, ensuring it doesn't revert to bind pose.
