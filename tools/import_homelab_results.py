"""Bring the homelab server's finished work back into the project:  python tools/import_homelab_results.py [--dry-run]   (no zip needed)
Zips are kept in notes/homelab_inbox/ (done/ after import), never in Downloads. Receive the zip from the server with:  tailscale file get <folder>   (the server sends it with `tailscale file cp results_*.zip desktop-oo4qcjn:`).
  * outputs (staging/..., notes/...) are copied to the same relative paths in the project (existing identical files are left alone)
  * tasks that finished OK are recorded in notes/progress_homelab_server.json, so no PC worker repeats them
  * tasks the server gave up on after 3 tries go to notes/needs_better_model/<id>.json; notes/needs_better_model/INDEX.md lists them for a stronger model or a person"""
import json, os, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
dry = "--dry-run" in sys.argv
INBOX = "notes/homelab_inbox"
args = [a for a in sys.argv[1:] if not a.startswith("--")]


def collect():
    """No argument: pull anything the server sent (tailscale file get) and sweep stray results_*.zip out of Downloads into the project inbox."""
    import glob, shutil, subprocess
    os.makedirs(INBOX + "/done", exist_ok=True)
    try:
        subprocess.run(["tailscale", "file", "get", "--conflict=rename", INBOX], capture_output=True, timeout=60, creationflags=0x08000000)
    except Exception:
        pass
    for f in glob.glob(os.path.join(os.path.expanduser("~"), "Downloads", "results_*.zip")):
        shutil.move(f, os.path.join(INBOX, os.path.basename(f)))
    return sorted(glob.glob(INBOX + "/results_*.zip"))


zips = args or collect()
if not zips:
    sys.exit("nothing to import (inbox %s is empty)" % INBOX)
if len(zips) > 1 or not args:
    import subprocess
    for z in zips:
        subprocess.run([sys.executable, os.path.abspath(__file__), z] + (["--dry-run"] if dry else []), check=False)
        if not dry and os.path.dirname(os.path.abspath(z)) == os.path.abspath(INBOX):
            os.replace(z, os.path.join(INBOX, "done", os.path.basename(z)))
    sys.exit(0)
zp = zips[0]
if not os.path.exists(zp):
    sys.exit("usage: python tools/import_homelab_results.py [RESULTS.zip] [--dry-run]")
SAFE_ROOTS = ("staging/", "notes/")
copied = same = skipped = parked = 0
prog = {}
if os.path.exists("notes/progress_homelab_server.json"):
    prog = json.load(open("notes/progress_homelab_server.json"))
os.makedirs("notes/needs_better_model", exist_ok=True)
with zipfile.ZipFile(zp) as z:
    for name in z.namelist():
        data = z.read(name)
        if name == "progress.jsonl":
            for l in data.decode("utf-8", "replace").splitlines():
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                if r.get("ok"):
                    prog[r["id"]] = dict(ok=True, at=r.get("at", ""), worker="homelab-server")
            continue
        if name.startswith("needs_better_model/"):
            dest = "notes/" + name
            if not name.endswith("/"):
                parked += 1
                if not dry:
                    open(dest, "wb").write(data)
            continue
        rel = name.replace("\\", "/")
        if ".." in rel.split("/") or not rel.startswith(SAFE_ROOTS):       # never write outside staging/ or notes/
            skipped += 1
            continue
        if os.path.exists(rel) and open(rel, "rb").read() == data:
            same += 1
            continue
        copied += 1
        if not dry:
            os.makedirs(os.path.dirname(rel), exist_ok=True)
            open(rel, "wb").write(data)
if not dry:
    json.dump(prog, open("notes/progress_homelab_server.json", "w"), indent=1)
    rows = []
    for f in sorted(os.listdir("notes/needs_better_model")):
        if f.endswith(".json"):
            try:
                d = json.load(open("notes/needs_better_model/" + f, encoding="utf-8"))
                last = (d.get("attempts") or [{}])[-1].get("why", "")
                rows.append("- `%s` -> wanted `%s` | %s" % (d["id"], d["wanted_output"], last))
            except Exception:
                pass
    open("notes/needs_better_model/INDEX.md", "w", encoding="utf-8").write(
        "# Tasks that a small model could not do (3 failed attempts each)\n\nEach file has the full prompt (with the code already pasted in), what went wrong and the last answer. "
        "Do these with a stronger model, or by hand, and write the result to the path in `wanted_output`.\n\n" + "\n".join(rows) + "\n\nTotal: %d\n" % len(rows))
print("%s: %d files copied, %d unchanged, %d skipped (outside staging/notes), %d marked done, %d parked for a better model"
      % ("DRY RUN" if dry else "imported", copied, same, skipped, len([1 for v in prog.values() if v.get("worker") == "homelab-server"]), parked))
