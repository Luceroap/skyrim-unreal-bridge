"""Which models in the live world stream are missing in Unreal, and why. Usage: python tools\\stream_coverage.py [filter]"""
import ctypes, ctypes.wintypes as wt, math, os, struct, sys, collections

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
AREA = os.path.join(ROOT, "area2")
CONTENT = os.path.join(ROOT, "unreal", "SkyBridge", "Content", "Area2")
MAX_MODELS, MAX_REFS, MODEL_LEN = 4096, 16384, 128
HDR = 32; REF_FMT = "<II3f9ffI"; REF = struct.calcsize(REF_FMT)
REFS_OFF = HDR + MAX_MODELS * MODEL_LEN

k = ctypes.windll.kernel32
k.OpenFileMappingW.restype = ctypes.c_void_p
k.MapViewOfFile.restype = ctypes.c_void_p
k.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
h = k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_world_v1")
if not h:
    raise SystemExit("world mapping not found")
p = k.MapViewOfFile(h, 4, 0, 0, 0)
hd = struct.unpack("<8I", ctypes.string_at(p, HDR))
nref, nmod = hd[4], hd[5]
data = ctypes.string_at(p, REFS_OFF + nref * REF)
models = [data[HDR + i * MODEL_LEN: HDR + (i + 1) * MODEL_LEN].split(b"\0")[0].decode("latin1") for i in range(nmod)]
refs = [struct.unpack_from(REF_FMT, data, REFS_OFF + i * REF) for i in range(nref)]

read = lambda n: set(open(os.path.join(AREA, n)).read().split()) if os.path.exists(os.path.join(AREA, n)) else set()
ready, failed, requested = read("ready.txt"), read("failed.txt"), read("requests.txt")
count = collections.Counter(r[1] for r in refs)
flt = sys.argv[1].lower() if len(sys.argv) > 1 else ""
rows = collections.Counter()
for mi, m in enumerate(models):
    if flt and flt not in m.lower():
        continue
    name = m[:-4].replace("/", "_") if m.endswith(".nif") else m
    if " " in m: st = "SKIPPED (space in name)"
    elif os.path.exists(os.path.join(CONTENT, name + ".uasset")): st = "ok"
    elif name in failed: st = "FAILED to convert"
    elif name in ready: st = "converted, not imported"
    elif name in requested: st = "requested, not converted"
    else: st = "never requested"
    rows[st] += count[mi]
    if st != "ok":
        print("%-26s %4d refs  %s" % (st, count[mi], m))
print("\nrefs by status:", dict(rows), " total refs", nref, "models", nmod)
