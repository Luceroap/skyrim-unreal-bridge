"""Visible top-level windows: title, process, pid."""
import ctypes, ctypes.wintypes as wt, subprocess
u = ctypes.windll.user32
k = ctypes.windll.kernel32
out = []
def cb(h, _):
    if u.IsWindowVisible(h) and not u.IsIconic(h) or u.IsWindowVisible(h):
        n = u.GetWindowTextLengthW(h)
        if n:
            b = ctypes.create_unicode_buffer(n + 1); u.GetWindowTextW(h, b, n + 1)
            pid = wt.DWORD(); u.GetWindowThreadProcessId(h, ctypes.byref(pid))
            hp = k.OpenProcess(0x1000, False, pid.value); name = ""
            if hp:
                buf = ctypes.create_unicode_buffer(512); sz = wt.DWORD(512)
                if k.QueryFullProcessImageNameW(hp, 0, buf, ctypes.byref(sz)): name = buf.value.split("\\")[-1]
                k.CloseHandle(hp)
            out.append((name, pid.value, "min" if u.IsIconic(h) else "", b.value[:90]))
    return True
u.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)(cb), 0)
for o in sorted(out): print("%-28s %6d %-3s %s" % o)
