"""Apply reviewed docstring suggestions from the local model (staging/docstrings/*.txt) to the real source files.
  python tools/apply_docstrings.py            DRY RUN: shows what would be inserted, changes nothing
  python tools/apply_docstrings.py --apply    writes the docstrings (a .bak copy of each changed file goes to staging/docstring_backups/)
Rows look like `<line> | <function name> | <docstring>`. A docstring is only inserted when: the line really is that function's `def`, the function has no docstring yet,
the result still parses, and the text is a single plain line. Review the suggestions first; commit only the files you reviewed."""
import ast, glob, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
APPLY = "--apply" in sys.argv
done = 0
for sug in sorted(glob.glob("staging/docstrings/*.txt")):
    rel = os.path.basename(sug)[:-4].replace("__", "/")
    rel = re.sub(r"\.part\d+$", "", rel)
    if not os.path.exists(rel):
        print("skip (no such file):", rel); continue
    src = open(rel, encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in src else "\n"
    lines = src.replace("\r\n", "\n").split("\n")
    tree = ast.parse("\n".join(lines))
    funcs = {n.lineno: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    inserts = []
    for row in open(sug, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*(\d+)\s*\|\s*([\w.]+)\s*\|\s*(.+?)\s*$", row)
        if not m:
            continue
        ln, name, doc = int(m.group(1)), m.group(2), m.group(3).strip().strip('"').strip("'")
        fn = funcs.get(ln)
        if not fn or fn.name != name.split(".")[-1] or ast.get_docstring(fn) or '"""' in doc or "\\" in doc or len(doc) > 120:
            continue
        body = fn.body[0]
        ind = " " * body.col_offset
        inserts.append((body.lineno - 1, ind + '"""' + doc.rstrip(".") + '."""'))
    if not inserts:
        continue
    for at, text in sorted(inserts, reverse=True):
        lines.insert(at, text)
    new = "\n".join(lines)
    try:
        ast.parse(new)
    except SyntaxError as e:
        print("REJECTED (would break %s: %s)" % (rel, e)); continue
    print("%s: %d docstrings %s" % (rel, len(inserts), "applied" if APPLY else "would be added"))
    done += len(inserts)
    if APPLY:
        os.makedirs("staging/docstring_backups", exist_ok=True)
        shutil.copy2(rel, os.path.join("staging/docstring_backups", rel.replace("/", "__") + ".bak"))
        open(rel, "w", encoding="utf-8", newline="").write(new.replace("\n", eol))
print("total: %d" % done)
