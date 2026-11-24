# Launcher and duplicate processes

Local-model review lead; NOT independently verified or applied.

## Finding
Startup path may create duplicate editors due to missing editor check before starting

## Evidence
- play.py:122 - if not running("UnrealEditor.exe"):
- play.py:124 - subprocess.Popen([UE, os.path.join(PROJ, "SkyBridge.uproject"), "-windowed", "-ResX=1600", "-ResY=900",

## Suggested fix
Add a check to ensure no duplicate editors are started by verifying the editor is not already running before launching

## Validation needed
Run with --stop to kill any existing UnrealEditor.exe, then run play.py without --stop to verify only one editor instance starts
