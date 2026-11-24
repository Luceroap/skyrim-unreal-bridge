param([string]$names = "Aela,Carlotta,Mila", [string]$dist = "260", [string]$pre = "root")
$s = "area2\npc_step.txt"
"setup $names $dist" | Set-Content $s; python tools/ue_run.py area2/cap_root.py 60
Start-Sleep 2
"grab $pre" | Set-Content $s; python tools/ue_run.py area2/cap_root.py 60
"done" | Set-Content $s; python tools/ue_run.py area2/cap_root.py 60
python -c "import glob,sys; from PIL import Image; p=sys.argv[1]; fs=sorted(glob.glob(f'area2/{p}_[0-9].png')); ims=[Image.open(f).convert('RGB') for f in fs]; o=Image.new('RGB',(sum(i.width for i in ims),ims[0].height)); x=0
for i in ims: o.paste(i,(x,0)); x+=i.width
o.thumbnail((1400,800)); o.save(f'area2/{p}_all.png')" $pre
