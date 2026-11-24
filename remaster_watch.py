"""Runs alongside the remaster view (started by `start_bridge.py --remaster`).
- Unreal's view covers Skyrim only while the player is in the world: menus (inventory, wait, map, dialogue, console),
  loading screens and the main menu show Skyrim's own frame. Unreal is also hidden while Skyrim is not the active window.
- Draws a Skyrim-style HUD above Unreal (compass, health/magicka/stamina, crosshair) from the plugin's packet (version 2),
  plus the activation prompt ("E Talk / Aela the Huntress") from packet version 3.
Exits when Skyrim or the editor closes."""
import ctypes, ctypes.wintypes as wt, math, struct, sys, time
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge")
from start_bridge import find_window, running

user32, kernel32, gdi32 = ctypes.windll.user32, ctypes.windll.kernel32, ctypes.windll.gdi32
PKT_FMT = "<4I21f2I64s64s64sI11fI21f"
PKT_SIZE = struct.calcsize(PKT_FMT)
PKT_FMT_V3 = PKT_FMT + "64s"                                             # + crosshair "<verb>\t<name>"
PKT_SIZE_V3 = struct.calcsize(PKT_FMT_V3)
ACTIVATE_KEY = "E"
UI_SHOW_SKYRIM, UI_COMBAT, UI_SNEAK, UI_WEAPON, UI_IN_WORLD = 1, 8, 16, 32, 64

kernel32.OpenFileMappingW.restype = ctypes.c_void_p
kernel32.MapViewOfFile.restype = ctypes.c_void_p
kernel32.MapViewOfFile.argtypes = [ctypes.c_void_p, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_size_t]
user32.DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
user32.DefWindowProcW.restype = ctypes.c_ssize_t
user32.CreateWindowExW.restype = wt.HWND
user32.CreateWindowExW.argtypes = [wt.DWORD, wt.LPCWSTR, wt.LPCWSTR, wt.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, wt.HWND, wt.HMENU, wt.HINSTANCE, wt.LPVOID]
gdi32.CreateDIBSection.restype = wt.HBITMAP
gdi32.CreateDIBSection.argtypes = [wt.HDC, ctypes.c_void_p, wt.UINT, ctypes.POINTER(ctypes.c_void_p), wt.HANDLE, wt.DWORD]
gdi32.SelectObject.argtypes = [wt.HDC, wt.HGDIOBJ]
gdi32.SelectObject.restype = wt.HGDIOBJ
gdi32.DeleteObject.argtypes = [wt.HGDIOBJ]
gdi32.CreateCompatibleDC.restype = wt.HDC
gdi32.CreateCompatibleDC.argtypes = [wt.HDC]
user32.GetDC.argtypes = [wt.HWND]
gdi32.DeleteDC.argtypes = [wt.HDC]
user32.GetDC.restype = wt.HDC
user32.ReleaseDC.argtypes = [wt.HWND, wt.HDC]
user32.UpdateLayeredWindow.argtypes = [wt.HWND, wt.HDC, ctypes.c_void_p, ctypes.c_void_p, wt.HDC, ctypes.c_void_p, wt.DWORD,
                                       ctypes.c_void_p, wt.DWORD]      # (without this the 64-bit HDC overflowed and the HUD process died)


class Packet:
    def __init__(self):
        self.p = None

    def read(self):
        if not self.p:
            h = kernel32.OpenFileMappingW(4, False, "Local\\SkyrimUnrealBridge_v1")
            if not h:
                return None
            self.p = kernel32.MapViewOfFile(h, 4, 0, 0, 0)
        for _ in range(4):
            raw = ctypes.string_at(self.p, PKT_SIZE)
            v = struct.unpack(PKT_FMT, raw)
            if v[1] >= 3:
                v = struct.unpack(PKT_FMT_V3, ctypes.string_at(self.p, PKT_SIZE_V3))
            if v[2] % 2 == 0:
                return v
            time.sleep(0.001)
        return v


WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)
_wndproc = WNDPROC(lambda h, m, w, l: user32.DefWindowProcW(h, m, w, l))


