"""Feeds notes/queue.json to the local Ollama model one task at a time, unattended.
  python tools/run_local_queue.py            run everything not finished yet (resumable; Ctrl+C or --stop-file to halt)
  python tools/run_local_queue.py --limit 5  only the next 5 tasks      --only F_todos  one task by id (re-runs it)
  python tools/run_local_queue.py --status   show progress only
Safety: the model may only write under notes/. After every task, any other file it changed is restored with `git checkout` (files that were
already modified before the task are left alone and reported). Untracked files outside notes/ are only reported, never deleted.
Results: notes/*.md, notes/files/*.md.  Progress: notes/progress.json.  Log: logs/local_queue.log.  Create the file notes/STOP to stop after the current task."""
import argparse, glob, json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PROGRESS, LOG, STOP = "notes/progress.json", "logs/local_queue.log", "notes/STOP"
ARGS = argparse.Namespace(base_url=None, model=None, api_key="none")
MODEL = os.environ.get("LOCAL_MODEL", "qwen3:30b-a3b-32k")   # e.g. qwen3:30b-a3b-12k for the lean, lower-memory setup
TIMEOUT = 12 * 60
RULES_THINK_OFF = "/no_think\n"   # Qwen3 switch; other models get plain text
RULES = """You are a documentation helper working in the folder C:\\Users\\Aidan\\SkyrimUnrealBridge (a Skyrim-to-Unreal bridge project).
HARD RULES: You are READ-ONLY: do not create, edit, rename or delete any file. Your final reply IS the deliverable: reply with the COMPLETE markdown document described in the task and nothing else (no preamble, no code fence around it). Never run git commit/checkout/reset/push, never install or download anything, never start Skyrim or Unreal.
Read files with commands like Get-Content / Select-String / git log (read only). Use plain English and ASCII only. Be concrete: file names, line numbers, exact values. If you do not know something write 'unsure' - never invent.
Start your reply directly with the first heading.

TASK: """


def log(msg):
    os.makedirs("logs", exist_ok=True)
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def codex_exe():
    c = sorted(glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\OpenAI\Codex\bin\*\codex.exe")), key=os.path.getmtime)
    if not c:
        sys.exit("codex.exe not found - open the ChatGPT desktop app once so it installs it.")
    return c[-1]


def git(*a):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def dirty():
    out = {}
    for ln in git("status", "--porcelain", "-uall").splitlines():
        out[ln[3:].strip().strip('"').replace("\\", "/")] = ln[:2]
    return out


def all_progress():
    """Union of every worker's progress file: notes/progress.json (the local qwen runner) and notes/progress_<worker>.json."""
    out = {}
    for f in glob.glob("notes/progress*.json"):
        for k, v in load(f, {}).items():
            if k not in out or (v.get("ok") and not out[k].get("ok")):
                out[k] = v
    return out


def claim(task_id, worker):
    """Atomically reserve a task so two workers never do the same one. A claim older than 40 min is stale (its worker died)."""
    os.makedirs("notes/claims", exist_ok=True)
    p = "notes/claims/" + task_id + ".lock"
    try:
        if os.path.exists(p) and time.time() - os.path.getmtime(p) > 40 * 60:
            os.remove(p)
        fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, ("%s %s" % (worker, time.strftime("%H:%M:%S"))).encode()); os.close(fd)
        return True
    except OSError:
        return False


def http_chat(prompt):
    """OpenAI-compatible chat call (Ollama /v1, llama.cpp, LM Studio, vLLM) for a second worker such as the homelab server."""
    import urllib.request, json as _j
    body = _j.dumps({"model": ARGS.model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2, "stream": False}).encode()
    req = urllib.request.Request(ARGS.base_url.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + (ARGS.api_key or "none")})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        txt = _j.loads(resp.read().decode("utf-8", "replace"))["choices"][0]["message"]["content"]
    return re.sub(r"<think>.*?</think>", "", txt, flags=re.S).strip()


def load(p, d):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


BANNED = ("shutil.rmtree", "os.remove", "os.unlink", "os.rmdir", "os.rename", "shutil.move", "subprocess", "os.system", "import requests", "urllib", "socket",
          "eval(", "exec(", "__import__", "ctypes", "winreg", "os.popen")


def check_python(txt):
    import ast
    try:
        ast.parse(txt)
    except SyntaxError as e:
        return "python syntax error line %s" % e.lineno
    bad = [b for b in BANNED if b in txt]
    if bad:
        return "unsafe call in script: " + ", ".join(bad)
    return ""


