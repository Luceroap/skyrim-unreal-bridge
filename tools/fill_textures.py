"""Fill in diffuse maps the converter missed: every area2/tex/<key>_n.png without <key>.png gets its colour map from the
game data (loose files first, PBR folders included, then every BSA, mods last-loaded wins as for loose files).
Textures with real cut-out alpha are listed in area2/tex/alpha_masked_extra.txt (read by remaster_materials.configure).
Usage: python tools/fill_textures.py"""
import glob, io, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bsa import Bsa
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "area2", "tex")
DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"


def decode(raw):
    if raw[84:88] == b"DX10":
        f = struct.unpack_from("<I", raw, 128)[0]
        if f in (72, 75, 78, 99):                      # *_SRGB variants: PIL only knows the UNORM ids
            raw = raw[:128] + struct.pack("<I", f - 1) + raw[132:]
    im = Image.open(io.BytesIO(raw)); im.load()
    return im.convert("RGBA")


def main():
    missing = sorted({os.path.basename(p)[:-6] for p in glob.glob(os.path.join(TEX, "*_n.png"))
                      if not os.path.exists(p[:-6] + ".png")})
    print(len(missing), "textures without a colour map")
    loose = {}
    for p in glob.glob(os.path.join(DATA, "textures", "**", "*.dds"), recursive=True):
        k = os.path.basename(p)[:-4].lower()
        if k in missing and (k not in loose or "\\pbr\\" in p.lower()):
            loose[k] = p
    archives = []
    for a in sorted(glob.glob(os.path.join(DATA, "*.bsa"))):
        try:
            archives.append(Bsa(a))
        except Exception:
            pass
    extra_path = os.path.join(TEX, "alpha_masked_extra.txt")
    masked = set(open(extra_path).read().split()) if os.path.exists(extra_path) else set()
    filled = 0
    for k in missing:
        raw = open(loose[k], "rb").read() if k in loose else None
        if raw is None:
            for a in reversed(archives):
                hit = next((f for f in a.files if f.endswith("\\" + k + ".dds")), None)
                if hit:
                    raw = a.read(hit); break
        if raw is None:
            print("not found:", k); continue
        try:
            im = decode(raw)
        except Exception as e:
            print("decode failed:", k, e); continue
        a = im.getchannel("A")
        lo = sum(a.histogram()[:128]) / float(im.size[0] * im.size[1])
        if lo > 0.05:                                  # >5% of the texture is see-through: leaves, needles, grass cards
            masked.add(k)
        im.save(os.path.join(TEX, k + ".png"))
        filled += 1
        print("filled", k, im.size, "masked" if k in masked else "")
    open(extra_path, "w").write("\n".join(sorted(masked)) + "\n")
    print("filled %d, masked list %d" % (filled, len(masked)))


if __name__ == "__main__":
    main()
