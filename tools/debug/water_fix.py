import unreal
mel = unreal.MaterialEditingLibrary
m = unreal.load_asset("/Game/Area2Tex/M_SkyWater")
for e in list(mel.get_material_expressions(m)):
    if type(e).__name__ == "MaterialExpressionSingleLayerWaterMaterialOutput":
        mel.delete_material_expression(m, e)
out = mel.create_material_expression(m, unreal.MaterialExpressionSingleLayerWaterMaterialOutput, -100, 400)
sc = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, 350)
sc.set_editor_property("constant", unreal.LinearColor(0.05, 0.09, 0.075, 1.0))
ab = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, 480)
ab.set_editor_property("constant", unreal.LinearColor(1.2, 0.35, 0.25, 1.0))
res = {}
for pin in ("ScatteringCoefficients", "Scattering Coefficients", "Scattering", "Input0", ""):
    res[("sc", pin)] = mel.connect_material_expressions(sc, "", out, pin)
    if res[("sc", pin)]: break
for pin in ("AbsorptionCoefficients", "Absorption Coefficients", "Absorption", "Input1", ""):
    res[("ab", pin)] = mel.connect_material_expressions(ab, "", out, pin)
    if res[("ab", pin)]: break
print("connect results", res)
mel.recompile_material(m)
unreal.EditorAssetLibrary.save_loaded_asset(m)
n = sum(1 for e in mel.get_material_expressions(m) if type(e).__name__ == "MaterialExpressionSingleLayerWaterMaterialOutput")
print("SLW nodes now:", n)
