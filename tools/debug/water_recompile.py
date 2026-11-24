import unreal
m = unreal.load_asset('/Game/Area2Tex/M_SkyWater')
unreal.MaterialEditingLibrary.recompile_material(m)
print('recompiled')