class WNDCLASSW(ctypes.Structure):
    _fields_ = [("style", wt.UINT), ("lpfnWndProc", WNDPROC), ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                ("hInstance", wt.HINSTANCE), ("hIcon", wt.HICON), ("hCursor", wt.HANDLE), ("hbrBackground", wt.HBRUSH),
                ("lpszMenuName", wt.LPCWSTR), ("lpszClassName", wt.LPCWSTR)]


class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [("BlendOp", ctypes.c_ubyte), ("BlendFlags", ctypes.c_ubyte), ("SourceConstantAlpha", ctypes.c_ubyte),
                ("AlphaFormat", ctypes.c_ubyte)]


_registered = False


class Sprite:
    """Click-through, never-activated, always-on-top window showing an RGBA image (per-pixel alpha)."""

    def __init__(self, x, y, w, h):
        global _registered
        hinst = kernel32.GetModuleHandleW(None)
        if not _registered:
            wc = WNDCLASSW(0, _wndproc, 0, 0, hinst, None, None, None, None, "SkyBridgeHUD")
            user32.RegisterClassW(ctypes.byref(wc)); _registered = True
        ex = 0x80000 | 0x20 | 0x8 | 0x80 | 0x08000000      # layered, transparent, topmost, toolwindow, noactivate
        self.hwnd = user32.CreateWindowExW(ex, "SkyBridgeHUD", "SkyBridgeHUD", 0x80000000, x, y, w, h, None, None, hinst, None)
        self.x, self.y, self.w, self.h = x, y, w, h
        self.shown = False

    def update(self, img):
        w, h = img.size
        r, g, b, a = img.split()
        prem = Image.merge("RGBA", (Image.composite(b, Image.new("L", img.size), a), Image.composite(g, Image.new("L", img.size), a),
                                    Image.composite(r, Image.new("L", img.size), a), a))
        bmi = (ctypes.c_uint32 * 10)(40, w, ctypes.c_uint32(-h).value, 1 | (32 << 16), 0, 0, 0, 0, 0, 0)
        bits = ctypes.c_void_p()
        screen = user32.GetDC(None)
        dc = gdi32.CreateCompatibleDC(screen)
        bmp = gdi32.CreateDIBSection(screen, bmi, 0, ctypes.byref(bits), None, 0)
        ctypes.memmove(bits, prem.tobytes(), w * h * 4)
        old = gdi32.SelectObject(dc, bmp)
        size, src, pos = wt.SIZE(w, h), wt.POINT(0, 0), wt.POINT(self.x, self.y)
        blend = BLENDFUNCTION(0, 0, 255, 1)
        user32.UpdateLayeredWindow(self.hwnd, screen, ctypes.byref(pos), ctypes.byref(size), dc, ctypes.byref(src), 0,
                                   ctypes.byref(blend), 2)
        gdi32.SelectObject(dc, old); gdi32.DeleteObject(bmp); gdi32.DeleteDC(dc); user32.ReleaseDC(None, screen)

    def show(self, on):
        if on != self.shown:
            self.shown = on
            user32.ShowWindow(self.hwnd, 4 if on else 0)                 # SW_SHOWNOACTIVATE / SW_HIDE
        if on:
            user32.SetWindowPos(self.hwnd, wt.HWND(-1), 0, 0, 0, 0, 0x0013)


