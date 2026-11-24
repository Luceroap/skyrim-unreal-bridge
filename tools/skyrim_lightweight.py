"""Make the base Skyrim as cheap as possible while Unreal draws the picture. Run while Skyrim is CLOSED (it rewrites SkyrimPrefs.ini on exit).
  python tools/skyrim_lightweight.py          apply (backs up SkyrimPrefs.ini first)
  python tools/skyrim_lightweight.py --undo   restore the backup
Adds to what start_bridge.REMASTER_PROFILE already does (low shadows, no grass, Community Shaders effects off, DLSS performance)."""
import os, re, shutil, subprocess, sys, time

PREFS = r"C:\Users\Aidan\OneDrive\Documents\My Games\Skyrim Special Edition\SkyrimPrefs.ini"
BACKUP = r"C:\Users\Aidan\SkyrimBackups\SkyrimPrefs.pre-lightweight.ini"
# key -> (section, value)
SETTINGS = {
    "fShadowDistance": ("Display", "0.0000"),            # no shadows at all (Unreal draws the shadows)
    "iTexMipMapSkip": ("Display", "3"),                  # eighth-resolution textures (only menus show Skyrim's own picture)
    "iMultiSample": ("Display", "0"),
    "bFXAAEnabled": ("Display", "0"),
    "bUseWaterReflections": ("Water", "0"),
    "bUseWaterRefractions": ("Water", "0"),
    "bUseWaterDisplacements": ("Water", "0"),
    "bUseWaterDepth": ("Water", "0"),
    "iMaxDesired": ("Particles", "120"),
    "iMaxDecalsPerFrame": ("Decals", "5"),
    "iMaxSkinDecalsPerFrame": ("Decals", "2"),
    "bDoDepthOfField": ("Imagespace", "0"),
    "iBlurDeferredShadowMask": ("Display", "0"),
}


def running():
    return "SkyrimSE.exe" in subprocess.run(["tasklist", "/FI", "IMAGENAME eq SkyrimSE.exe"], capture_output=True, text=True).stdout


def set_keys(text, settings):
    lines = text.split("\n")
    for key, (sec, val) in settings.items():
        pat = re.compile(r"^\s*%s\s*=" % re.escape(key), re.I)
        hit = [i for i, l in enumerate(lines) if pat.match(l)]
        if hit:
            for i in hit:
                lines[i] = "%s=%s" % (key, val) + ("\r" if lines[i].endswith("\r") else "")
            continue
        s = next((i for i, l in enumerate(lines) if l.strip().lower() == "[%s]" % sec.lower()), None)
        if s is None:
            lines += ["[%s]\r" % sec, "%s=%s\r" % (key, val)]
        else:
            lines.insert(s + 1, "%s=%s\r" % (key, val))
    return "\n".join(lines)


if running():
    sys.exit("Skyrim is running; close it first (it rewrites its settings when it exits)")
if "--undo" in sys.argv:
    shutil.copy2(BACKUP, PREFS); print("restored", BACKUP); sys.exit()
if not os.path.exists(BACKUP):
    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    shutil.copy2(PREFS, BACKUP)
raw = open(PREFS, "rb").read().decode("utf-8", errors="replace")
open(PREFS, "wb").write(set_keys(raw, SETTINGS).encode("utf-8"))
print("applied %d settings to SkyrimPrefs.ini (backup: %s)" % (len(SETTINGS), BACKUP))
