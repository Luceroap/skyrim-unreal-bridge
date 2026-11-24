"""One-command launcher for the Skyrim -> Unreal bridge.
    python C:\\Users\\Aidan\\SkyrimUnrealBridge\\start_bridge.py [--no-overlay] [--overlay-only] [--opacity 130]
Starts Skyrim via SKSE (auto-loads your newest save), waits for live data, opens Unreal, then (optionally) turns the Unreal
window into a click-through, semi-transparent, non-focus-stealing overlay over Skyrim. Skyrim must be borderless/windowed."""
import argparse, ctypes, ctypes.wintypes as wt, os, struct, subprocess, sys, time

ROOT = r"C:\Users\Aidan\SkyrimUnrealBridge"
GAME = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition"
UE = r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
# remaster_watch (pythonw, no console) polls these every second: without CREATE_NO_WINDOW each call opened a terminal
# window that stole focus from Skyrim (which pauses when it loses focus)
HIDDEN = 0x08000000


def running(exe):
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + exe], capture_output=True, text=True, creationflags=HIDDEN).stdout
    return exe.lower() in out.lower()


def stream_frame():
    """Frame counter from the plugin's shared memory, or None."""
    kernel32.OpenFileMappingW.restype = ctypes.c_void_p
    kernel32.MapViewOfFile.restype = ctypes.c_void_p
    kernel32.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
    h = kernel32.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_v1")
    if not h:
        return None
    p = kernel32.MapViewOfFile(h, 4, 0, 0, 0)
    magic, ver, seq, frame = struct.unpack("<4I", ctypes.string_at(p, 16))
    kernel32.UnmapViewOfFile(ctypes.c_void_p(p)); kernel32.CloseHandle(ctypes.c_void_p(h))
    return frame


def pids(exe):
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + exe, "/FO", "CSV", "/NH"], capture_output=True, text=True,
                         creationflags=HIDDEN).stdout
    return {int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"' + exe.lower())}


def find_window(exe):
    """Largest visible top-level window owned by a process with this image name (Skyrim's window has an empty title)."""
    want, found = pids(exe), []
    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            pid = wt.DWORD(); user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value in want:
                r = wt.RECT(); user32.GetWindowRect(hwnd, ctypes.byref(r))
                found.append(((r.right - r.left) * (r.bottom - r.top), hwnd))
        return True
    user32.EnumWindows(cb, 0)
    return max(found)[1] if found else None


def overlay(opacity):
    sky, ue = find_window("SkyrimSE.exe"), find_window("UnrealEditor.exe")
    if not sky or not ue:
        print("overlay: could not find both windows"); return
    r = wt.RECT(); user32.GetWindowRect(sky, ctypes.byref(r))
    GWL_STYLE, GWL_EXSTYLE = -16, -20
    st = user32.GetWindowLongW(ue, GWL_STYLE)
    user32.SetWindowLongW(ue, GWL_STYLE, st & ~0x00C00000 & ~0x00040000)                       # no caption / resize frame
    ex = user32.GetWindowLongW(ue, GWL_EXSTYLE)
    user32.SetWindowLongW(ue, GWL_EXSTYLE, ex | 0x80000 | 0x20 | 0x80 | 0x08000000)            # layered, click-through, toolwindow, no-activate
    user32.SetLayeredWindowAttributes(ue, 0, opacity, 2)
    user32.SetWindowPos(ue, wt.HWND(-1), r.left, r.top, r.right - r.left, r.bottom - r.top, 0x0070)  # topmost, no-activate
    user32.SetForegroundWindow(sky)                                                            # Skyrim pauses if it loses focus
    print("overlay applied (%d%% opaque)" % round(opacity / 2.55))


def side_by_side():
    """Unreal fully opaque on the monitor that is NOT showing Skyrim (or right of it), no focus stealing, click-through off."""
    sky, ue = find_window("SkyrimSE.exe"), find_window("UnrealEditor.exe")
    if not ue:
        print("Unreal window not found"); return
    SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN = 76, 77, 78, 79
    vx, vy = user32.GetSystemMetrics(SM_XVIRTUALSCREEN), user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    vw, vh = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN), user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    r = wt.RECT()
    if sky: user32.GetWindowRect(sky, ctypes.byref(r))
    # the free space is whatever part of the virtual desktop lies left of Skyrim's window (or right of it)
    if sky and r.left - vx >= 600:
        x, w = vx, r.left - vx
    elif sky and (vx + vw) - r.right >= 600:
        x, w = r.right, (vx + vw) - r.right
    else:
        x, w = 100, 1280
    h = int(w * 9 / 16)
    st = user32.GetWindowLongW(ue, -16)
    user32.SetWindowLongW(ue, -16, st & ~0x00C00000 & ~0x00040000)
    ex = user32.GetWindowLongW(ue, -20)
    user32.SetWindowLongW(ue, -20, (ex & ~0x20 & ~0x80000) | 0x08000000)          # opaque, clickable, never steals focus
    user32.SetWindowPos(ue, wt.HWND(-2), x, max(vy, 0), w, h, 0x0070)               # not topmost, no-activate
    if sky: user32.SetForegroundWindow(sky)
    print("Unreal placed at x=%d y=%d %dx%d" % (x, max(vy, 0), w, h))


