import unreal, os, math, struct, zlib, random

at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
SRC = r"C:\Users\Aidan\SkyrimUnrealBridge\area2\tex\water_n.png"

# 1. tileable wave normal map (sum of sines -> height -> normals), written as PNG with the stdlib
if not os.path.exists(SRC):
    N = 256
    H = [[0.0] * N for _ in range(N)]
    rnd = random.Random(7)
    waves = [(rnd.randint(1, 6), rnd.randint(1, 6), rnd.random() * 6.28, 1.0 / (1 + i)) for i in range(14)]
    for y in range(N):
        for x in range(N):
            H[y][x] = sum(a * math.sin(2 * math.pi * (kx * x + ky * y) / N + ph) for kx, ky, ph, a in waves)
    rows = []
    for y in range(N):
        row = bytearray([0])
        for x in range(N):
            dx = H[y][(x + 1) % N] - H[y][x - 1]
            dy = H[(y + 1) % N][x] - H[y - 1][x]
            nx, ny, nz = -dx * 3.0, -dy * 3.0, 1.0
            l = math.sqrt(nx * nx + ny * ny + nz * nz)
            row += bytes([int((nx / l * 0.5 + 0.5) * 255), int((ny / l * 0.5 + 0.5) * 255), int((nz / l * 0.5 + 0.5) * 255)])
        rows.append(bytes(row))
    raw = b"".join(rows)
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", N, N, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    open(SRC, "wb").write(png)

t = unreal.AssetImportTask()
t.filename = SRC; t.destination_path = "/Game/Area2Tex"; t.automated = True; t.replace_existing = True; t.save = True
at.import_asset_tasks([t])
nt = unreal.load_asset("/Game/Area2Tex/water_n")
nt.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
nt.set_editor_property("srgb", False); eal.save_loaded_asset(nt)

# 2. single-layer-water material
path = "/Game/Area2Tex/M_Water"
m = unreal.load_asset(path) if eal.does_asset_exist(path) else at.create_asset("M_Water", "/Game/Area2Tex", unreal.Material, unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(m)
try:
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_SINGLE_LAYER_WATER)
except Exception as e:
    unreal.log_warning("single layer water shading model not settable: %s" % e)
m.set_editor_property("two_sided", True)
col = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -700, -150)
col.set_editor_property("constant", unreal.LinearColor(0.02, 0.09, 0.11, 1.0))
mel.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
rough = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -700, 0)
rough.set_editor_property("r", 0.04)
mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
spec = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -700, 100)
spec.set_editor_property("r", 0.5)
mel.connect_material_property(spec, "", unreal.MaterialProperty.MP_SPECULAR)
uv = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1100, 250)
uv.set_editor_property("u_tiling", 40.0); uv.set_editor_property("v_tiling", 40.0)
pan = mel.create_material_expression(m, unreal.MaterialExpressionPanner, -900, 250)
pan.set_editor_property("speed_x", 0.012); pan.set_editor_property("speed_y", 0.006)
mel.connect_material_expressions(uv, "", pan, "Coordinate")
n = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 250)
n.set_editor_property("texture", nt)
n.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
mel.connect_material_expressions(pan, "", n, "UVs")
mel.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL)
mel.recompile_material(m); eal.save_loaded_asset(m)
unreal.log("WATER material ready, shading model: %s" % m.get_editor_property("shading_model"))

m0 = unreal.load_asset('/Game/Area2/architecture_whiterun_wrbuildings_wrhousebanneredmare01')
unreal.log('NANITE probe enabled=%s' % m0.get_editor_property('nanite_settings').enabled)
