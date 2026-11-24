"""Read-only: for each SkyBridge*.log (current + backups) print start time, end time and the last fatal/GPU/memory lines,
plus the last [SkyBridgeLive] lines before the end. python area2/crash_triage/scan_logs.py > area2/crash_triage/logs.txt"""
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOGS = os.path.join(ROOT, "unreal", "SkyBridge", "Saved", "Logs")
BAD = re.compile(r"Fatal|GPU ?Crash|DXGI_ERROR|DEVICE_REMOVED|DEVICE_HUNG|TDR|timed? ?out|not completed|Breadcrumb|Aftermath|"
                 r"Out of (video )?memory|OutOfMemory|Ran out of memory|LowMemory|Residency|pSet->Open|Assertion failed|"
                 r"Unhandled Exception|EXCEPTION_|Error: === Critical|appError|Request exit|QUIT_EDITOR|Cmd: QUIT|"
                 r"LogWindows: Error|LogD3D12RHI: Error|LogRHI: Error|Memory Stats|Texture pool|over budget|"
                 r"LogMemory|PageFault|commit", re.I)
LIVE = re.compile(r"\[SkyBridgeLive\]")
STAMP = re.compile(r"^\[(\d{4}\.\d\d\.\d\d-\d\d\.\d\d\.\d\d):\d+\]")


def main():
    files = sorted(glob.glob(os.path.join(LOGS, "SkyBridge*.log")), key=os.path.getmtime)
    for f in files:
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        stamps = [m.group(1) for m in (STAMP.match(l) for l in lines[:400]) if m]
        last = [m.group(1) for m in (STAMP.match(l) for l in lines[-400:]) if m]
        print("=" * 100)
        print(os.path.basename(f), "lines", len(lines), "start(UTC)", stamps[0] if stamps else "?", "end(UTC)", last[-1] if last else "?")
        bad = [l.rstrip() for l in lines if BAD.search(l) and "LogRHI: Display:     " not in l]
        for l in bad[-30:]:
            print("  !", l[:300])
        live = [l.rstrip() for l in lines[-3000:] if LIVE.search(l) and "alive:" not in l]
        alive = [l.rstrip() for l in lines if "alive:" in l]
        if alive:
            print("  last heartbeat:", alive[-1][:200])
        for l in live[-12:]:
            print("  >", l[:250])
        print("  -- last 6 lines:")
        for l in lines[-6:]:
            print("    ", l.rstrip()[:250])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
