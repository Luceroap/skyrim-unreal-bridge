@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -Command "if (Get-Process SkyrimSE,UnrealEditor -ErrorAction SilentlyContinue) { exit 1 }"
if errorlevel 1 (
 echo Close Skyrim and Unreal before starting the 30B local model.
 pause
 exit /b 1
)
set "OPENCODE_CLI="
for /f "delims=" %%D in ('dir /b /ad /o-d "%APPDATA%\ai.opencode.desktop\cli" 2^>nul') do if not defined OPENCODE_CLI if exist "%APPDATA%\ai.opencode.desktop\cli\%%D\opencode-cli.exe" set "OPENCODE_CLI=%APPDATA%\ai.opencode.desktop\cli\%%D\opencode-cli.exe"
if not defined OPENCODE_CLI (
 echo Open OpenCode Desktop once to finish installing its local command line tool.
 pause
 exit /b 1
)
echo Local model tasks. First response may take a minute while the model loads.
"%OPENCODE_CLI%" --prompt "Use the read tool to read the first 15 lines of C:/Users/Aidan/SkyrimUnrealBridge/AGENT_BRIEFING.md. Confirm the project and wait for my task. /no_think" "%CD%" %*
pause
