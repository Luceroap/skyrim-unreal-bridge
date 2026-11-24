"""Read-only summary of every UE crash folder (CrashContext + the crash-time log).

python area2/crash_triage/parse_crashes.py > area2/crash_triage/crashes.txt
"""
import os
import re
import sys
import datetime
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CRASHES = os.path.join(ROOT, "unreal", "SkyBridge", "Saved", "Crashes")

FIELDS = ["CrashType", "IsEnsure", "IsAssert", "SecondsSinceStart", "ProcessId",
          "MemoryStats.AvailablePhysical", "MemoryStats.AvailableVirtual",
          "MemoryStats.UsedPhysical", "MemoryStats.UsedVirtual", "MemoryStats.bIsOOM",
          "MemoryStats.OOMAllocationSize"]
INTEREST = re.compile(r"SkyBridgeLive|LogPython|exec_request|Error|Fatal|GPU|D3D|crash|Assertion|"
                      r"Ensure|Unhandled|ACCESS_VIOLATION|Out of memory|OOM|TDR|DXGI|Lumen", re.I)


def gb(v):
    try:
        return "%.1f GB" % (int(v) / 2 ** 30)
    except Exception:
        return v


def main():
    dirs = sorted((d for d in os.listdir(CRASHES)), key=lambda d: os.path.getmtime(os.path.join(CRASHES, d)))
    for d in dirs:
        p = os.path.join(CRASHES, d)
        t = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%H:%M:%S")
        ctx = os.path.join(p, "CrashContext.runtime-xml")
        print("=" * 100)
        print(t, d)
        if os.path.exists(ctx):
            try:
                tree = ET.parse(ctx).getroot().find("RuntimeProperties")
                for f in FIELDS:
                    e = tree.find(f)
                    if e is not None:
                        v = e.text or ""
                        print("  %-32s %s" % (f, gb(v) if "Physical" in f or "Virtual" in f else v))
                msg = (tree.findtext("ErrorMessage") or "").strip().splitlines()
                print("  ErrorMessage:")
                for line in msg[:28]:
                    print("    " + line)
            except Exception as ex:
                print("  (xml parse failed: %s)" % ex)
        logs = [f for f in os.listdir(p) if f.lower().endswith(".log")]
        for lf in logs:
            try:
                with open(os.path.join(p, lf), "r", encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
            except Exception:
                continue
            tail = lines[-400:]
            hits = [l.rstrip() for l in tail if INTEREST.search(l)]
            print("  -- %s (%d lines); last interesting lines:" % (lf, len(lines)))
            for l in hits[-45:]:
                print("    " + l[:260])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
