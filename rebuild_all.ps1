$r='C:\Users\Aidan\SkyrimUnrealBridge'; $d='D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data'
Get-Process UnrealEditor -ea 0 | Stop-Process -Force
python -W ignore -I "$r\tools\auto_build.py" --no-restart-ue *> "$r\rebuild1.log"
python -W ignore -I "$r\tools\esm_land_tex.py" $d "$d\Skyrim.esm" "$r\area2" 'whiterunworld,tamriel' 23000 -6000 14000 4096 *> "$r\rebuild2.log"
$env:FORCE='1'; & 'D:\blender.exe' -b -P "$r\tools\blender_export.py" -- "$r\area2\terrain_obj" "$r\area2\export" *> "$r\rebuild3.log"; Remove-Item Env:FORCE
& D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe "$r\unreal\SkyBridge\SkyBridge.uproject" -run=pythonscript -script="$r\unreal\SkyBridge\import_terrain3.py" -unattended -nullrhi -stdout -FullStdOutLogOutput *> "$r\rebuild4.log"
& D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe "$r\unreal\SkyBridge\SkyBridge.uproject" -run=pythonscript -script="$r\unreal\SkyBridge\fix_slots.py" -unattended -nullrhi -stdout -FullStdOutLogOutput *> "$r\rebuild5.log"
'done' | Set-Content "$r\rebuild_done.txt"
