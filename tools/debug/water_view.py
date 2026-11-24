import unreal, os, math
AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2"
U = 1.4287
# target: river cell (5,-4) south of the Whiterun market; Skyrim units
tx, ty, tz = 22528.0, -14336.0, -4700.0
quads = [l.split(",") for l in open(os.path.join(AREA, "water_quads.csv")).read().split()]
flow = [l.split(",") for l in open(os.path.join(AREA, "water_flow.csv")).read().split()]
w = unreal.EditorLevelLibrary.get_editor_world()
n = 0
for q, f in zip(quads, flow):
    x0, y0, cnt, h = int(q[0]), int(q[1]), int(q[2]), float(q[3])
    cx, cy = x0 + cnt * 64, y0 + 64
    if math.hypot(cx - tx, cy - ty) > 2600 or (n and n % 1 and (x0 // 128 + y0 // 128) % 3):
        continue
    fx, fy, sp = float(f[0]), float(f[1]), float(f[2])
    if sp == 0:
        continue
    a = unreal.Vector(cy * U, cx * U, (h + 25) * U)              # Skyrim (x, y) -> UE (y, x)
    b = unreal.Vector((cy + fy * 260 * sp) * U, (cx + fx * 260 * sp) * U, (h + 25) * U)
    unreal.SystemLibrary.draw_debug_arrow(w, a, b, 90.0, unreal.LinearColor(1, 0.1, 0.1, 1), 120.0, 14.0)
    n += 1
cam = unreal.Vector(ty * U + 3200 * U, tx * U - 2600 * U, (tz + 1900) * U)     # south-west and above, looking at the river
look = unreal.Vector(ty * U, tx * U, tz * U)
rot = unreal.MathLibrary.find_look_at_rotation(cam, look)
live.ues.set_level_viewport_camera_info(cam, rot)
print("arrows", n, "camera", cam, rot)
