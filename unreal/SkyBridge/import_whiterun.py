import unreal, glob, os
src = r"C:\Users\Aidan\SkyrimUnrealBridge\whiterun\export"
tasks = []
for f in sorted(glob.glob(os.path.join(src, "*.fbx"))):
    t = unreal.AssetImportTask()
    t.filename = f
    t.destination_path = "/Game/WhiterunMeshes"
    t.automated = True
    t.replace_existing = True
    t.save = True
    tasks.append(t)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for t in tasks:
    unreal.log("IMPORTED %s -> %s" % (os.path.basename(t.filename), [str(p) for p in t.imported_object_paths]))
