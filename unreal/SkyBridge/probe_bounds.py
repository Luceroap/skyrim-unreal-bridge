import unreal
for n in ["wrhousebanneredmare01", "wrhouse02", "wrbridge01", "wrguardhouse01", "wrbreezehome01"]:
    m = unreal.load_asset("/Game/WhiterunMeshes/" + n)
    b = m.get_bounds()
    unreal.log("PROBE %s origin=(%.1f,%.1f,%.1f) ext=(%.1f,%.1f,%.1f)" % (n, b.origin.x, b.origin.y, b.origin.z, b.box_extent.x, b.box_extent.y, b.box_extent.z))