def ue_only():
    """Minimize Skyrim (it keeps running paused) and show Unreal alone, full size, opaque, on Skyrim's monitor."""
    sky, ue = find_window("SkyrimSE.exe"), find_window("UnrealEditor.exe")
    if not ue:
        print("Unreal window not found"); return
    r = wt.RECT()
    if sky:
        user32.GetWindowRect(sky, ctypes.byref(r))
    else:
        r.left, r.top, r.right, r.bottom = 0, 0, 2560, 1440
    st = user32.GetWindowLongW(ue, -16)
    user32.SetWindowLongW(ue, -16, st & ~0x00C00000 & ~0x00040000)
    ex = user32.GetWindowLongW(ue, -20)
    user32.SetWindowLongW(ue, -20, ex & ~0x20 & ~0x80000 & ~0x08000000)          # opaque, clickable, activatable
    if sky: user32.ShowWindow(sky, 6)                                              # SW_MINIMIZE
    user32.SetWindowPos(ue, wt.HWND(-1), r.left, r.top, r.right - r.left, r.bottom - r.top, 0x0040)
    user32.SetForegroundWindow(ue)
    print("Unreal full-size; Skyrim minimized (run with --restore-skyrim to bring it back)")


EXEC_REQ = os.path.join(ROOT, "area2", "exec_request.py")
EXEC_OUT = os.path.join(ROOT, "area2", "exec_out.txt")

EXEC_LOCK = EXEC_REQ + ".lock"


def ue_exec(src, timeout=20):
    """Run a script inside the editor through live_bridge's debug hook; returns its output.
    Callers from several agents share one request/output file pair, so they are serialized with a lock file."""
    wait_end = time.time() + 600
    while True:
        try:
            fd = os.open(EXEC_LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(time.time() + timeout + 15).encode())
            os.close(fd)
            break
        except FileExistsError:
            try:
                txt = open(EXEC_LOCK).read()
                stale = float(txt) < time.time() if txt else time.time() - os.path.getmtime(EXEC_LOCK) > 5
            except FileNotFoundError:
                continue
            except (OSError, ValueError):
                stale = False
            if stale:
                try:
                    os.remove(EXEC_LOCK)
                except OSError:
                    pass
                continue
            if time.time() > wait_end:
                return None
            time.sleep(0.5)
    try:
        return _ue_exec_locked(src, timeout)
    finally:
        try:
            os.remove(EXEC_LOCK)
        except OSError:
            pass


def _ue_exec_locked(src, timeout):
    t0 = os.path.getmtime(EXEC_OUT) if os.path.exists(EXEC_OUT) else 0
    with open(EXEC_REQ, "w") as f:
        f.write(src)
    end = time.time() + timeout
    while time.time() < end:
        time.sleep(0.3)
        if os.path.exists(EXEC_OUT) and os.path.getmtime(EXEC_OUT) > t0:
            return open(EXEC_OUT).read()
    try:
        os.remove(EXEC_REQ)                  # unanswered: never let a later editor session run it
    except OSError:
        pass
    return None


def hide_editor_popups(main):
    """Hide the editor's floating windows (Message Log / Map Check etc.) so they do not sit on top of the game."""
    want = pids("UnrealEditor.exe")

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        pid = wt.DWORD(); user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in want and hwnd != main and user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            t = ctypes.create_unicode_buffer(n + 1); user32.GetWindowTextW(hwnd, t, n + 1)
            if t.value:
                user32.ShowWindow(hwnd, 0)
                print("  hid editor window: " + t.value)
        return True
    user32.EnumWindows(cb, 0)


