"""Print a summary of the plugin's live world stream."""
import ctypes, ctypes.wintypes as wt, struct
k = ctypes.windll.kernel32
k.OpenFileMappingW.restype = ctypes.c_void_p
k.MapViewOfFile.restype = ctypes.c_void_p
k.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
h = k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_world_v1")
if not h:
    raise SystemExit("world mapping not found (plugin not loaded or an old plugin version)")
p = k.MapViewOfFile(h, 4, 0, 0, 0)
hd = struct.unpack("<8I", ctypes.string_at(p, 32))
print("magic %08x version %d seq %d tick %d refs %d models %d lights %d status 0x%x" % hd[:8])
if hd[5]:
    print([ctypes.string_at(p + 32 + i * 128, 128).split(b"\0")[0].decode() for i in range(min(8, hd[5]))])
if hd[4]:
    ref_off = 32 + 4096 * 128
    for i in range(min(3, hd[4])):
        r = struct.unpack_from("<II3f9ffI", ctypes.string_at(p + ref_off, 64 * (i + 1)), 64 * i)
        print("ref %x model %d pos %.0f,%.0f,%.0f scale %.2f flags %d" % (r[0], r[1], r[2], r[3], r[4], r[14], r[15]))

