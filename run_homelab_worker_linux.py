"""Linux entrypoint for the homelab Qwen worker."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import run_local_queue


def free_commit_gb():
    try:
        with open("/proc/meminfo", encoding="ascii") as handle:
            values = {}
            for line in handle:
                name, value, _ = line.split()
                values[name.rstrip(":")] = int(value)
        return values.get("MemAvailable", values.get("MemFree", 0)) / (1024 * 1024)
    except (OSError, ValueError):
        return 999.0


run_local_queue.free_commit_gb = free_commit_gb
run_local_queue.main()
