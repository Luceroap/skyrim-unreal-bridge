@echo off
setlocal
title Skyrim + SkyBridge Standalone

set "SKYRIM_DIR=D:\SteamLibrary\steamapps\common\Skyrim Special Edition"
set "SKYRIM=%SKYRIM_DIR%\skse64_loader.exe"
set "SKYBRIDGE=C:\Users\Aidan\SkyrimUnrealBridge\packaged\SkyBridge_NpcRuntime\Windows\SkyBridge.exe"

if not exist "%SKYRIM%" (
    echo Skyrim SKSE loader was not found:
    echo %SKYRIM%
    pause
    exit /b 1
)

if not exist "%SKYBRIDGE%" (
    echo Packaged SkyBridge was not found:
    echo %SKYBRIDGE%
    pause
    exit /b 1
)

tasklist /FI "IMAGENAME eq SkyrimSE.exe" | find /I "SkyrimSE.exe" >nul
if errorlevel 1 (
    echo Starting Skyrim through SKSE...
    pushd "%SKYRIM_DIR%"
    start "Skyrim SKSE" "%SKYRIM%"
    popd
) else (
    echo Skyrim is already running.
)

echo Waiting for Skyrim to start...
for /l %%N in (1,1,60) do (
    tasklist /FI "IMAGENAME eq SkyrimSE.exe" | find /I "SkyrimSE.exe" >nul
    if not errorlevel 1 goto SkyrimStarted
    timeout /t 2 /nobreak >nul
)

echo Skyrim did not start within 120 seconds.
pause
exit /b 1

:SkyrimStarted
echo Skyrim is running. Wait until your save is fully loaded.
timeout /t 20 /nobreak >nul
echo Starting standalone SkyBridge without UnrealEditor...
start "SkyBridge Standalone" "%SKYBRIDGE%"
echo Aligning SkyBridge over Skyrim...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Overlay_SkyBridge_Standalone.ps1"
echo SkyBridge launched. Keep Skyrim open and do not minimize it.
endlocal
