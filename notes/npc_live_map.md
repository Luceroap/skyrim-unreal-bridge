# Function Call Tree

## Functions

| Function | Description | Calls |
|----------|-------------|-------|
| `tick` | Every editor frame: smooths each NPC between stream samples. When the stream has a new frame (seq changed, ~30 Hz), reads it, spawns/despawns NPCs, and records samples. | `stream_seq`, `_read_and_spawn`, `_smooth`, `_apply_pose`, `_pose_gap` |
| `stream_seq` | Checks actor stream sequence number; initializes memory mapping if not active. | (Called by `tick`) |
| `_read_and_spawn` | Processes new actor data: spawns NPCs, despawns outdated ones, updates poses. | `parse_bones`, `mesh_for`, `_spawn`, `_ingest`, `read_gear`, `_weapon` |
| `_smooth` | Smooths NPC position/rotation between stream samples using linear interpolation. | `_ensure_rest`, `_pose_gap` |
| `_apply_pose` | Applies bone transformations to skeletal mesh based on stream data. | `_plan` |
| `_pose_gap` | Calculates limb update interval (seconds) based on distance to NPC. | (Called by `_smooth`, `tick`) |
| `read_actors` | Reads actor stream data from memory; parses bones lazily if requested. | (Called by `_read_and_spawn`) |
| `mesh_for` | Loads or imports skeletal mesh for an actor from FBX file. | (Called by `_read_and_spawn`) |
| `_spawn` | Creates Unreal Actor instance with skeletal mesh component. | (Called by `_read_and_spawn`) |
| `_ingest` | Processes new actor data: sets pose, records history, handles walking cycles. | `skel_key`, `rest_pose`, `_is_bind`, `_limb_rel`, `_walk_record` |
| `_walk_record` | Records gait cycle for walking NPCs from animated samples. | (Called by `_ingest`) |
| `_walk_pose` | Retrieves next pose in recorded gait cycle for walking NPCs. | (Called by `_ingest`) |
| `rest_pose` | Reads reference bone poses from JSON file for skeleton. | (Called by `_ingest`, `_walk_record`) |
| `skel_key` | Determines skeleton key (e.g., "male", "female", race) from actor data. | (Called by `_ingest`) |
| `parse_bones` | Parses bone data from actor stream buffer into dictionary. | (Called by `_read_and_spawn`) |
| `_is_bind` | Checks if skeleton is in bind pose (no animation) via limb angles. | (Called by `_ingest`) |
| `_limb_rel` | Computes relative bone orientations between current and rest pose. | (Called by `_ingest`, `_walk_record`) |
| `read_gear` | Reads worn gear (weapons, clothing) stream data from memory. | (Called by `_read_and_spawn`) |
| `_weapon` | Spawns weapon mesh on actor's streamed "WEAPON" node. | (Called by `_read_and_spawn`) |
| `_ensure_rest` | Ensures reference rest pose is loaded for bone transformations. | (Called by `_smooth`) |
| `_plan` | Precomputes bone transformation constants for pose math. | (Called by `_apply_pose`) |
| `ue_bone` | Converts FBX bone names to Unreal-compatible format. | (Called by `_plan`) |

## Module-level Constants

```python
AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
EXPORT = os.path.join(AREA, "npc", "export")
U = 1.4287
MAX_NPCS = 12
CREATURE_SLOTS = 6
RADIUS = 5200.0
POSE_BUDGET = (0.002, 0.008, 0.08)
UPDATE_HZ = 60.0
FLIP = (1.0, -1.0, 1.0)
MAXB = 512
NAMELEN = 40
MAXBONES = 320
APOSE = 180 + MAXBONES * 32
POSES_OFF = 32 + MAXB * NAMELEN
```

## `_state` Keys

- `map`
- `meshes`
- `actors`
- `rest`
- `last`
- `import_budget_t`
- `mats`
- `failed`
- `template`