def focus(hwnd):
    """SetForegroundWindow only works for the process that got the last input; a synthetic Alt tap satisfies that."""
    user32.keybd_event(0x12, 0, 0, 0); user32.keybd_event(0x12, 0, 2, 0)
    user32.SetForegroundWindow(hwnd)


def remaster():
    """Unreal's viewport fullscreen over Skyrim (needs the SkyBridge C++ module). Skyrim keeps focus: play Skyrim, see Unreal."""
    sky, ue = find_window("SkyrimSE.exe"), find_window("UnrealEditor.exe")
    if not sky or not ue:
        print("need both Skyrim and the Unreal editor running"); return False
    s = wt.RECT(); user32.GetWindowRect(sky, ctypes.byref(s))
    hide_editor_popups(ue)
    user32.SetWindowRgn(ue, None, True)
    user32.ShowWindow(ue, 4)                                                       # SW_SHOWNOACTIVATE (un-minimize)
    user32.SetWindowPos(ue, None, s.left + 50, s.top + 50, 1600, 900, 0x0014)      # onto Skyrim's monitor, no z-order/activate
    time.sleep(1.0)
    # off first: the editor restores "windowed fullscreen" from the last session, so setting it again would be a no-op
    out = ue_exec("unreal.SkyBridgeViewLibrary.set_remaster_view(False)\nprint(unreal.SkyBridgeViewLibrary.set_remaster_view(True))")
    if not out or "True" not in out:
        print("editor could not switch to the remaster view: %s" % (out or "no answer (is live_bridge running?)")); return False
    time.sleep(2.0)
    ue = find_window("UnrealEditor.exe")
    ex = user32.GetWindowLongW(ue, -20)
    user32.SetWindowLongW(ue, -20, ex | 0x80000 | 0x20 | 0x80 | 0x08000000)       # layered, click-through, toolwindow, no-activate
    user32.SetLayeredWindowAttributes(ue, 0, 255, 2)
    user32.SetWindowPos(ue, wt.HWND(-1), 0, 0, 0, 0, 0x0013)                      # topmost, keep pos/size, no-activate
    hide_editor_popups(ue)
    focus(sky)
    r = wt.RECT(); user32.GetWindowRect(ue, ctypes.byref(r))
    print("remaster view on: Unreal %d,%d %dx%d over Skyrim %d,%d %dx%d (undo: --remaster-off)"
          % (r.left, r.top, r.right - r.left, r.bottom - r.top, s.left, s.top, s.right - s.left, s.bottom - s.top))
    start_watch()
    return True


def watch_pids():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | ? { $_.CommandLine -match 'remaster_watch' } | % ProcessId"],
                         capture_output=True, text=True, creationflags=HIDDEN).stdout
    return [int(x) for x in out.split()]


def start_watch():
    """Menus/loading show Skyrim, the world shows Unreal, plus the HUD overlay (remaster_watch.py, runs in the background)."""
    for pid in watch_pids():
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    subprocess.Popen([pyw if os.path.exists(pyw) else sys.executable, os.path.join(ROOT, "remaster_watch.py")], cwd=ROOT,
                     creationflags=0x00000008 | 0x00000200)
    print("menu/HUD watcher started (menus show Skyrim, the world shows Unreal)")


def remaster_off():
    for pid in watch_pids():
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    ue = find_window("UnrealEditor.exe")
    if not ue: return
    user32.SetLayeredWindowAttributes(ue, 0, 255, 2)
    ex = user32.GetWindowLongW(ue, -20)
    user32.SetWindowLongW(ue, -20, ex & ~0x20 & ~0x80000 & ~0x80 & ~0x08000000)
    user32.SetWindowPos(ue, wt.HWND(-2), 0, 0, 0, 0, 0x0013)                      # not topmost
    ue_exec("print(unreal.SkyBridgeViewLibrary.set_remaster_view(False))")
    print("remaster view off; editor is a normal window again")


