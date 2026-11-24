"""Capture a window's contents even when it is covered (PrintWindow). Usage: python capture_window.py <exe> <out.png>"""
import ctypes, ctypes.wintypes as wt, sys
sys.path.insert(0, r"C:\Users\Aidan\SkyrimUnrealBridge")
from start_bridge import find_window
from PIL import Image

user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
user32.SetProcessDPIAware()
hwnd = find_window(sys.argv[1])
r = wt.RECT(); user32.GetWindowRect(hwnd, ctypes.byref(r))
w, h = r.right - r.left, r.bottom - r.top
hdc = user32.GetWindowDC(hwnd); mdc = gdi32.CreateCompatibleDC(hdc)
bmp = gdi32.CreateCompatibleBitmap(hdc, w, h); gdi32.SelectObject(mdc, bmp)
user32.PrintWindow(hwnd, mdc, 2)
buf = ctypes.create_string_buffer(w * h * 4)
gdi32.GetBitmapBits(bmp, len(buf), buf)
Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1).convert("RGB").save(sys.argv[2])
print("window", r.left, r.top, w, h)