def ok(t):
    p = t["out"]
    if not os.path.isfile(p) or os.path.getsize(p) < t["min_bytes"]:
        return "output missing or too small"
    txt = open(p, encoding="utf-8", errors="replace").read()
    for m in t["must"]:
        if m not in txt:
            return "missing section " + m
    if sum(1 for ch in txt if ord(ch) > 0x2FFF) > 5:
        return "contains non-ASCII/CJK text"
    if t.get("check") == "python":
        return check_python(txt)
    if t["out"].endswith(".txt"):
        return "" if re.search(r"\||^\s*-\s", txt, re.M) else "no 'a | b | c' rows or bullets"
    names = {n for n in re.findall(r"[\w][\w.\-]*\.(?:py|cpp|h|bat|ps1|md|json|txt|ini|csv)\b", txt)}
    if len(names) >= 4:
        bad = [n for n in names if n.lower() not in known_names()]
        if len(bad) > 0.3 * len(names):
            return "invents files: " + ", ".join(sorted(bad)[:6])
    return ""


_known = None


def known_names():
    """Lower-case base names of every file git knows plus everything under area2/ and notes/ (for the invented-file check)."""
    global _known
    if _known is None:
        _known = {os.path.basename(f).lower() for f in git("ls-files").splitlines()}
        for pat in ("area2/*", "notes/**/*", "logs/*", "*"):
            _known |= {os.path.basename(f).lower() for f in glob.glob(pat, recursive=True)}
    return _known


MIN_FREE_COMMIT_GB = 1.2   # emergency level only: the resident 30B model alone commits ~22 GB (only ~8 GB resident) and Windows grows its system-managed paging file on demand
CAP = 55000  # chars of pasted material per task (64k-token context)


def material(t):
    parts, left = [], CAP
    for spec in t.get("inputs", []):
        if spec.startswith("cmd:"):
            r = subprocess.run(spec[4:], shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
            blocks = [(spec[4:], r.stdout or r.stderr)]
        elif spec.startswith("range:"):  # range:path:first_line:last_line (1-based, inclusive)
            path, a, b = spec[6:].rsplit(":", 2)
            lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
            blocks = [("%s (lines %s-%s of %d)" % (path, a, b, len(lines)), "\n".join(lines[int(a) - 1:int(b)]))]
        elif spec.startswith("numbered:"):  # numbered:path:first:last -> every line prefixed with its real line number
            path, a, b = spec[9:].rsplit(":", 2)
            lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
            blocks = [("%s (lines %s-%s of %d; each line starts with its line number)" % (path, a, b, len(lines)),
                       "\n".join("%d: %s" % (i + 1, ln) for i, ln in enumerate(lines) if int(a) - 1 <= i < int(b)))]
        else:
            blocks = [(f, open(f, encoding="utf-8", errors="replace").read()) for f in sorted(glob.glob(spec)) if os.path.isfile(f)]
        for name, text in blocks:
            share = max(left, 0)
            cut = len(text) > share
            parts.append("\n===== %s%s =====\n%s" % (name, " (TRUNCATED: only the first part is shown)" if cut else "", text[:share]))
            left -= len(text[:share])
    return "".join(parts) or "\n(no material)"


def call_model(codex, prompt):
    """One read-only model call; returns (reply_text, stdout_tail)."""
    if ARGS.base_url:
        try:
            return http_chat(prompt), ""
        except Exception as e:
            return "", "HTTP error: %s" % e
    cmd = [codex, "exec", "--oss", "--local-provider", "ollama", "-m", MODEL, "-C", ROOT, "-s", "read-only", "--skip-git-repo-check", "-o", "notes/_last.txt", "-"]
    tail = ""
    try:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT)
        tail = (r.stdout or "")[-300:].strip().replace("\n", " ")
    except subprocess.TimeoutExpired:
        tail = "TIMEOUT"
    try:
        txt = open("notes/_last.txt", encoding="utf-8", errors="replace").read().strip()
        os.remove("notes/_last.txt")
    except OSError:
        txt = ""
    return txt, tail


RETRY_NOTE = "\nIMPORTANT: your previous attempt at this task was rejected. Mention ONLY file names that literally appear in the pasted material; if you are unsure about a detail, leave it out.\n"


