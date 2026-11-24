# Run in the live editor: python tools/ue_run.py tools/weatherfx_splash.py 120  (rebuilds only M_RainSplash)
import importlib, unreal
import weather_fx
importlib.reload(weather_fx)
m = weather_fx.splash_material(rebuild=True)
print(m.get_editor_property("material_domain"), m.get_editor_property("blend_mode"),
      unreal.MaterialEditingLibrary.get_num_material_expressions(m))
