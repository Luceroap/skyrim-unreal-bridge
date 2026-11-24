# Starts Skyrim (via SKSE, auto-loads your newest save), waits for live data, then opens the Unreal window.
# Run from PowerShell: C:\Users\Aidan\SkyrimUnrealBridge\start_bridge.ps1
# (If your execution policy blocks scripts, that is your setting to change; or paste the steps below by hand.)
$root = 'C:\Users\Aidan\SkyrimUnrealBridge'
$game = 'D:\SteamLibrary\steamapps\common\Skyrim Special Edition'

function Test-Stream {
    $out = python -I -u "$root\tools\read_bridge.py" 2>&1 | Select-Object -First 1
    return ($out -match '^frame=(\d+)' -and [int]$Matches[1] -gt 0)
}

if (-not (Get-Process SkyrimSE -ErrorAction SilentlyContinue)) {
    Start-Process "$game\skse64_loader.exe" -WorkingDirectory $game
    Start-Sleep 20
    if (-not (Get-Process SkyrimSE -ErrorAction SilentlyContinue)) {   # Bethesda launcher window got in the way
        Get-Process SkyrimSELauncher -ErrorAction SilentlyContinue | Stop-Process -Force
        Start-Sleep 2
        Start-Process "$game\skse64_loader.exe" -WorkingDirectory $game
    }
}
Write-Host 'Waiting for Skyrim to stream data...'
for ($i = 0; $i -lt 90 -and -not (Test-Stream); $i++) { Start-Sleep 4 }
if (-not (Test-Stream)) { Write-Host 'No data from Skyrim (plugin blocked by Smart App Control? see README).'; exit 1 }

if (-not (Get-Process UnrealEditor -ErrorAction SilentlyContinue)) {
    Start-Process 'D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList "`"$root\unreal\SkyBridge\SkyBridge.uproject`"",'-game','-windowed','-ResX=1280','-ResY=720'
}
Write-Host 'Bridge running.'
