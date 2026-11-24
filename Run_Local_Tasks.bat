@echo off
cd /d "%~dp0"
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" tools\run_bridge_batch.py --resume %*
pause
