@echo off
setlocal
cd /d "%~dp0"
title PC Skyrim Bridge AI Assistant

powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3; if ($r.StatusCode -ne 200) { exit 1 } } catch { exit 1 }"
if errorlevel 1 (
 echo The local AI endpoint is not running.
 echo Start Ollama, then run this file again.
 echo Expected endpoint: http://127.0.0.1:11434/v1
 pause
 exit /b 1
)

call "%~dp0OpenCode_Local.bat"
endlocal
