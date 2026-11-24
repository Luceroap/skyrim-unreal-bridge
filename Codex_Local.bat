@echo off
rem Codex agent driven by YOUR LOCAL model (Ollama, qwen3:30b-a3b, 64k context): free, no ChatGPT login or usage limit needed.
rem Same safe defaults as Codex.bat: may edit files inside this project only (workspace-write), asks before anything else.
rem Close Skyrim and the Unreal editor first: the model needs ~18 GB of GPU/system memory.  Extra args pass through, e.g. -m qwen3:30b-a3b-128k
for /f "delims=" %%i in ('powershell -NoProfile -Command "(Get-ChildItem \"$env:LOCALAPPDATA\OpenAI\Codex\bin\*\codex.exe\" | Sort-Object LastWriteTime | Select-Object -Last 1).FullName"') do set CODEX=%%i
if "%CODEX%"=="" (echo Could not find codex.exe - open the ChatGPT desktop app once so it installs it. & pause & exit /b 1)
"%CODEX%" --oss --local-provider ollama -m qwen3:30b-a3b-64k -C "C:\Users\Aidan\SkyrimUnrealBridge" -s workspace-write -a on-request %*
