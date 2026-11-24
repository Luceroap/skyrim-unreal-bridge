"""Print live values from the SkyrimUnrealBridge shared memory (run while Skyrim is running)."""
import ctypes, struct, time

FILE_MAP_READ = 4
k = ctypes.windll.kernel32
k.OpenFileMappingW.restype = ctypes.c_void_p
k.MapViewOfFile.restype = ctypes.c_void_p
k.MapViewOfFile.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_size_t]
h = k.OpenFileMappingW(FILE_MAP_READ, False, "Local\\SkyrimUnrealBridge_v1")
if not h:
    raise SystemExit("mapping not found: is Skyrim running with the plugin loaded?")
p = k.MapViewOfFile(h, FILE_MAP_READ, 0, 0, 0)
FMT = "<4I21f2I64s64s64s"  # matches shared/BridgeShared.h (pack 4)
size = struct.calcsize(FMT)
s = lambda b: b.split(b"\0")[0].decode(errors="replace")
while True:
    v = struct.unpack(FMT, ctypes.string_at(p, size))
    print(f"frame={v[3]} player={v[4]:.0f},{v[5]:.0f},{v[6]:.0f} cam={v[10]:.0f},{v[11]:.0f},{v[12]:.0f} "
          f"fov={v[22]:.0f} hour={v[23]:.2f} weather={s(v[27])}({v[25]:08X}) cell={s(v[28])} ws={s(v[29])}")
    time.sleep(0.5)