def font(size):
    for f in ("C:/Windows/Fonts/constan.ttf", "C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


class Hud:
    def __init__(self, rect):
        L, T, R, B = rect
        W, H = R - L, B - T
        s = H / 1080.0
        self.s = s
        self.cw, self.ch = int(760 * s), int(44 * s)
        self.compass = Sprite(L + (W - self.cw) // 2, T + int(18 * s), self.cw, self.ch)
        self.bw, self.bh = int(1500 * s), int(40 * s)
        self.bars = Sprite(L + (W - self.bw) // 2, B - int(70 * s), self.bw, self.bh)
        c = max(8, int(14 * s))
        self.cross = Sprite(L + (W - c) // 2, T + (H - c) // 2, c, c)
        self.font = font(int(22 * s)); self.small = font(int(15 * s))
        img = Image.new("RGBA", (c, c), (0, 0, 0, 0))
        d = ImageDraw.Draw(img); r = c / 2
        d.ellipse((r - 2.2 * s, r - 2.2 * s, r + 2.2 * s, r + 2.2 * s), fill=(235, 235, 225, 220), outline=(0, 0, 0, 140))
        self.cross.update(img)
        self.pw, self.ph = int(700 * s), int(110 * s)
        self.prompt = Sprite(L + (W - self.pw) // 2, T + int(H * 0.56), self.pw, self.ph)
        self.big = font(int(30 * s)); self.key = font(int(19 * s))
        self.last_heading = None; self.last_bars = None; self.bars_alpha = 0.0; self.bars_t = 0.0
        self.last_prompt = None

    def draw_compass(self, heading):
        if self.last_heading is not None and abs((heading - self.last_heading + 180) % 360 - 180) < 0.25:
            return
        self.last_heading = heading
        s, w, h = self.s, self.cw, self.ch
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        mid = h * 0.62
        d.line((0, mid, w, mid), fill=(0, 0, 0, 120), width=max(3, int(4 * s)))
        d.line((0, mid, w, mid), fill=(220, 220, 210, 170), width=max(1, int(1.5 * s)))
        span = 100.0                                                      # degrees across the compass
        for deg in range(0, 360, 15):
            off = (deg - heading + 180) % 360 - 180
            if abs(off) > span / 2: continue
            x = w / 2 + off / span * w
            edge = 1.0 - (abs(off) / (span / 2)) ** 3                     # fade towards the ends like Skyrim's
            a = int(255 * edge)
            label = {0: "N", 90: "E", 180: "S", 270: "W"}.get(deg)
            if label:
                tw = d.textlength(label, font=self.font)
                d.text((x - tw / 2 + 1, mid - 30 * s + 1), label, font=self.font, fill=(0, 0, 0, a // 2))
                d.text((x - tw / 2, mid - 30 * s), label, font=self.font, fill=(240, 236, 220, a))
            else:
                d.line((x, mid - 5 * s, x, mid + 5 * s), fill=(220, 220, 210, int(a * 0.7)), width=max(1, int(1.5 * s)))
        d.polygon([(w / 2 - 6 * s, h), (w / 2 + 6 * s, h), (w / 2, h - 7 * s)], fill=(240, 236, 220, 200))
        self.compass.update(img)

    def draw_bars(self, v, flags):
        hp, mp, sp = (v[0], v[1]), (v[2], v[3]), (v[4], v[5])
        frac = [max(0.0, min(1.0, c / m)) if m > 0 else 1.0 for c, m in (hp, mp, sp)]
        busy = (flags & (UI_COMBAT | UI_WEAPON)) or min(frac) < 0.999
        now = time.time()
        if busy: self.bars_t = now
        target = 1.0 if now - self.bars_t < 3.0 else 0.0                  # hide a few seconds after everything is full
        self.bars_alpha += (target - self.bars_alpha) * 0.15
        key = tuple(round(f, 3) for f in frac) + (round(self.bars_alpha, 2),)
        if key == self.last_bars:
            return self.bars_alpha > 0.01
        self.last_bars = key
        s, w, h = self.s, self.bw, self.bh
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        A = self.bars_alpha
        bw, bh, y = 300 * s, 9 * s, h / 2
        for cx, f, col in ((w * 0.12, frac[1], (60, 110, 200)), (w * 0.5, frac[0], (170, 30, 30)), (w * 0.88, frac[2], (60, 150, 60))):
            x0, x1 = cx - bw / 2, cx + bw / 2
            d.rounded_rectangle((x0 - 3 * s, y - bh / 2 - 3 * s, x1 + 3 * s, y + bh / 2 + 3 * s), radius=6 * s,
                                fill=(10, 10, 10, int(150 * A)), outline=(200, 195, 180, int(170 * A)), width=max(1, int(1.2 * s)))
            half = bw / 2 * f                                             # Skyrim's bars shrink towards the centre
            if f > 0:
                d.rectangle((cx - half, y - bh / 2, cx + half, y + bh / 2), fill=col + (int(235 * A),))
        self.bars.update(img)
        return A > 0.01

    def draw_prompt(self, text):
        """Skyrim's activation prompt: the target's name, and under it the key in a box plus the verb."""
        if text == self.last_prompt:
            return bool(text)
        self.last_prompt = text
        if not text:
            return False
        verb, _, name = text.partition("\t")
        if not name:
            verb, name = "", verb
        s, w, h = self.s, self.pw, self.ph
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        while d.textlength(name, font=self.big) > w - 20 * s and len(name) > 4:
            name = name[:-2].rstrip() + "…"
        tw = d.textlength(name, font=self.big)
        y0 = 8 * s
        d.text(((w - tw) / 2 + 2 * s, y0 + 2 * s), name, font=self.big, fill=(0, 0, 0, 170))
        d.text(((w - tw) / 2, y0), name, font=self.big, fill=(245, 242, 230, 255))
        if verb:
            kw = d.textlength(ACTIVATE_KEY, font=self.key)
            vw = d.textlength(verb, font=self.font)
            box = max(kw + 12 * s, 28 * s)
            gap = 10 * s
            x = (w - (box + gap + vw)) / 2
            y = y0 + 48 * s
            d.rounded_rectangle((x, y, x + box, y + 28 * s), radius=4 * s, fill=(10, 10, 10, 150),
                                outline=(225, 220, 205, 220), width=max(1, int(1.5 * s)))
            d.text((x + (box - kw) / 2, y + 3 * s), ACTIVATE_KEY, font=self.key, fill=(245, 242, 230, 255))
            d.text((x + box + gap + 1 * s, y + 1 * s + 1 * s), verb, font=self.font, fill=(0, 0, 0, 160))
            d.text((x + box + gap, y + 1 * s), verb, font=self.font, fill=(225, 220, 205, 240))
        self.prompt.update(img)
        return True

    def frame(self, v, visible):
        if not visible:
            for sp in (self.compass, self.bars, self.cross, self.prompt): sp.show(False)
            return
        rot = v[13:22]
        heading = math.degrees(math.atan2(rot[1], rot[4])) % 360          # camera forward = column 1; X east, Y north
        flags = v[30]
        self.draw_compass(heading); self.compass.show(True)
        self.bars.show(self.draw_bars(v[31:37], flags))
        self.cross.show(True)
        text = v[64].split(b"\0", 1)[0].decode("utf-8", "replace") if len(v) > 64 else ""
        self.prompt.show(self.draw_prompt(text))


def pump():
    msg = wt.MSG()
    while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
        user32.TranslateMessage(ctypes.byref(msg)); user32.DispatchMessageW(ctypes.byref(msg))


def main():
    pkt = Packet()
    hud = None
    shown = None
    last_check = 0
    sky = ue = None
    while True:
        now = time.time()
        if now - last_check > 3:
            last_check = now
            if not running("SkyrimSE.exe") or not running("UnrealEditor.exe"):
                break
            sky, ue = find_window("SkyrimSE.exe"), find_window("UnrealEditor.exe")
            if sky and hud is None:
                r = wt.RECT(); user32.GetWindowRect(sky, ctypes.byref(r))
                hud = Hud((r.left, r.top, r.right, r.bottom))
        v = pkt.read()
        if v is None or not sky or not ue:
            time.sleep(0.2); continue
        flags = v[30] if v[1] >= 2 else (UI_IN_WORLD if v[3] else UI_SHOW_SKYRIM)
        in_world = (flags & UI_IN_WORLD) and not (flags & UI_SHOW_SKYRIM) and v[3] > 0
        visible = bool(in_world and user32.GetForegroundWindow() == sky)
        if visible != shown:
            shown = visible
            user32.SetLayeredWindowAttributes(ue, 0, 255 if visible else 0, 2)
            if visible:
                user32.SetWindowPos(ue, wt.HWND(-1), 0, 0, 0, 0, 0x0013)
        if hud:
            hud.frame(v, visible and v[1] >= 2)
        pump()
        time.sleep(1 / 60)


if __name__ == "__main__":
    main()
