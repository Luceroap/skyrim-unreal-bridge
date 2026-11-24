# Run in the live editor: recompile the WeatherFX materials and list their expression classes.
import collections, unreal
mel = unreal.MaterialEditingLibrary
for p in ("/Game/WeatherFX/M_SnowFlakes", "/Game/WeatherFX/M_RainSplash"):
    m = unreal.load_asset(p)
    mel.recompile_material(m)
    ex = []
    try:
        ex = list(m.get_editor_property("expressions") or [])
    except Exception:
        try:
            ex = list(m.get_editor_only_data().get_editor_property("expression_collection").get_editor_property("expressions"))
        except Exception as e:
            print("no expression list:", e)
    print(p, mel.get_num_material_expressions(m), dict(collections.Counter(type(e).__name__ for e in ex)))
