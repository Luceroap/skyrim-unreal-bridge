import unreal
unreal.SystemLibrary.execute_console_command(None, "csvprofile frames=%d" % int(globals().get("FRAMES", 300)))
print("csv started")
