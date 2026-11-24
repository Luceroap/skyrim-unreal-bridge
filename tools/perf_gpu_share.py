"""GPU share per process (SkyrimSE vs UnrealEditor) from the Windows GPU performance counters. Read-only, no editor access.
Usage: python tools/perf_gpu_share.py [seconds=30] [out=area2/perf/gpu_share.json]
Samples '\\GPU Engine(*)\\Utilization Percentage' (summed per pid and engine type) and '\\GPU Process Memory(*)\\Dedicated
Usage' / 'Shared Usage' once per second, then prints mean/p95 per process."""
import json, os, re, subprocess, sys, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_WINDOW = 0x08000000


def names():
    out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True, creationflags=NO_WINDOW).stdout
    pids = {}
    for line in out.splitlines():
        p = [x.strip('"') for x in line.split('","')]
        if len(p) > 1 and p[1].isdigit():
            pids[int(p[1])] = p[0]
    return pids


def main():
    secs = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "area2", "perf", "gpu_share.json")
    ps = ("$c = Get-Counter -Counter '\\GPU Engine(*)\\Utilization Percentage','\\GPU Process Memory(*)\\Dedicated Usage',"
          "'\\GPU Process Memory(*)\\Shared Usage' -SampleInterval 1 -MaxSamples %d -ErrorAction SilentlyContinue;"
          "foreach ($s in $c) { foreach ($x in $s.CounterSamples) { if ($x.CookedValue -gt 0) "
          "{ '{0}|{1}|{2}' -f $s.Timestamp.ToString('HH:mm:ss'), $x.Path, $x.CookedValue } } }" % secs)
    txt = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True,
                         creationflags=NO_WINDOW).stdout
    pidname = names()
    util, mem = {}, {}                       # util[(pid, engtype)][ts] = sum %, mem[(pid, kind)][ts] = bytes
    for line in txt.splitlines():
        try:
            ts, path, val = line.rsplit("|", 2)
            val = float(val)
        except ValueError:
            continue
        m = re.search(r"pid_(\d+)_.*engtype_([^)]*)\)", path)
        if m and "utilization" in path.lower():
            d = util.setdefault((int(m.group(1)), m.group(2)), {})
            d[ts] = d.get(ts, 0.0) + val
            continue
        m = re.search(r"pid_(\d+)_.*\\(dedicated|shared) usage", path.lower())
        if m:
            d = mem.setdefault((int(m.group(1)), m.group(2)), {})
            d[ts] = d.get(ts, 0.0) + val
    nts = max(1, len({ts for d in util.values() for ts in d}))
    res = {"seconds": secs, "samples": nts, "util": [], "mem": []}
    for (pid, eng), d in util.items():
        vals = list(d.values()) + [0.0] * (nts - len(d))
        mean = sum(vals) / nts
        if mean < 0.5:
            continue
        res["util"].append(dict(pid=pid, name=pidname.get(pid, "?"), engine=eng, mean=round(mean, 1),
                                p95=round(sorted(vals)[int(0.95 * (len(vals) - 1))], 1), max=round(max(vals), 1)))
    for (pid, kind), d in mem.items():
        v = statistics.mean(d.values()) / 2 ** 30
        if v > 0.05:
            res["mem"].append(dict(pid=pid, name=pidname.get(pid, "?"), kind=kind, gb=round(v, 2)))
    res["util"].sort(key=lambda r: -r["mean"]); res["mem"].sort(key=lambda r: -r["gb"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(res, open(out, "w"), indent=1)
    print("GPU engine utilisation over %d s (%% of that engine, mean / p95 / max):" % secs)
    for r in res["util"]:
        print("  %-18s %6d %-10s %5.1f / %5.1f / %5.1f" % (r["name"], r["pid"], r["engine"], r["mean"], r["p95"], r["max"]))
    print("GPU memory (GB):")
    for r in res["mem"]:
        print("  %-18s %6d %-9s %6.2f" % (r["name"], r["pid"], r["kind"], r["gb"]))


if __name__ == "__main__":
    main()
