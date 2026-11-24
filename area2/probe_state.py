"""Is Skyrim in the world? Reads the bridge packet (run with normal python)."""
import ctypes, struct, time
k = ctypes.windll.kernel32
k.OpenFileMappingW.restype = ctypes.c_void_p
k.MapViewOfFile.restype = ctypes.c_void_p
k.MapViewOfFile.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_size_t]
for n in ("v1", "world_v1", "actors_v1", "gear_v1"):
    print(n, "open" if k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_" + n) else "MISSING")
h = k.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_v1")
if h:
    p = k.MapViewOfFile(h, 4, 0, 0, 0)
    for i in range(3):
        b = ctypes.string_at(p, 400)
        ui = struct.unpack_from("<I", b, 300)[0]
        print("frame", struct.unpack_from("<I", b, 12)[0], "pos", [round(x) for x in struct.unpack_from("<3f", b, 16)],
              "hour %.3f" % struct.unpack_from("<f", b, 92)[0], "ui", bin(ui), "inWorld", bool(ui & 64), "loading", bool(ui & 4),
              "mainmenu", bool(ui & 2), "menu", bool(ui & 1), "cell", b[172:236].split(b"\0")[0], "ws", b[236:300].split(b"\0")[0])
        time.sleep(1)
