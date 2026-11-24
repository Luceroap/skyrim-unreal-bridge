import sys, glob, io, os, struct
sys.path.insert(0, os.path.dirname(__file__))
from bsa import Bsa
from PIL import Image

d, out = sys.argv[1], sys.argv[2]
want = None
for p in sorted(glob.glob(os.path.join(d, "Skyrim - Textures*.bsa"))):
    b = Bsa(p)
    names = [k for k in b.files if k.startswith("textures\\landscape\\") and ("dirt" in k or "grass" in k or "whiterun" in k)
             and not k.endswith(("_n.dds", "_m.dds", "_p.dds", "_msn.dds", "_sk.dds"))]
    for k in sorted(names)[:12]:
        print(k)
    pick = [k for k in names if k in ("textures\\landscape\\dirt02.dds", "textures\\landscape\\fielddirtgrass01.dds")]
    if pick and want is None:
        raw = b.read(pick[0])
        if raw[84:88] == b"DX10":
            f = struct.unpack_from("<I", raw, 128)[0]
            if f in (72, 75, 78, 99): raw = raw[:128] + struct.pack("<I", f - 1) + raw[132:]
        Image.open(io.BytesIO(raw)).convert("RGB").save(out)
        want = pick[0]
print("PICKED", want)
