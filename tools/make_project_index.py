"""Exact (non-LLM) project index for the agent team -> notes/index/*.md and notes/index/symbols.json.   python tools/make_project_index.py
Everything here is extracted with ast/regex, so it is reliable; the local model's notes (notes/files/) add the explanations.
  SYMBOLS.md      every Python class/function: file:line, signature, first docstring line
  CPP.md          every C++ function/struct in plugin/ and unreal/SkyBridge/Source, with line numbers
  IMPORTS.md      which project module imports which, plus modules nobody imports
  ENTRYPOINTS.md  scripts with a main, .bat launchers and what they run
  CONTROLS.md     every control file, flag, environment variable, command-line option and console variable the code reads or sets
  TODO.md         TODO/FIXME/HACK/workaround comments
  STATS.md        biggest files, line counts per folder"""
import ast, collections, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = "notes/index"
os.makedirs(OUT, exist_ok=True)
SKIP = ("\\.git\\", "\\build\\", "\\deps\\", "__pycache__", "\\notes\\", "\\Content\\", "\\Intermediate\\", "\\Saved\\", "\\Binaries\\",
        "\\screenshots\\", "\\logs\\", "\\.old_before_move", "\\area2\\export", "\\area2\\obj", "\\area2\\tex", "\\area2\\nif", "\\area2\\landterrain\\fbx")


def files(*pats):
    out = set()
    for p in pats:
        for f in glob.glob(p, recursive=True):
            a = os.path.abspath(f)
            if os.path.isfile(a) and not any(s in a for s in SKIP):
                out.add(os.path.relpath(a, ROOT).replace("\\", "/"))
    return sorted(out)


def read(f):
    return open(f, encoding="utf-8", errors="replace").read()


py = files("*.py", "tools/**/*.py", "unreal/**/*.py", "area2/*.py", "plugin/**/*.py")
cpp = files("plugin/**/*.cpp", "plugin/**/*.h", "shared/*.h", "unreal/SkyBridge/Source/**/*.cpp", "unreal/SkyBridge/Source/**/*.h")
bat = files("*.bat", "*.ps1", "tools/*.bat")
md = files("*.md")

# ---------------------------------------------------------------- symbols
sym, lines = {}, {}
with open(f"{OUT}/SYMBOLS.md", "w", encoding="utf-8") as w:
    w.write("# Python symbols (exact, from ast)\nformat: `line  name(args)  - first docstring line`\n")
    for f in py:
        try:
            src = read(f); tree = ast.parse(src)
        except Exception as e:
            w.write(f"\n## {f}\n(parse error: {e})\n"); continue
        lines[f] = src.count("\n") + 1
        doc = (ast.get_docstring(tree) or "").strip().splitlines()
        w.write(f"\n## {f}  ({lines[f]} lines)\n")
        if doc:
            w.write(f"> {doc[0][:160]}\n")
        entries = []
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                args = ""
                if not isinstance(n, ast.ClassDef):
                    try:
                        args = ast.unparse(n.args)
                    except Exception:
                        args = "..."
                d = (ast.get_docstring(n) or "").strip().splitlines()
                entries.append((n.lineno, ("class " if isinstance(n, ast.ClassDef) else "") + n.name + ("(" + args[:90] + ")" if not isinstance(n, ast.ClassDef) else ""), d[0][:110] if d else ""))
        sym[f] = [(a, b, c) for a, b, c in sorted(entries)]
        for a, b, c in sorted(entries):
            w.write(f"- {a}  `{b}`{('  - ' + c) if c else ''}\n")
json.dump(sym, open(f"{OUT}/symbols.json", "w"), indent=0)

# ---------------------------------------------------------------- C++
with open(f"{OUT}/CPP.md", "w", encoding="utf-8") as w:
    w.write("# C++ declarations (regex, approximate)\n")
    fn = re.compile(r"^\s*(?:static\s+|inline\s+|constexpr\s+|extern\s+)*([A-Za-z_][\w:<>,\s\*&]*?)\s+\**&?([A-Za-z_]\w*)\s*\(([^;{)]*)\)\s*(?:const\s*)?(?:noexcept\s*)?\{", re.M)
    st = re.compile(r"^\s*(?:struct|class|enum(?:\s+class)?|namespace)\s+([A-Za-z_]\w*)", re.M)
    for f in cpp:
        src = read(f)
        w.write(f"\n## {f}  ({src.count(chr(10)) + 1} lines)\n")
        for m in st.finditer(src):
            w.write(f"- {src.count(chr(10), 0, m.start()) + 1}  {m.group(0).strip()[:80]}\n")
        for m in fn.finditer(src):
            if m.group(2) in ("if", "for", "while", "switch", "catch", "return"):
                continue
            w.write(f"- {src.count(chr(10), 0, m.start()) + 1}  `{m.group(2)}({' '.join(m.group(3).split())[:90]})`\n")

