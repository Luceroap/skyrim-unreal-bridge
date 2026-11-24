import unreal
m = unreal.load_asset("/Game/Area2Tex/M_SkyWater")
mel = unreal.MaterialEditingLibrary
exprs = mel.get_material_expressions(m) if hasattr(mel, "get_material_expressions") else []
from collections import Counter
print("shading", m.get_editor_property("shading_model"), "blend", m.get_editor_property("blend_mode"))
print("expressions", len(exprs), dict(Counter(type(e).__name__ for e in exprs)))
for e in exprs:
    if "SingleLayer" in type(e).__name__:
        print("SLW node", e.get_name())
print("normal connected:", mel.get_material_property_input_node(m, unreal.MaterialProperty.MP_NORMAL))
print("basecolor connected:", mel.get_material_property_input_node(m, unreal.MaterialProperty.MP_BASE_COLOR))
