@echo off
rem Codex agent on your HOMELAB server model (sunsetservers, Ollama over Tailscale): small, repetitive jobs only.
rem GTX 1070, ~9 tokens/s, context only 4096: give it ONE function or small file section at a time and add /no_think to prompts.
rem The heavier model on this PC is Codex_Local.bat (qwen3:30b-a3b-64k). No config file is edited: the second provider is passed on the command line.
for /f "delims=" %%i in ('powershell -NoProfile -Command "(Get-ChildItem \"$env:LOCALAPPDATA\OpenAI\Codex\bin\*\codex.exe\" | Sort-Object LastWriteTime | Select-Object -Last 1).FullName"') do set CODEX=%%i
if "%CODEX%"=="" (echo Could not find codex.exe - open the ChatGPT desktop app once so it installs it. & pause & exit /b 1)
"%CODEX%" -C "C:\Users\Aidan\SkyrimUnrealBridge" -s workspace-write -a on-request -m qwen3:14b-gpu ^
  -c model_provider=\"homelab\" ^
  -c model_providers.homelab.name=\"Homelab Ollama\" ^
  -c model_providers.homelab.base_url=\"http://<homelab-tailscale-ip>:11434/v1\" ^
  -c model_providers.homelab.wire_api=\"chat\" ^
  %*
