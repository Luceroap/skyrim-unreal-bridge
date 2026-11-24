import unreal
fbx = r"C:\Users\Aidan\SkyrimUnrealBridge\area2\npc\export\npc_000cdd72.fbx"
ui = unreal.FbxImportUI()
ui.set_editor_property("import_mesh", True)
ui.set_editor_property("import_as_skeletal", True)
ui.set_editor_property("import_materials", False)
ui.set_editor_property("import_textures", False)
ui.set_editor_property("import_animations", False)
ui.set_editor_property("create_physics_asset", False)
ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
t = unreal.AssetImportTask()
t.filename = fbx; t.destination_path = "/Game/Npc"; t.automated = True; t.replace_existing = True; t.save = False
t.options = ui
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
print("imported:", [str(p) for p in t.get_editor_property("imported_object_paths")])
mesh = unreal.load_asset("/Game/Npc/npc_000cdd72")
print("mesh", mesh, type(mesh).__name__)
if mesh:
    sk = mesh.get_editor_property("skeleton")
    print("skeleton", sk)
    names = unreal.SkeletalMeshEditorSubsystem if hasattr(unreal, "SkeletalMeshEditorSubsystem") else None
    print("materials", [str(m.material_slot_name) for m in mesh.get_editor_property("materials")][:12])
    comp_cls = [n for n in dir(unreal) if "Poseable" in n]
    print("poseable classes", comp_cls)
    print("PoseableMesh methods", [n for n in dir(unreal.PoseableMeshComponent) if "bone" in n.lower() or "skinned" in n.lower() or "skeletal" in n.lower()][:40])
