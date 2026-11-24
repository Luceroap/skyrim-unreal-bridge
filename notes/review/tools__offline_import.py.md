# Review leads for tools/offline_import.py (UNVERIFIED)
L9 | robustness | `CMD = r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"` | hard-coded path breaks portability | use environment variables or config | high
L10 | robustness | `PROJ = os.path.join(ROOT, "unreal", "SkyBridge", "SkyBridge.uproject")` | hard-coded path breaks if project moves | use relative paths or config | high
L15 | bug | `tasklist /FI "IMAGENAME eq " + exe` | missing quotes breaks process detection | wrap filter in quotes: `"/FI \"IMAGENAME eq " + exe + "\""` | high
L26 | bug | `sys.argv.index(name) + 1` | crashes if argument lacks value | add index check: `if name in sys.argv and len(sys.argv) > index+1` | medium
L37 | robustness | `print("progress: area2\\offline_import.log")` | logs to `offline_import_stdout.log` not expected path | correct output to match actual log path | high
L44 | bug | `open(os.path.join(ROOT, "area2", "offline_import.log"))` | reads wrong log file (not `offline_import_stdout.log`) | fix file path to match log destination | high
