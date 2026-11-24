import ctypes
cam = live.ues.get_level_viewport_camera_info()[0]
ws = ctypes.string_at(live.pkt + 236, 64).split(b"\0")[0] if live.pkt else None
print("cam", round(cam.y / U), round(cam.x / U), round(cam.z / U), "ws", ws, "interior", getattr(live, "_interior", None))
names = ["landscape_grass_curvedgrassdeadtundra", "landscape_grass_highlandflower"]
print("assets", [unreal.EditorAssetLibrary.does_asset_exist("/Game/Area2/" + n) for n in names])
print("grass state", hasattr(live, "_grass"), "actors", len(live.actors))