def install_plugin():
    """Copy a newer build of the SKSE plugin into the game (only while Skyrim is closed): back up, test-load, copy."""
    import filecmp, shutil
    src = os.path.join(ROOT, "build", "Release", "SkyrimUnrealBridge.dll")
    dst = os.path.join(GAME, "Data", "SKSE", "Plugins", "SkyrimUnrealBridge.dll")
    if not os.path.exists(src) or (os.path.exists(dst) and (os.path.getmtime(src) <= os.path.getmtime(dst) or filecmp.cmp(src, dst, False))):
        return
    if running("SkyrimSE.exe"):
        print("a newer plugin build is waiting; it is installed the next time Skyrim is started from here"); return
    test = subprocess.run([sys.executable, "-I", "-c", "import ctypes,sys; ctypes.WinDLL(sys.argv[1])", src], capture_output=True, text=True)
    if test.returncode:
        print("new plugin build did not load (Smart App Control?), keeping the installed one:", test.stderr.strip()[-200:]); return
    if os.path.exists(dst):
        bak = os.path.join(r"C:\Users\Aidan\SkyrimBackups", "SkyrimUnrealBridge.%s.dll" % time.strftime("%Y%m%d-%H%M%S"))
        os.makedirs(os.path.dirname(bak), exist_ok=True)
        shutil.copy2(dst, bak)
        print("backed up the installed plugin to " + bak)
    shutil.copy2(src, dst)
    print("installed the new plugin build")


SKYRIM_PREFS = os.path.join(os.environ["USERPROFILE"], r"OneDrive\Documents\My Games\Skyrim Special Edition\SkyrimPrefs.ini")
DISPLAY_TWEAKS = os.path.join(GAME, r"Data\SKSE\Plugins\SSEDisplayTweaks.ini")
COMMUNITY_SHADERS = os.path.join(GAME, r"Data\SKSE\Plugins\CommunityShaders\SettingsUser.json")
PROFILE_BACKUP = r"C:\Users\Aidan\SkyrimBackups\remaster_profile_original.json"
# Skyrim's own frame is hidden under Unreal's, so render it cheaply: it only has to drive the camera and the world stream.
REMASTER_PROFILE = {
    SKYRIM_PREFS: {"iShadowMapResolution": "1024", "fShadowDistance": "2000.0000", "bSAOEnable": "0",
                   "bVolumetricLightingEnable": "0", "bScreenSpaceReflectionEnabled": "0", "bDoDepthOfField": "0",
                   "iTexMipMapSkip": "2",                       # quarter-res textures: frees VRAM for Unreal
                   "fGrassStartFadeDistance": "0.0000",         # no grass (the bridge does not stream it)
                   "bTreesReceiveShadows": "0", "bDrawLandShadows": "0",
                   # distant LOD is never seen (Unreal draws the backdrop); the loaded cells, which the stream needs, are unchanged
                   "fBlockLevel0Distance": "8000.0000", "fBlockLevel1Distance": "16000.0000", "fBlockMaximumDistance": "30000.0000",
                   "fTreeLoadDistance": "8000.0000", "fSplitDistanceMult": "0.5000",
                   "fLODFadeOutMultObjects": "4.0000", "fLODFadeOutMultItems": "2.0000",
                   "bReflectLODObjects": "0", "bReflectLODLand": "0", "bReflectLODTrees": "0", "bReflectSky": "0",
                   "iMaxDesired": "500", "iMaxDecalsPerFrame": "10", "iMaxSkinDecalsPerFrame": "3"},
    # Resolution + BorderlessUpscale froze Skyrim at the main menu. MinimumFramerate: Display Tweaks caps the game step
    # at 1/MinimumFramerate, so with the default 60 and the GPU shared with Unreal (~44 fps) the whole game ran at 74% speed
    # (player moved as if over-encumbered)
    DISPLAY_TWEAKS: {"FramerateLimit": "60", "MinimumFramerate": "20"},
    # Community Shaders: every effect off; DLSS Performance renders Skyrim at a fraction of the resolution (safe, unlike Display Tweaks)
    COMMUNITY_SHADERS: {"Screen Space GI/Enabled": False, "Screen Space GI/EnableGI": False,
                        "Screen Space Shadows/Enable": 0,
                        "Volumetric Lighting/ExteriorEnabled": False, "Volumetric Lighting/InteriorEnabled": False,
                        "Wetness Effects/EnableWetnessEffects": 0, "Wetness Effects/EnableRaindropFx": 0,
                        "Wetness Effects/EnableRipples": 0, "Wetness Effects/EnableSplashes": 0,
                        "Extended Materials/EnableParallax": 0, "Extended Materials/EnableComplexMaterial": 0,
                        "Extended Materials/EnableShadows": 0, "Extended Materials/ExtendShadows": 0,
                        "Extended Materials/EnableTerrain": 0, "Extended Materials/EnableHeightBlending": 0,
                        "Grass Collision/EnableGrassCollision": False, "Terrain Shadows/EnableTerrainShadow": False,
                        "Light Limit Fix/EnableContactShadows": False, "Dynamic Cubemaps/EnabledSSR": 0,
                        "Hair Specular/Enabled": 0, "Terrain Blending/Enabled": 0,
                        "Subsurface Scattering/EnableCharacterLighting": 0,
                        "Upscaling/qualityMode": 3, "Upscaling/frameGenerationMode": 0},
}