def run_task(codex, t):
    before = dirty()
    start = time.time()
    mat = material(t)
    if all_progress().get(t["id"], {}).get("ok") is False:
        mat = RETRY_NOTE + mat
    txt, tail = call_model(codex, (RULES if (ARGS.base_url and "qwen3" not in (ARGS.model or "")) else RULES_THINK_OFF + RULES) + t["prompt"] + "\n\nPASTED MATERIAL (real, current):" + mat)
    if txt and t.get("verify"):  # second pass: delete or correct every claim the pasted material does not support
        fixed, _ = call_model(codex, (RULES if (ARGS.base_url and "qwen3" not in (ARGS.model or "")) else RULES_THINK_OFF + RULES) + "Below is a DRAFT document and the REAL material it was written from. Output the corrected COMPLETE document: delete or fix every statement, file name, number or line number that the real material does not support; keep everything that is supported; keep the same headings. Reply with the document only.\n\nDRAFT:\n" + txt + "\n\nREAL MATERIAL:" + mat)
        if len(fixed) > 0.5 * len(txt):
            txt = fixed
    try:
        if txt and t["out"].endswith(".py"):     # the model sometimes wraps code in a markdown fence
            fenced = re.match(r"^```[a-zA-Z]*\n(.*?)\n```\s*$", txt, re.S)
            if fenced:
                txt = fenced.group(1)
        if txt:
            os.makedirs(os.path.dirname(t["out"]), exist_ok=True)
            open(t["out"], "w", encoding="utf-8", newline="\n").write(txt + "\n")
    except OSError:
        pass
    after = dirty()
    stray = []
    for f, st in after.items():
        if f.startswith(("notes/", "logs/", "staging/")):
            continue
        if f in before and before[f] == st:
            continue
        if st.strip() == "??":
            stray.append(f + " (untracked, left in place)")
        elif f not in before:
            # NOTE: never `git checkout` here. The model runs read-only, and restoring "stray" changes silently reverted other people's
            # (user/agent) uncommitted edits made while a task was running. Report only.
            stray.append(f + " (changed while this task ran - not by the model, it is read-only; left alone)")
        else:
            stray.append(f + " (was already modified, left alone)")
    why = ok(t)
    log("%s %-40s %4ds  %s%s" % ("OK  " if not why else "FAIL", t["id"][:40], time.time() - start, why or "done", ("  STRAY: " + "; ".join(stray)) if stray else ""))
    if why and tail:
        log("      model said: " + tail[:200])
    return not why


def free_commit_gb():
    import ctypes
    class MEM(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in
                   ("ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile", "ullTotalVirtual", "ullAvailVirtual", "ullAvailExtendedVirtual")]
    m = MEM(); m.dwLength = ctypes.sizeof(MEM)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPageFile / 2 ** 30


