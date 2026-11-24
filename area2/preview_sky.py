"""area2/preview.txt: '<hour> <weather name>' previews that time/weather in the editor; 'off' returns to Skyrim's."""
a = open(r"C:\Users\Aidan\SkyrimUnrealBridge\area2\preview.txt").read().split()
live._sky_override = None if a[0] == "off" else (float(a[0]), a[1] if len(a) > 1 else "SkyrimClear")
live._sky_key = None
print("override", live._sky_override)