# where a key goes if the file does not have it yet
INI_SECTIONS = {"iTexMipMapSkip": "Display", "fBlockLevel0Distance": "TerrainManager", "fBlockLevel1Distance": "TerrainManager",
                "fBlockMaximumDistance": "TerrainManager", "fTreeLoadDistance": "TerrainManager", "fSplitDistanceMult": "TerrainManager",
                "fLODFadeOutMultObjects": "LOD", "fLODFadeOutMultItems": "LOD", "bReflectLODObjects": "Water",
                "bReflectLODLand": "Water", "bReflectLODTrees": "Water", "bReflectSky": "Water", "iMaxDesired": "Particles",
                "iMaxDecalsPerFrame": "Decals", "iMaxSkinDecalsPerFrame": "Decals"}


def set_json(path, values):
    """values: {"Section/Key": value}; returns the previous values (None = was absent)."""
    import json
    d = json.load(open(path, encoding="utf-8"))
    old = {}
    for k, v in values.items():
        sec, key = k.split("/", 1)
        s = d.get(sec)
        if not isinstance(s, dict):
            s = d[sec] = {}
        old[k] = s.get(key)
        s[key] = v
    json.dump(d, open(path, "w", encoding="utf-8"), indent=1)
    return old


def unset_json(path, keys):
    import json
    d = json.load(open(path, encoding="utf-8"))
    for k in keys:
        sec, key = k.split("/", 1)
        if isinstance(d.get(sec), dict):
            d[sec].pop(key, None)
    json.dump(d, open(path, "w", encoding="utf-8"), indent=1)


def set_ini(path, values):
    """Set key=value lines in place (adds missing keys at the end); returns the previous values (None = was absent)."""
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    old, done = {}, set()
    for i, ln in enumerate(lines):
        k = ln.split("=", 1)[0].strip()
        if "=" in ln and not ln.lstrip().startswith(("#", ";")) and k in values and k not in done:
            old[k] = ln.split("=", 1)[1]; lines[i] = "%s=%s" % (k, values[k]); done.add(k)
    for i, ln in enumerate(lines):                                  # a commented-out default sits in the right section
        k = ln.lstrip("#; ").split("=", 1)[0].strip()
        if ln.lstrip().startswith(("#", ";")) and "=" in ln and k in values and k not in done:
            old[k] = None; lines[i] = "%s=%s" % (k, values[k]); done.add(k)
    for k in values:
        if k not in done:
            old[k] = None
            hdr = "[%s]" % INI_SECTIONS.get(k, "")
            at = next((i + 1 for i, ln in enumerate(lines) if ln.strip().lower() == hdr.lower()), None)
            if at is None: lines.append("%s=%s" % (k, values[k]))
            else: lines.insert(at, "%s=%s" % (k, values[k]))
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return old


