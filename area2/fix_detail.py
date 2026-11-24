import importlib, sys
rm = importlib.reload(sys.modules["remaster_materials"]) if "remaster_materials" in sys.modules else importlib.import_module("remaster_materials")
m = rm.master()
print("params:", [str(n) for n in unreal.MaterialEditingLibrary.get_scalar_parameter_names(m)])
