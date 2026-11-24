import sys, os, io, struct
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\tools")
from bsa import Bsa
from PIL import Image
D = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"
a = Bsa(D + "/Skyrim - Textures7.bsa")
for k in ("textures\\terrain\\tamriel\\tamriel.4.4.-4.dds", "textures\\terrain\\tamriel\\tamriel.4.-16.-4_n.dds"):
    raw = a.read(k)
    print(k, raw[84:88], struct.unpack_from("<II", raw, 12))
    im = Image.open(io.BytesIO(raw)); print(im.size, im.mode)
