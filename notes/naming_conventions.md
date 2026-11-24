# Naming Conventions

## Asset Names from Model Paths
**Function**: `asset_name(nif)` (tools/grass_placement.py:330)  
**Rule**: Extract base name (without path/extension) from `.nif` path.  
**Example**: `nif = "clutter/banners/x.nif"` → `"x"` 

## Texture Keys
**Function**: `tex_key(rel)` (tools/land_textures.py:289)  
**Rule**: Extract base name (without path/extension) from relative path.  
**Example**: `rel = "clutter/banners/x.nif"` → `"x"` 

## Material Slot Names
**Function**: `_material_for_slot(slot, key=None)` (unreal/SkyBridge/npc_live.py:245)  
**Rule**: Combine slot name and key (if provided) with underscore.  
**Example**: `slot = "hair", key = "tint"` → `"hair_tint"` 

## OBJ Names
**Function**: `write_obj(shapes, obj_path, mtl_name=None)` (tools/nif2obj.py:182)  
**Rule**: Base name of model (from `.nif`) with `.obj` extension.  
**Example**: Model path `dagger.nif` → `dagger.obj` 

## Unreal Bone-Name Mangling
**Function**: `ue_bone(name)` (unreal/SkyBridge/npc_live.py:430)  
**Rule**: Replace hyphens (`-`) with underscores (`_`).  
**Example**: `"Head-Bone"` → `"Head_Bone"` 

## Folder Names Under /Game
**Function**: `_texture(key)` (unreal/SkyBridge/ue_assets.py:22)  
**Rule**: Capitalize texture key for folder name (no path).  
**Example**: Key `"rock"` → `/Game/Textures/Rock` (folder name `"Rock"`)
