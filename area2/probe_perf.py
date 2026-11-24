from collections import Counter
folders, meshes = Counter(), Counter()
n = 0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    f = str(a.get_folder_path())
    if not f.startswith("SkyBridge"):
        continue
    n += 1
    folders[f] += 1
    if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh:
        meshes[(f, a.static_mesh_component.static_mesh.get_name())] += 1
print("actors", n, dict(folders))
dup = [(k, c) for k, c in meshes.items() if c >= 8]
dup.sort(key=lambda x: -x[1])
print("models with >=8 copies:", len(dup), "covering", sum(c for _, c in dup), "actors")
print(dup[:15])
