# Notes on live_bridge.py Layers

| Name | Function (file:line) | How often it runs | What flag or file turns it off |
|------|----------------------|-------------------|-------------------------------|
| Sky/Weather | update_sky | Per tick | N/A |
| Lights | apply_lights | Per tick | N/A |
| World Stream | apply_world | Per tick | N/A |
| City | city_world, city_some | On city change, per tick | self._flags contains 'nocity' |
| Distant World | distant_some, distant_setup | Per tick (distant_some), once (distant_setup) | self._flags contains 'nodistant' |
| Terrain | spawn_static_world | Once (on initialization) | N/A |
| Water | spawn_cell_water, water_slots | Once (spawn_cell_water), on object spawn (water_slots) | N/A |
| Interiors | set_interior, interior_key | On interior change, periodic | N/A |
| Prefetch | prefetch_step | Per tick | N/A |

## Add-on Modules
No add-on modules loaded from area2/addons.txt in the provided code. The code imports standard modules like `atmosphere` (line 30), `remaster_materials` (line 253), and `water_flow_apply` (line 223), but these are not loaded from area2/addons.txt.
