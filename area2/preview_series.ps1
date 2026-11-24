param([string[]]$Shots = @("6.2 SkyrimClear", "19.9 SkyrimClear", "23.5 SkyrimClear", "13 SkyrimRain", "10 SkyrimFog"))
$env:PYTHONIOENCODING = "utf-8"
Set-Location C:\Users\Aidan\SkyrimUnrealBridge
foreach ($s in $Shots) {
    Set-Content area2\preview.txt $s
    python tools\ue_run.py area2\preview_sky.py 60 | Out-Null
    Start-Sleep 6
    $t = Get-Date
    New-Item -ItemType File area2\shot_request.txt -Force | Out-Null
    for ($i = 0; $i -lt 30; $i++) { Start-Sleep 1; if ((Get-Item shot_ue.png).LastWriteTime -gt $t) { break } }
    $name = "area2\look_" + ($s -replace '[ .]', '_') + ".png"
    Copy-Item shot_ue.png $name
    Write-Output "$s -> $name"
}
Set-Content area2\preview.txt "off"
python tools\ue_run.py area2\preview_sky.py 60 | Out-Null
