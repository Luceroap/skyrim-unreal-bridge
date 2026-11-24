# Run in the live editor: python tools/ue_run.py tools/weatherfx_build.py 120
# Builds /Game/WeatherFX assets (rebuild=True recompiles both materials) and reports compile errors.
import importlib, unreal
import weather_fx
importlib.reload(weather_fx)
snow, splash = weather_fx.build(rebuild=True)
for m in (snow, splash):
    errs = []
    try:
        errs = unreal.MaterialEditingLibrary.get_material_compile_errors(m) if hasattr(unreal.MaterialEditingLibrary, "get_material_compile_errors") else []
    except Exception as e:
        errs = [str(e)]
    print(m.get_path_name(), "nodes", unreal.MaterialEditingLibrary.get_num_material_expressions(m), "errors", list(errs))
