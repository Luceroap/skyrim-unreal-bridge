import unreal, glob, os, collections
bad = collections.defaultdict(list)
total = 0
for p in sorted(glob.glob(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Content\Area2\*.uasset")):
    n = os.path.splitext(os.path.basename(p))[0]
    mesh = unreal.load_asset("/Game/Area2/" + n)
    if not isinstance(mesh, unreal.StaticMesh) or n == "terrain":
        continue
    for i, sm in enumerate(mesh.static_materials):
        total += 1
        mi = sm.material_interface
        path = mi.get_path_name() if mi else "NONE"
        if "/Game/Area2Tex/M_" not in path:
            bad[str(sm.material_slot_name)].append(n)
unreal.log("AUDIT total slots %d, unassigned/white %d" % (total, sum(len(v) for v in bad.values())))
for slot, meshes in sorted(bad.items(), key=lambda kv: -len(kv[1]))[:40]:
    unreal.log("AUDIT slot=%s used by %d meshes e.g. %s" % (slot, len(meshes), meshes[0]))
