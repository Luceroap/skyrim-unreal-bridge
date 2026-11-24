w = unreal.EditorLevelLibrary.get_editor_world()
unreal.SystemLibrary.execute_console_command(w, "memreport -full")
acts = unreal.EditorLevelLibrary.get_all_level_actors()
from collections import Counter
c = Counter(type(a).__name__ for a in acts)
print("actors", len(acts), c.most_common(8))
print("loaded meshes:", len(unreal.EditorAssetLibrary.list_assets("/Game/Area2", recursive=False)))