# ---------------------------------------------------------------- imports
mods = {os.path.splitext(os.path.basename(f))[0]: f for f in py}
graph, imported = collections.defaultdict(set), set()
for f in py:
    try:
        tree = ast.parse(read(f))
    except Exception:
        continue
    for n in ast.walk(tree):
        names = []
        if isinstance(n, ast.Import):
            names = [a.name.split(".")[0] for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module:
            names = [n.module.split(".")[0]]
        for nm in names:
            if nm in mods and mods[nm] != f:
                graph[f].add(mods[nm]); imported.add(mods[nm])
alltext = "\n".join(read(f) for f in bat + md)
with open(f"{OUT}/IMPORTS.md", "w", encoding="utf-8") as w:
    w.write("# Project imports (exact for static `import x`; dynamic imports/exec are not seen)\n\n## who imports whom\n")
    for f in sorted(graph):
        w.write(f"- {f}  ->  {', '.join(sorted(graph[f]))}\n")
    w.write("\n## python files nobody imports and no .bat/.md mentions (candidates: scripts run by hand, or dead code)\n")
    for f in py:
        base = os.path.basename(f)
        if f not in imported and base not in alltext and not any(base in read(g) for g in py if g != f):
            w.write(f"- {f}\n")

# ---------------------------------------------------------------- entry points
with open(f"{OUT}/ENTRYPOINTS.md", "w", encoding="utf-8") as w:
    w.write("# Entry points\n\n## launchers (.bat/.ps1): first comment lines\n")
    for f in bat:
        head = [l.strip() for l in read(f).splitlines() if l.strip().lower().startswith(("rem", "#", "::"))][:3]
        w.write(f"- **{f}**: {' '.join(h[:140] for h in head) or '(no comment)'}\n")
    w.write("\n## python scripts with `if __name__ == '__main__'` (first docstring line)\n")
    for f in py:
        s = read(f)
        if "__main__" in s:
            try:
                d = (ast.get_docstring(ast.parse(s)) or "").strip().splitlines()
            except Exception:
                d = []
            w.write(f"- {f}: {d[0][:150] if d else ''}\n")

# ---------------------------------------------------------------- controls
pat = {
    "control file / area2 path": re.compile(r"area2[\\/]+([\w.\-]+\.(?:txt|json|py|csv|tsv))|AREA[^,\n]{0,40}['\"]([\w.\-]+\.(?:txt|json|py))['\"]"),
    "environment variable": re.compile(r"os\.environ(?:\.get)?\(?\[?['\"]([A-Z_][A-Z0-9_]+)['\"]|os\.getenv\(['\"]([A-Z_][A-Z0-9_]+)['\"]"),
    "command-line option": re.compile(r"add_argument\(['\"](--?[\w\-]+)['\"]|['\"](--[a-z][\w\-]+)['\"]\s+in\s+sys\.argv"),
    "console variable": re.compile(r"['\"]((?:r|sg|t)\.[A-Za-z][\w.]+)\s"),
    "sky command / SKSE file": re.compile(r"(SkyrimUnrealBridge\.(?:sky|autoload|dump|out))"),
}
found = {k: collections.defaultdict(set) for k in pat}
for f in py + cpp + bat:
    s = read(f)
    for k, rx in pat.items():
        for m in rx.finditer(s):
            name = next((g for g in m.groups() if g), None)
            if name:
                found[k][name].add(f)
with open(f"{OUT}/CONTROLS.md", "w", encoding="utf-8") as w:
    w.write("# Controls (regex scan: names are exact, meanings are in notes/files/)\n")
    for k, d in found.items():
        w.write(f"\n## {k} ({len(d)})\n")
        for name in sorted(d):
            fs = sorted(d[name])
            w.write(f"- `{name}`  <- {', '.join(fs[:4])}{' ...' if len(fs) > 4 else ''}\n")

# ---------------------------------------------------------------- TODO
rx = re.compile(r"(TODO|FIXME|HACK|XXX|workaround|known issue|not implemented)", re.I)
with open(f"{OUT}/TODO.md", "w", encoding="utf-8") as w:
    w.write("# TODO / FIXME / workaround comments\n")
    for f in py + cpp + bat + md:
        for i, l in enumerate(read(f).splitlines(), 1):
            if rx.search(l) and len(l) < 400:
                w.write(f"- {f}:{i}  {l.strip()[:200]}\n")

# ---------------------------------------------------------------- stats
allf = py + cpp
sizes = sorted(((os.path.getsize(f), f) for f in allf), reverse=True)
by_dir = collections.Counter()
for f in allf:
    by_dir[os.path.dirname(f) or "."] += read(f).count("\n") + 1
with open(f"{OUT}/STATS.md", "w", encoding="utf-8") as w:
    w.write("# Size\n\n## largest source files\n")
    for s, f in sizes[:40]:
        w.write(f"- {s // 1024} KB  {f}\n")
    w.write("\n## lines per folder\n")
    for d, n in by_dir.most_common():
        w.write(f"- {n:7d}  {d}\n")
print("index written: %d python files, %d C++ files, %d launchers -> %s/" % (len(py), len(cpp), len(bat), OUT))
