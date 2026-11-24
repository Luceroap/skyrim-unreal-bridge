"""Build the bundle for the homelab server:  python tools/make_server_bundle.py [--send]
Resolves every not-yet-done tiny task (kinds H,K,M,X,N,T,Y,U,A,B,G) into a ready-to-send prompt (code excerpts already pasted in) and packs them with
tools/server_worker.py, a systemd unit and install notes into logs/homelab_bundle/homelab_worker_bundle.zip.  --send pushes the zip to the server
with Tailscale file transfer (Taildrop): on the server it is received with `tailscale file get <folder>`."""
import json, os, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import run_local_queue as R

KINDS = ("H_", "K_", "M_", "X_", "N_", "T_", "Y_", "U_", "A_", "B_", "G_")
OUT = os.path.join(ROOT, "logs", "homelab_bundle")
os.makedirs(OUT, exist_ok=True)
R.CAP = 4500
tasks = json.load(open("notes/queue.json", encoding="utf-8"))
done = R.all_progress()
todo = [t for t in tasks if t["id"].startswith(KINDS) and not done.get(t["id"], {}).get("ok")]
lines, skipped = [], 0
for t in todo:
    try:
        prompt = R.RULES_THINK_OFF + R.RULES + t["prompt"] + "\n\nPASTED MATERIAL (real, current):" + R.material(t)
    except Exception:
        skipped += 1
        continue
    lines.append(json.dumps(dict(id=t["id"], out=t["out"], min_bytes=t.get("min_bytes", 8), prompt=prompt)))
service = """[Unit]
Description=Skyrim bridge tiny-task worker (local Ollama, qwen3:14b-gpu)
After=network-online.target ollama.service

[Service]
Type=simple
User=@USER@
WorkingDirectory=@DIR@
ExecStart=/usr/bin/python3 @DIR@/worker.py
Restart=always
RestartSec=30
Nice=10

[Install]
WantedBy=multi-user.target
"""
readme = """HOMELAB WORKER BUNDLE
=====================
tasks.jsonl   %d ready-made prompts (code excerpts already pasted in). The worker needs nothing else from the PC.
worker.py     stdlib-only worker: python3 worker.py | --status | --pack
homelab-worker.service   systemd unit template (replace @USER@ and @DIR@)

Install (summary): unzip into a folder, read worker.py, fill in and enable the unit (systemctl enable --now homelab-worker), check `python3 worker.py --status`.
Results: `python3 worker.py --pack` makes results_<time>.zip; send it to the PC with `tailscale file cp results_*.zip desktop-oo4qcjn:`.
It only talks to Ollama on 127.0.0.1:11434, only writes inside its own folder, never deletes anything else, and keeps one task in flight (the GPU has one slot).
""" % len(lines)
zp = os.path.join(OUT, "homelab_worker_bundle.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("homelab_worker/tasks.jsonl", "\n".join(lines) + "\n")
    z.write(os.path.join(ROOT, "tools", "server_worker.py"), "homelab_worker/worker.py")
    z.writestr("homelab_worker/homelab-worker.service", service)
    z.writestr("homelab_worker/README.txt", readme)
print("bundle: %d tasks (%d unresolvable, skipped) -> %s (%.1f MB)" % (len(lines), skipped, zp, os.path.getsize(zp) / 1e6))
if "--send" in sys.argv:
    r = subprocess.run([r"C:\Program Files\Tailscale\tailscale.exe", "file", "cp", zp, "sunsetservers:"], capture_output=True, text=True)
    print("taildrop:", (r.stdout + r.stderr).strip() or "sent", "(exit %d)" % r.returncode)
