import importlib, sys
rm = importlib.reload(sys.modules["remaster_materials"])
m = rm.master()
print("master", [str(n) for n in unreal.MaterialEditingLibrary.get_scalar_parameter_names(m)])
