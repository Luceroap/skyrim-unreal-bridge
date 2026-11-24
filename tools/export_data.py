"""Exact exports of project data as CSV into staging/exports/ (no LLM):   python tools/export_data.py
  symbols.csv  every Python symbol (file,line,name,docstring)      todo.csv  TODO/FIXME comments (file,line,text)
  hardcoded_paths.csv  absolute Windows paths in source (file,line,drive,path)
  mesh_index.csv  asset name -> nif path (area2/mesh_index.json)   ready_models.csv  models converted and ready (area2/ready.txt)
  spaced_models.csv  models skipped because of a space in the path  scripts.csv  every launcher/script entry point"""
import csv, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = "staging/exports"
os.makedirs(OUT, exist_ok=True)


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print("%-22s %d rows" % (name, len(rows)))


try:
    sym = json.load(open("notes/index/symbols.json"))
    write("symbols.csv", ["file", "line", "name", "docstring"], [(f, a, b, c) for f in sorted(sym) for a, b, c in sym[f]])
except Exception as e:
    print("symbols.csv skipped (run tools/make_project_index.py first):", e)
try:
    rows = []
    for l in open("notes/index/TODO.md", encoding="utf-8"):
        m = re.match(r"- (.+?):(\d+)\s\s(.*)", l.rstrip())
        if m:
            rows.append(m.groups())
    write("todo.csv", ["file", "line", "text"], rows)
except Exception as e:
    print("todo.csv skipped:", e)

SKIP = (".git", "build", "deps", "notes", "staging", "screenshots", "logs", "export", "obj", "tex", "nif", "Content", "Intermediate", "Saved", "Binaries", "__pycache__")
rx = re.compile(r"([A-Za-z]):[\\/]+[^\s'\"<>|*?]{3,}")
paths = []
for dp, dn, fn in os.walk("."):
    dn[:] = [d for d in dn if d not in SKIP and not d.endswith("old_before_move")]
    for f in fn:
        if f.endswith((".py", ".cpp", ".h", ".bat", ".ps1")):
            p = os.path.join(dp, f)
            try:
                for i, l in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                    for m in rx.finditer(l):
                        paths.append((p[2:].replace("\\", "/"), i, m.group(1).upper(), m.group(0)[:200]))
            except OSError:
                pass
write("hardcoded_paths.csv", ["file", "line", "drive", "path"], paths)

try:
    mi = json.load(open("area2/mesh_index.json"))
    items = mi.items() if isinstance(mi, dict) else enumerate(mi)
    write("mesh_index.csv", ["asset", "nif"], [(k, v if isinstance(v, str) else json.dumps(v)) for k, v in items])
except Exception as e:
    print("mesh_index.csv skipped:", e)
if os.path.exists("area2/ready.txt"):
    write("ready_models.csv", ["model"], [(l.strip(),) for l in open("area2/ready.txt", encoding="utf-8", errors="replace") if l.strip()])
if os.path.exists("area2/spaced_models.txt"):
    rows = []
    for l in open("area2/spaced_models.txt", encoding="utf-8", errors="replace"):
        if l.strip() and not l.startswith("#"):
            rows.append(l.rstrip("\n").split("\t")[:2])
    write("spaced_models.csv", ["asset", "nif"], rows)
rows = []
for dp, dn, fn in os.walk("."):
    dn[:] = [d for d in dn if d not in SKIP and not d.endswith("old_before_move") and d not in ("area2", "unreal")]
    for f in fn:
        if f.endswith((".bat", ".ps1")) or (f.endswith(".py") and dp in (".", ".\\tools")):
            rows.append((os.path.join(dp, f)[2:].replace("\\", "/"), os.path.getsize(os.path.join(dp, f))))
write("scripts.csv", ["file", "bytes"], sorted(rows))
