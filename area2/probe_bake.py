import sys, os, re
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\tools")
import tamriel_terrain as tt
from PIL import Image
land = tt.load_land()
b = tt.Baker(land["ltex"])
skip = sorted(tt.whiterun_cells())
print("whiterun cells", skip[:5], len(skip))
xy = skip[len(skip) // 2]
c = land["cells"][xy]
print(xy, "base", {q: (hex(f), land["ltex"].get(f)) for q, f in c["base"].items()})
for q, l, f, op in c["layers"]:
    print(" layer q%d l%d %s %s max %.2f" % (q, l, hex(f), land["ltex"].get(f), max(op)))
vc = c["vc"]
if vc:
    print("vc mean", sum(vc) / len(vc), "min", min(vc), "max", max(vc))
img = b.cell(c, 512)
cv = dict(c); cv["vc"] = None
img2 = b.cell(cv, 512)
old = Image.open(os.path.join(tt.TEX, "terrain_tile_%d_%d.png" % xy)).resize((512, 512))
out = Image.new("RGB", (1536, 512)); out.paste(img, (0, 0)); out.paste(img2, (512, 0)); out.paste(old, (1024, 0))
out.save(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\prev_cmp.png")
