import time
import grass_live
st = live._grass
st["t_missing"] = 0.0
print("imported", [n for n in sorted(st["missing"]) if unreal.EditorAssetLibrary.does_asset_exist("/Game/Area2/" + n)])
for i in range(3):
    t = time.time()
    grass_live.update(live)
    print("update %d: %.0f ms, dirty %d, missing %d, err %s" % (i, (time.time() - t) * 1000, len(st["dirty"]),
                                                              len(st["missing"]), st["err"]))
print("near/far/models/tiles", grass_live.stats(live))
print({k: v for k, v in st["built"].items()})
