"""Capture one GPU frame in the live editor (ProfileGPU) and print the expensive passes per GPU queue.
Usage: python tools/gpu_profile.py [min_ms=0.25] [max_depth=6]"""
import os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from start_bridge import ue_exec

LOG = r"C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Saved\Logs\SkyBridge.log"
ROW = re.compile(r"┃[^┃]*?([\d.]+) ms ┃[^┃]*?([\d.]+) ms ┃( +)(.*?)\s*┃")


def main():
    min_ms = float(sys.argv[1]) if len(sys.argv) > 1 else 0.25
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    size = os.path.getsize(LOG)
    ue_exec("import unreal\nunreal.SystemLibrary.execute_console_command(None, 'ProfileGPU')\nprint('ok')", 20)
    time.sleep(6)
    with open(LOG, "rb") as f:
        f.seek(size)
        text = f.read().decode("utf-8", "replace")
    queue = None
    for line in text.splitlines():
        m = re.search(r"LogRHI: Display: (?:GPU Profile for Frame \d+ - )?(\w+ pipeline \d+) - GPU \d+\s*$", line)
        if m:
            queue = m.group(1); print("==", queue); continue
        m = ROW.search(line)
        if not m or queue is None:
            continue
        incl, depth, name = float(m.group(2)), (len(m.group(3)) - 1) // 3, m.group(4)
        if incl >= min_ms and depth <= max_depth and not name.startswith("Frame"):
            print("%7.3f ms %s%s" % (incl, "  " * depth, name[:90]))


if __name__ == "__main__":
    main()
