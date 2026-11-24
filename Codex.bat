@echo off
rem Starts the Codex command-line agent in this project. Safe defaults: it may edit files inside this folder only (workspace-write)
rem and asks before running anything else (on-request). Extra arguments are passed through, e.g.  Codex.bat -m gpt-6-astra
rem Uses the codex.exe that the ChatGPT/Codex desktop app installed (already logged in with your ChatGPT account).
for /f "delims=" %%i in ('powershell -NoProfile -Command "(Get-ChildItem \"$env:LOCALAPPDATA\OpenAI\Codex\bin\*\codex.exe\" | Sort-Object LastWriteTime | Select-Object -Last 1).FullName"') do set CODEX=%%i
if "%CODEX%"=="" (echo Could not find codex.exe - open the ChatGPT desktop app once so it installs it. & pause & exit /b 1)
"%CODEX%" -C "C:\Users\Aidan\SkyrimUnrealBridge" -s workspace-write -a on-request %*
