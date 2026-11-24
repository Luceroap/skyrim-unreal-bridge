import unreal
unreal.SystemLibrary.execute_console_command(None, "r.Editor.Viewport.ScreenPercentage " + open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\sp.txt").read().strip())
print("ok", unreal.SystemLibrary.get_console_variable_float_value("r.Editor.Viewport.ScreenPercentage"))
