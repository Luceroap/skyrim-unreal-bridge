@echo off
rem Photo shoot: stops the local model, starts Skyrim + Unreal at showcase quality, then listens for photo hotkeys (F8 4K, F9 8K, F5 time, F6 weather, F7 release).
rem Fly with the Skyrim console: ~ then tfc.  Photos land in screenshots\photos.
title Photo shoot
cd /d "C:\Users\Aidan\SkyrimUnrealBridge"
python tools\shot_session.py --max
python tools\photo_keys.py
pause
