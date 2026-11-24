import importlib, sys, time
import grass_live
importlib.reload(grass_live)
t = time.time()
grass_live.update(live)
st = live._grass
print("update %.1f ms" % ((time.time() - t) * 1000), "ds", repr(st["ds"]), "tiles", len(st["tiles"]),
      "dirty", len(st["dirty"]), "missing", sorted(st["missing"]), "err", st["err"])
print("stats near/far/models/tiles", grass_live.stats(live))
t = time.time()
grass_live.update(live)
print("2nd update %.2f ms" % ((time.time() - t) * 1000))
