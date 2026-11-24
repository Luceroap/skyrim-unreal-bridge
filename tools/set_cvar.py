"""Set console variables in the live editor:  python tools/set_cvar.py "r.ScreenPercentage 100" "sg.ShadowQuality 4" """
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from start_bridge import ue_exec

code = "import unreal\nfor c in %r:\n    unreal.SystemLibrary.execute_console_command(None, c)\nprint('set', %r)" % (sys.argv[1:], sys.argv[1:])
print(ue_exec(code, 30))
