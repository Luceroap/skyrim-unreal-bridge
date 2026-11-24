@echo off
title Importing assets into Unreal (no game needed)
echo Closes Skyrim + the Unreal editor first, then imports every converted model. About 2.5 hours; safe to stop and run again.
"C:\Users\Aidan\AppData\Local\Programs\Python\Python312\python.exe" "C:\Users\Aidan\SkyrimUnrealBridge\play.py" --stop
"C:\Users\Aidan\AppData\Local\Programs\Python\Python312\python.exe" "C:\Users\Aidan\SkyrimUnrealBridge\tools\offline_import.py" %*
pause

