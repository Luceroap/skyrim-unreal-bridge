"""Run inside the editor (python tools/ue_run.py unreal/SkyBridge/water_flow_apply.py).
1. Rebuilds /Game/Area2Tex/M_SkyWater so its ripples are panned along a PER-INSTANCE flow vector (custom data 0,1 = flow in UE axes).
2. Writes area2/water_flow.csv (tools/water_flow.py) into the instances of the 'CellWater' actor.
Also importable: apply_flow(actor) is used by live_bridge when it spawns the water."""
import os
import unreal

AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
MP = unreal.MaterialProperty


def _n(m, cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def rebuild_water_material():
    m = unreal.load_asset("/Game/Area2Tex/M_SkyWater")
    for e in list(mel.get_material_expressions(m)):
        mel.delete_material_expression(m, e)
    E = unreal
    m.set_editor_property("shading_model", E.MaterialShadingModel.MSM_SINGLE_LAYER_WATER)
    nrm = unreal.load_asset("/Game/Area2Tex/skywater_n")
    wp = _n(m, E.MaterialExpressionWorldPosition, -1900, 0)
    xy = _n(m, E.MaterialExpressionComponentMask, -1700, 0, r=True, g=True, b=False, a=False)
    mel.connect_material_expressions(wp, "", xy, "")
    # per-instance flow (UE axes; 0 = x, 1 = y). Default (0.3, 0.2) keeps non-instanced water (LOD water) moving.
    fx = _n(m, E.MaterialExpressionPerInstanceCustomData, -1900, 300, data_index=0, const_default_value=0.3)
    fy = _n(m, E.MaterialExpressionPerInstanceCustomData, -1900, 450, data_index=1, const_default_value=0.2)
    flow = _n(m, E.MaterialExpressionAppendVector, -1700, 380)
    mel.connect_material_expressions(fx, "", flow, "A"); mel.connect_material_expressions(fy, "", flow, "B")
    normals = []
    # (texture tile in cm, UV units per second per unit flow): ~60 cm/s at full flow for both layers; negative: the texture
    # coordinate increases over time, so the ripple pattern drifts the other way, i.e. along the flow.
    for i, (tile, k) in enumerate(((900.0, -0.07), (2300.0, -0.027))):
        d = _n(m, E.MaterialExpressionDivide, -1500, i * 300, const_b=tile)
        mel.connect_material_expressions(xy, "", d, "A")
        sp = _n(m, E.MaterialExpressionMultiply, -1500, 300 + i * 150, const_b=k)
        mel.connect_material_expressions(flow, "", sp, "A")
        pan = _n(m, E.MaterialExpressionPanner, -1250, i * 300)
        mel.connect_material_expressions(d, "", pan, "Coordinate")
        mel.connect_material_expressions(sp, "", pan, "Speed")
        tx = _n(m, E.MaterialExpressionTextureSample, -1000, i * 300, sampler_type=E.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        if nrm:
            tx.set_editor_property("texture", nrm)
        mel.connect_material_expressions(pan, "", tx, "UVs")
        normals.append(tx)
    add = _n(m, E.MaterialExpressionAdd, -700, 100)
    mel.connect_material_expressions(normals[0], "RGB", add, "A"); mel.connect_material_expressions(normals[1], "RGB", add, "B")
    nn = _n(m, E.MaterialExpressionNormalize, -500, 100)
    mel.connect_material_expressions(add, "", nn, "")
    mel.connect_material_property(nn, "", MP.MP_NORMAL)
    col = _n(m, E.MaterialExpressionConstant3Vector, -500, -200, constant=unreal.LinearColor(0.01, 0.015, 0.015, 1.0))
    mel.connect_material_property(col, "", MP.MP_BASE_COLOR)
    rough = _n(m, E.MaterialExpressionConstant, -500, -80, r=0.03)
    mel.connect_material_property(rough, "", MP.MP_ROUGHNESS)
    out = _n(m, E.MaterialExpressionSingleLayerWaterMaterialOutput, -200, 400)
    sc = _n(m, E.MaterialExpressionConstant3Vector, -500, 350, constant=unreal.LinearColor(0.05, 0.09, 0.075, 1.0))
    ab = _n(m, E.MaterialExpressionConstant3Vector, -500, 480, constant=unreal.LinearColor(1.2, 0.35, 0.25, 1.0))
    mel.connect_material_expressions(sc, "", out, "ScatteringCoefficients")
    mel.connect_material_expressions(ab, "", out, "AbsorptionCoefficients")
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


def apply_flow(actor):
    """actor: the CellWater actor (one InstancedStaticMeshComponent, instances in water_quads.csv order)."""
    c = actor.get_components_by_class(unreal.InstancedStaticMeshComponent)[0]
    rows = [l.split(",") for l in open(os.path.join(AREA, "water_flow.csv")).read().split()]
    n = c.get_instance_count()
    if len(rows) != n:
        return "flow rows %d != instances %d (regenerate water_flow.csv)" % (len(rows), n)
    c.set_num_custom_data_floats(2)
    for i, (fxs, fys, sp) in enumerate(rows):
        s = float(sp)
        last = i == n - 1                                          # only the final write refreshes the render state
        c.set_custom_data_value(i, 0, float(fys) * s, False)      # Skyrim y -> UE x
        c.set_custom_data_value(i, 1, float(fxs) * s, last)       # Skyrim x -> UE y
    return "flow applied to %d strips" % n


def run():
    """Rebuild the material and apply the flow to the live CellWater actor (tools/water_flow_run.py calls this in the editor)."""
    rebuild_water_material()
    out = "no CellWater actor"
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == "CellWater":
            out = apply_flow(a)
    return out
