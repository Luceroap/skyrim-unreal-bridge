import sys, os, tempfile
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\tools")
from bsa import Bsa
import nif2obj
D = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
m = Bsa(D + "/Skyrim - Meshes1.bsa")
p = "meshes\\terrain\\tamriel\\tamriel.4.4.-4.btr"
tmp = os.path.join(tempfile.gettempdir(), "probe.btr"); open(tmp, "wb").write(m.read(p))
for name, verts, uvs, tris, tex in nif2obj.extract(tmp):
    print(name, len(verts), tex)
    if not tex: continue
    xs = [v[0] for v in verts]; ys = [v[1] for v in verts]
    print("x", min(xs), max(xs), "y", min(ys), max(ys))
    for i in (0, len(verts) // 3, len(verts) // 2, len(verts) - 1):
        print(verts[i], uvs[i])
