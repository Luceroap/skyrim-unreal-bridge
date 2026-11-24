"""Assemble the local model's notes into compact files for the strong agents (deterministic, no LLM):  python tools/build_briefing.py
  notes/FILE_MAP.md       one line per source file: purpose (from notes/files/*.md '## Purpose') + size/functions from the exact index
  notes/REVIEW_LEADS.md   all review findings (notes/review/*.md) ranked: high confidence first, perf/memory before cleanup. UNVERIFIED leads.
Run automatically by tools/run_local_queue.py every few tasks; safe to run any time."""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def read(p):
    return open(p, encoding="utf-8", errors="replace").read()


# ---------------------------------------------------------------- FILE_MAP
try:
    sym = json.load(open("notes/index/symbols.json"))
except Exception:
    sym = {}
rows = {}
for p in sorted(glob.glob("notes/files/*.md")):
    name = os.path.basename(p)[:-3]
    part = ""
    m = re.search(r"\.part(\d+)$", name)
    if m:
        part, name = " (part %s)" % m.group(1), name[:m.start()]
    rel = name.replace("__", "/")
    txt = read(p)
    pm = re.search(r"##\s*Purpose\s*\n+(.+?)(?:\n##|\Z)", txt, re.S)
    purpose = " ".join(pm.group(1).split())[:260] if pm else ""
    um = "unsure" in txt.lower()
    rows.setdefault(rel, []).append((part, purpose, um))
with open("notes/FILE_MAP.md", "w", encoding="utf-8") as w:
    w.write("# File map (purpose by the local model - verify before relying; exact symbols are in notes/index/SYMBOLS.md)\n\n")
    w.write("| file | functions | purpose |\n|---|---|---|\n")
    for rel in sorted(rows):
        n = len(sym.get(rel, []))
        purposes = " ".join(("%s%s" % (pu, pt)) for pt, pu, _ in rows[rel] if pu)[:300]
        flag = " [contains 'unsure']" if any(u for _, _, u in rows[rel]) else ""
        w.write("| %s | %s | %s%s |\n" % (rel, n or "", purposes.replace("|", "/"), flag))
    w.write("\nFiles documented: %d\n" % len(rows))

# ---------------------------------------------------------------- REVIEW_LEADS
CAT = {"perf": 0, "memory": 1, "bug": 2, "robustness": 3, "cleanup": 4}
CONF = {"high": 0, "medium": 1, "low": 2}
leads = []
for p in sorted(glob.glob("notes/review/*.md")):
    name = os.path.basename(p)[:-3].replace("__", "/")
    for ln in read(p).splitlines():
        m = re.match(r"\s*`?L(\d+)\s*\|\s*([a-z]+)\s*\|(.+)\|\s*(low|medium|high)\s*`?\s*$", ln, re.I)
        if m:
            leads.append((CONF.get(m.group(4).lower(), 2), CAT.get(m.group(2).lower(), 5), name, int(m.group(1)), m.group(2).lower(), " ".join(m.group(3).split()), m.group(4).lower()))
leads.sort()
with open("notes/REVIEW_LEADS.md", "w", encoding="utf-8") as w:
    w.write("# Review leads (UNVERIFIED, from a small local model: confirm in the code before acting)\n")
    w.write("format: confidence | category | file:line | what / why / fix\n\n")
    for conf, cat, f, line, c, rest, cf in leads:
        w.write("- **%s** | %s | %s:%d | %s\n" % (cf, c, f, line, rest[:420]))
    w.write("\nLeads: %d\n" % len(leads))

# ---------------------------------------------------------------- REVIEW_LEADS_VERIFIED (leads that a second pass checked against the code and its callers)
ver = {}
for p in sorted(glob.glob("staging/verified/*.txt")):
    for ln in read(p).splitlines():
        m = re.match(r"\s*`?(.+?):(\d+)\s*\|\s*(YES|NO|UNSURE)\s*\|\s*(.+?)`?\s*$", ln, re.I)
        if m:
            ver[(m.group(1), int(m.group(2)))] = (m.group(3).upper(), m.group(4))
order = {"YES": 0, "UNSURE": 1, "NO": 2}
with open("notes/REVIEW_LEADS_VERIFIED.md", "w", encoding="utf-8") as w:
    w.write("# Review leads after a verification pass (still from small models: YES = worth a human/strong-model look first, NO = probably a false alarm)\n\n")
    vrows = []
    for conf, cat, f, line, c, rest, cf in leads:
        f0 = re.sub(r"\.part\d+$", "", f)
        v = ver.get((f0, line))
        vrows.append((order.get(v[0], 3) if v else 3, conf, f0, line, c, rest, v))
    vrows.sort(key=lambda r: (r[0], r[1]))
    for o, conf, f0, line, c, rest, v in vrows:
        tag = ("%s - %s" % v) if v else "not verified yet"
        w.write("- **%s** | %s | %s:%d | %s  \n  lead: %s\n" % (v[0] if v else "?", c, f0, line, tag, rest[:300]))
    w.write("\nVerified: %d of %d leads; YES: %d, UNSURE: %d, NO: %d\n" % (len(ver), len(leads), sum(1 for v in ver.values() if v[0] == "YES"), sum(1 for v in ver.values() if v[0] == "UNSURE"), sum(1 for v in ver.values() if v[0] == "NO")))

print("FILE_MAP: %d files; REVIEW_LEADS: %d leads (%d verified)" % (len(rows), len(leads), len(ver)))
