import importlib, sys
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import memory_governor
importlib.reload(memory_governor)
src = open(r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py").read()
src = src[:src.rindex("\nstart()")]
ns = {"__name__": "live_bridge_hot"}
exec(compile(src, "live_bridge.py", "exec"), ns)
type(live).tick_body = ns["Live"].tick_body
print("tick_body patched; governor", memory_governor.memory_gb())