def unset_ini(path, keys):
    lines = [ln for ln in open(path, encoding="utf-8", errors="replace").read().splitlines()
             if not ("=" in ln and ln.split("=", 1)[0].strip() in keys)]
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def skyrim_profile(on):
    """Apply (on) or undo the low-cost Skyrim render profile. Only while Skyrim is closed; originals kept in PROFILE_BACKUP."""
    import json, shutil
    if running("SkyrimSE.exe"):
        print("Skyrim is running; the render profile is changed the next time it is started from here"); return
    is_json = lambda p: p.lower().endswith(".json")
    if on:
        # applies keys not applied yet, so settings added to REMASTER_PROFILE later also take effect (originals kept once)
        os.makedirs(os.path.dirname(PROFILE_BACKUP), exist_ok=True)
        original = json.load(open(PROFILE_BACKUP)) if os.path.exists(PROFILE_BACKUP) else {}
        stamp = time.strftime("%Y%m%d-%H%M%S")
        changed = 0
        for path, values in REMASTER_PROFILE.items():
            if not os.path.exists(path):
                continue
            new = {k: v for k, v in values.items() if k not in original.get(path, {})}
            if not new:
                continue
            shutil.copy2(path, os.path.join(os.path.dirname(PROFILE_BACKUP), "%s.%s" % (os.path.basename(path), stamp)))
            original.setdefault(path, {}).update(set_json(path, new) if is_json(path) else set_ini(path, new))
            changed += len(new)
        if changed:
            json.dump(original, open(PROFILE_BACKUP, "w"), indent=1)
            print("Skyrim remaster render profile: %d settings applied (Unreal draws the picture); undo: --skyrim-profile-off" % changed)
    elif os.path.exists(PROFILE_BACKUP):
        original = json.load(open(PROFILE_BACKUP))
        for path, values in original.items():
            if is_json(path):
                set_json(path, {k: v for k, v in values.items() if v is not None})
                unset_json(path, [k for k, v in values.items() if v is None])
            else:
                set_ini(path, {k: v for k, v in values.items() if v is not None})
                unset_ini(path, [k for k, v in values.items() if v is None])
        os.remove(PROFILE_BACKUP)
        print("Skyrim render settings restored")


def restore_skyrim():
    sky = find_window("SkyrimSE.exe")
    if sky:
        user32.ShowWindow(sky, 9); user32.SetForegroundWindow(sky)
    print("Skyrim restored")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ue-only", action="store_true", help="minimize Skyrim and show only Unreal")
    ap.add_argument("--restore-skyrim", action="store_true")
    ap.add_argument("--no-overlay", action="store_true")
    ap.add_argument("--skyrim-only", action="store_true", help="start Skyrim + bridge only; do not launch the old game-mode Unreal")
    ap.add_argument("--overlay-only", action="store_true")
    ap.add_argument("--side-by-side", action="store_true", help="Unreal opaque beside Skyrim instead of over it")
    ap.add_argument("--opacity", type=int, default=130)
    ap.add_argument("--remaster", action="store_true", help="show only the Unreal viewport, exactly over Skyrim (play Skyrim, see Unreal)")
    ap.add_argument("--remaster-off", action="store_true")
    ap.add_argument("--skyrim-profile-off", action="store_true", help="restore Skyrim's own graphics settings")
    ap.add_argument("--full-skyrim-graphics", action="store_true", help="do not apply the low-cost Skyrim profile at launch")
    a = ap.parse_args()
    if a.skyrim_profile_off:
        skyrim_profile(False); return
    if a.remaster:
        remaster(); return
    if a.remaster_off:
        remaster_off(); return
    if a.ue_only:
        ue_only(); return
    if a.restore_skyrim:
        restore_skyrim(); return
    if a.side_by_side:
        side_by_side(); return
    if a.overlay_only:
        overlay(a.opacity); return

    install_plugin()
    if not a.full_skyrim_graphics:
        skyrim_profile(True)
    if not running("SkyrimSE.exe"):
        for attempt in range(2):
            subprocess.Popen([os.path.join(GAME, "skse64_loader.exe")], cwd=GAME)
            time.sleep(22)
            if running("SkyrimSE.exe"):
                break
            subprocess.run(["taskkill", "/F", "/IM", "SkyrimSELauncher.exe"], capture_output=True)   # Bethesda launcher got in the way
            time.sleep(2)
    print("waiting for Skyrim to stream data...")
    t0 = time.time()
    while time.time() - t0 < 360:
        f = stream_frame()
        if f:
            break
        if not running("SkyrimSE.exe"):
            sys.exit("Skyrim exited (no data). Check the SKSE log / crash logs; see README.")
        time.sleep(4)
    else:
        sys.exit("No data from the plugin (blocked by Smart App Control? see README).")
    print("Skyrim is streaming (frame %d). Give it ~30 s to settle before dumping references." % f)

    if not running("UnrealEditor.exe") and not a.skyrim_only:
        subprocess.Popen([UE, os.path.join(ROOT, "unreal", "SkyBridge", "SkyBridge.uproject"), "-game", "-windowed", "-ResX=1280", "-ResY=720"])
        for _ in range(60):
            time.sleep(3)
            if find_window("UnrealEditor.exe"):
                break
        time.sleep(30)  # let it load assets before the overlay resizes it
    if not a.no_overlay:
        overlay(a.opacity)
    print("bridge running")


if __name__ == "__main__":
    main()
