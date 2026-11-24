"""Package source snapshots and the task worker for an Ubuntu server."""
import hashlib, json, pathlib, shutil, subprocess, sys, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]

def build():
    tasks = json.loads((ROOT / "notes/homelab_batch_tasks.json").read_text(encoding="utf-8"))
    bundle = ROOT / "logs/homelab_server_bundle/skybridge-worker"
    bundle.mkdir(parents=True, exist_ok=True)
    worker = (ROOT / "tools/run_bridge_batch.py").read_text(encoding="utf-8")
    worker = worker.replace("import argparse, ctypes, hashlib, json, msvcrt, os, pathlib, subprocess, time, urllib.request", "import argparse, ctypes, hashlib, json, os, pathlib, subprocess, time, urllib.request\nif os.name == 'nt':\n    import msvcrt\nelse:\n    import fcntl")
    worker = worker.replace("ROOT = pathlib.Path(__file__).resolve().parents[1]", "ROOT = pathlib.Path(__file__).resolve().parent")
    worker = worker.replace("http://<homelab-tailscale-ip>:11434/api/chat", "http://127.0.0.1:11434/api/chat")
    worker = worker.replace("def free_commit():\n", "def free_commit():\n    if os.name != 'nt':\n        info = dict((parts[0].rstrip(':'), int(parts[1])) for parts in (line.split() for line in pathlib.Path('/proc/meminfo').read_text().splitlines()) if len(parts) >= 2 and parts[1].isdigit())\n        return info.get('MemAvailable', info.get('MemFree', 0)) / 1024**2\n")
    worker = worker.replace("try: msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)", "try:\n            if os.name == 'nt': msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)\n            else: fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)")
    worker = worker.replace('if STOP.exists(): raise SystemExit("STOP_BRIDGE_BATCH exists; use --resume to continue")', 'if STOP.exists():\n            print("Stop marker present; use --resume to continue"); return')
    marker = '        state.update(pid=os.getpid(), model=MODEL'
    wait = """        for attempt in range(120):
            if STOP.exists(): return
            try:
                with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5) as response:
                    installed = json.load(response).get("models", [])
                if not any(m.get("name") == MODEL for m in installed):
                    raise SystemExit("Required model is not installed: " + MODEL)
                break
            except OSError:
                time.sleep(5)
        else: raise SystemExit("Ollama did not become ready")
"""
    assert marker in worker
    worker = worker.replace(marker, wait + marker)
    compile(worker, "worker.py", "exec")
    (bundle / "worker.py").write_text(worker, encoding="utf-8")
    notes = bundle / "notes"; notes.mkdir(exist_ok=True)
    (notes / "homelab_batch_tasks.json").write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    copied = {}
    for rel in sorted({s["path"] for t in tasks for s in t["sources"]}):
        source = (ROOT / rel).resolve()
        if not source.is_relative_to(ROOT.resolve()): raise ValueError("Source outside project")
        dest = bundle / rel; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        copied[rel] = hashlib.sha256(dest.read_bytes()).hexdigest()
    progress = ROOT / "notes/homelab_batch_progress.json"
    state = json.loads(progress.read_text()) if progress.exists() else {"tasks": {}}
    transferred = {}
    for task_id, result in state.get("tasks", {}).items():
        if result.get("state") != "needs_review": continue
        report = ROOT / "notes/homelab_batch" / (task_id + ".md")
        if not report.exists(): continue
        dest = notes / "homelab_batch" / report.name; dest.parent.mkdir(exist_ok=True)
        shutil.copy2(report, dest)
        result = dict(result); result["report"] = "notes/homelab_batch/" + report.name
        transferred[task_id] = result
    (notes / "homelab_batch_progress.json").write_text(json.dumps({"tasks": transferred, "state": "ready", "total": len(tasks)}, indent=2), encoding="utf-8")
    (bundle / "snapshot.json").write_text(json.dumps({"tasks": len(tasks), "files": copied}, indent=2), encoding="utf-8")
    service = """[Unit]
Description=Skyrim bridge homelab task worker

[Service]
Type=exec
WorkingDirectory=%h/skybridge-worker
ExecStart=/usr/bin/python3 %h/skybridge-worker/worker.py --homelab
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=30

[Install]
WantedBy=default.target
"""
    (bundle / "skybridge-worker.service").write_text(service, encoding="utf-8")
    (bundle / "INSTALL.txt").write_text("""Install under ~/skybridge-worker on Ubuntu. Requires existing python3 and Ollama with qwen3:14b-gpu. The worker downloads nothing.
Copy skybridge-worker.service to ~/.config/systemd/user/.
Ensure lingering is enabled for the login user, then run:
  systemctl --user daemon-reload
  systemctl --user enable --now skybridge-worker.service
Check:
  systemctl --user status skybridge-worker.service --no-pager
  python3 ~/skybridge-worker/worker.py --homelab --status
Stop:
  systemctl --user stop skybridge-worker.service
Results: ~/skybridge-worker/notes/homelab_batch/.
This copy uses local source snapshots and does not edit the live PC project or run game tests.
Do not run PC and server dispatchers simultaneously; transfer fresh progress at cutover.
""", encoding="utf-8")
    assert len(tasks) == 600
    assert all((bundle / s["path"]).is_file() for t in tasks for s in t["sources"])
    check = subprocess.run([sys.executable, str(bundle / "worker.py"), "--homelab", "--status"], capture_output=True, text=True)
    if check.returncode: raise RuntimeError(check.stderr)
    assert json.loads(check.stdout)["total"] == 600
    archive = ROOT / "logs/skybridge_homelab_worker.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for path in bundle.rglob("*"):
            if path.is_file(): z.write(path, path.relative_to(bundle.parent))
    return {"archive": str(archive), "bytes": archive.stat().st_size, "source_files": len(copied), "tasks": len(tasks), "completed_transferred": len(transferred)}

if __name__ == "__main__": print(json.dumps(build()))