def wait_for_ollama(timeout=300):
    """The server may be mid-update or still starting: start the app if needed and wait until `ollama list` answers."""
    exe = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")
    app = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama app.exe")
    t0 = time.time()
    started = False
    while time.time() - t0 < timeout:
        r = subprocess.run([exe, "list"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0 and MODEL.split(":")[0] in r.stdout:
            log("Ollama is ready")
            return True
        if not started:
            env = dict(os.environ)
            env.setdefault("OLLAMA_MODELS", r"D:\Aidan_Moved\ollama_data\models")   # the C: junction is not followed by newer Ollama
            subprocess.Popen([app, "--hide"], env=env)
            started = True
        time.sleep(10)
    log("Ollama not ready after %d s: %s" % (timeout, (r.stdout + r.stderr)[-200:]))
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--base-url", help="use an OpenAI-compatible server instead of local Ollama, e.g. http://192.168.1.50:11434/v1")
    ap.add_argument("--model", help="model name on that server (with --base-url)")
    ap.add_argument("--api-key", default="none")
    ap.add_argument("--worker", default="local", help="worker name; progress goes to notes/progress_<worker>.json (default: the local qwen runner uses notes/progress.json)")
    ap.add_argument("--kinds", help="only tasks whose id starts with one of these letters, e.g. D,C,W,S (small-model friendly)")
    ap.add_argument("--timeout-min", type=float, help="per-request timeout in minutes (default 12; use 4 for tiny tasks on a slow server)")
    ap.add_argument("--cap", type=int, help="max characters of pasted material per task (small contexts: 16000)")
    ap.add_argument("--until", help="stop starting new tasks at this clock time HH:MM (morning), e.g. 07:30")
    a = ap.parse_args()
    global ARGS, PROGRESS, CAP, TIMEOUT
    ARGS = a
    if a.timeout_min:
        TIMEOUT = int(a.timeout_min * 60)
    if a.cap:
        CAP = a.cap
    if a.base_url:
        a.worker = a.worker if a.worker != "local" else "homelab"
        PROGRESS = "notes/progress_%s.json" % a.worker
        if not a.model:
            sys.exit("--model is required with --base-url")
    if not a.status:   # pid file so the on/off panel (tools/queue_toggle.py) can see and stop this worker: line 1 = this process, line 2 = the window (cmd) that launched it
        import atexit
        pidfile = "notes/run_%s.pid" % a.worker
        open(pidfile, "w").write("%d\n%d\n" % (os.getpid(), os.getppid()))
        atexit.register(lambda: os.path.exists(pidfile) and os.remove(pidfile))
    tasks = load("notes/queue.json", None)
    if tasks is None:
        sys.exit("run python tools/make_local_queue.py first")
    prog = load(PROGRESS, {})
    everyone = all_progress()
    if a.kinds:
        kinds = tuple(k.strip() + "_" for k in a.kinds.split(","))
        tasks = [t for t in tasks if t["id"].startswith(kinds)]
    done = sum(1 for t in tasks if everyone.get(t["id"], {}).get("ok"))
    failed = sum(1 for t in tasks if t["id"] in everyone and not everyone[t["id"]]["ok"])
    print("%d tasks: %d done, %d failed, %d waiting%s" % (len(tasks), done, failed, len(tasks) - done - failed, ("  [worker %s]" % a.worker) if a.base_url else ""))
    if a.status:
        return
    if os.path.exists(STOP):
        os.remove(STOP)
    codex = codex_exe() if not a.base_url else None
    try:   # keep Windows awake while this process runs (per-process, changes no system setting; released when the process ends)
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)   # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    except Exception:
        pass
    if not a.base_url and not wait_for_ollama():
        sys.exit("Ollama did not come up")
    todo = [t for t in tasks if (a.only and t["id"] == a.only) or (not a.only and (t["id"] not in everyone or (a.retry_failed and not everyone[t["id"]]["ok"] and not everyone[t["id"]].get("parked"))))]
    if a.limit:
        todo = todo[:a.limit]
    log("starting %d tasks with %s" % (len(todo), ARGS.model if ARGS.base_url else MODEL))
    spent = 0.0
    bad_streak = 0
    for i, t in enumerate(todo, 1):
        if os.path.exists(STOP):
            log("notes/STOP found - stopping")
            break
        waited = 0
        while free_commit_gb() < MIN_FREE_COMMIT_GB and waited < 15 and not os.path.exists(STOP):
            if waited == 0:
                log("free memory below 1.2 GB - pausing (Windows may be growing its paging file); re-checking every minute")
            time.sleep(60); waited += 1
        if free_commit_gb() < MIN_FREE_COMMIT_GB:
            log("free memory still below the limit after 15 minutes - stopping to protect the PC")
            break
        if bad_streak >= 10:
            log("10 failures in a row - stopping (something is wrong; check Ollama)")
            break
        if a.until and time.strftime("%H:%M") >= a.until and time.strftime("%H:%M") < "20:00":
            log("reached --until %s - stopping" % a.until)
            break
        if not a.only and not claim(t["id"], a.worker):
            continue            # another worker has it
        log("--- [%d/%d] NOW: %s  (%s%s)" % (i, len(todo), t["title"], t["out"], ", +verify pass" if t.get("verify") else ""))
        t0 = time.time()
        good = run_task(codex, t)
        bad_streak = 0 if good else bad_streak + 1
        spent += time.time() - t0
        prev = everyone.get(t["id"], {})
        attempts = prev.get("attempts", 0) + (0 if good else 1)
        prog[t["id"]] = dict(ok=good, at=time.strftime("%Y-%m-%d %H:%M:%S"), worker=a.worker, attempts=attempts)
        if not good and attempts >= 3:          # 3 failed attempts: skip it for good and file it for a stronger model / a person
            why = ok(t) or "no usable output"
            os.makedirs("notes/needs_better_model", exist_ok=True)
            json.dump(dict(id=t["id"], wanted_output=t["out"], reason="failed %d attempts with %s" % (attempts, ("the " + (ARGS.model or MODEL)) if True else ""),
                           attempts=[dict(attempt=attempts, why=why)], last_answer="", prompt=t["prompt"], inputs=t.get("inputs", [])),
                      open("notes/needs_better_model/%s.json" % t["id"], "w"), indent=1)
            prog[t["id"]]["parked"] = True
            log("task %s skipped after 3 failed attempts (%s) -> notes/needs_better_model/" % (t["id"], why))
        json.dump(prog, open(PROGRESS, "w"), indent=1)
        if i % 8 == 0 or t["id"].startswith("Z_"):   # keep notes/FILE_MAP.md and notes/REVIEW_LEADS.md current for the synthesis tasks and for any agent reading them
            subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_briefing.py")], capture_output=True)
        okc = sum(1 for v in prog.values() if v["ok"])
        eta = spent / i * (len(todo) - i) / 3600
        print("    totals: %d done, %d failed, %d left in this run; avg %.1f min/task; about %.1f hours to go\n" % (okc, len(prog) - okc, len(todo) - i, spent / i / 60, eta), flush=True)
    log("finished; run with --status to see totals")


if __name__ == "__main__":
    main()
