import unreal
unreal.SystemLibrary.execute_console_command(None, "ProfileGPU")
import struct, ctypes
print("hour/weather from last packet:")
try:
    import live_bridge as lb
    v = struct.unpack(lb.PKT_FMT, ctypes.string_at(live.pkt, lb.PKT_SIZE))
    print(v[23], v[27].split(b"\0")[0], v[29].split(b"\0")[0])
except Exception as e:
    print(e)
