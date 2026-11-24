"""python tools/ue_run.py tools/water_flow_run.py   (needs the editor running with live_bridge; water_flow.csv from tools/water_flow.py)"""
import sys
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge")
import importlib, water_flow_apply
importlib.reload(water_flow_apply)
print(water_flow_apply.run())
