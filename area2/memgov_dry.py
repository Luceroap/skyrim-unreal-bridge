import sys, time, importlib
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import memory_governor as mg
importlib.reload(mg)
t = time.time()
meshes, mats, tex = mg._in_use()
print("in use: %d meshes, %d materials, %d textures (%.2f s)" % (len(meshes), len(mats), len(tex), time.time() - t))
cached = [(n, m) for n, m in live.mesh_cache.items() if m]
unused = [n for n, m in cached if m.get_path_name() not in meshes]
print("cached meshes %d, unused now %d, e.g. %s" % (len(cached), len(unused), unused[:8]))
print("memory", mg.memory_gb())
