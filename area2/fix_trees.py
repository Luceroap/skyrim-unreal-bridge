n = 0
for a in getattr(live, "distant_actors", []):
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if c.get_editor_property("instance_end_cull_distance") == 160000:
            c.set_cull_distances(0, 300000); n += 1
print("trees extended", n)
unreal.SystemLibrary.execute_console_command(None, "ProfileGPU")
