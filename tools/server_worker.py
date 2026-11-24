#!/usr/bin/env python3
"""Standalone worker that runs ON the homelab server, so the PC can be switched off.  Python 3 standard library only.

  python3 worker.py                 run forever: take tasks from tasks.jsonl, ask the local Ollama, write outputs/<path>, record progress.jsonl
  python3 worker.py --status        show counts
  python3 worker.py --pack          zip outputs/ + needs_better_model/ + progress.jsonl into results_<time>.zip (to send back to the PC)

Rules it follows:
  * One task at a time; each task gets at most 3 attempts. Attempt 2 and 3 repeat the request with a note about what was wrong.
  * After the 3rd failed attempt the task is SKIPPED and filed in needs_better_model/<task id>.json (prompt, what went wrong, the last answer)
    for a stronger model or a person. The worker itself never shuts down because of a task.
  * A server outage (Ollama not answering at all) is NOT counted as an attempt: the worker waits, with growing pauses, and tries the same task again.
  * Resumable and crash-safe: progress.jsonl is append-only. It never deletes anything outside its own folder and only talks to the local Ollama."""
import argparse, fcntl, json, os, re, signal, sys, time, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
STOP = False
MAX_ATTEMPTS = 3


def log(msg):
    line = "%s %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    with open(os.path.join(HERE, "worker.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_tasks():
    with open(os.path.join(HERE, "tasks.jsonl"), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def load_progress():
    """-> (ok ids, parked ids, {id: number of counted failed attempts})"""
    ok, parked, fails = set(), set(), {}
    p = os.path.join(HERE, "progress.jsonl")
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            try:
                r = json.loads(l)
            except ValueError:
                continue
            if r.get("ok"):
                ok.add(r["id"])
            elif r.get("parked"):
                parked.add(r["id"])
            elif r.get("counts", True):
                fails[r["id"]] = fails.get(r["id"], 0) + 1
    return ok, parked - ok, fails


def record(tid, ok, secs, why="", **extra):
    with open(os.path.join(HERE, "progress.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(id=tid, ok=ok, at=time.strftime("%Y-%m-%d %H:%M:%S"), secs=round(secs), why=why, **extra)) + "\n")


def healthy(host):
    try:
        with urllib.request.urlopen(host.rstrip("/") + "/api/tags", timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


def chat(host, model, prompt, timeout, num_predict):
    # think=false: qwen3 otherwise spends the whole token budget "thinking" and returns an empty answer
    body = json.dumps({"model": model, "stream": False, "think": False, "messages": [{"role": "user", "content": prompt}],
                       "options": {"num_predict": num_predict, "temperature": 0.2}}).encode()
    req = urllib.request.Request(host.rstrip("/") + "/api/chat", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        msg = json.loads(r.read().decode("utf-8", "replace"))["message"]
    txt = re.sub(r"<think>.*?</think>", "", msg.get("content") or "", flags=re.S).strip()
    return txt


def valid(task, txt):
    if len(txt) < task.get("min_bytes", 8):
        return "answer too short or empty"
    if sum(1 for ch in txt if ord(ch) > 0x2FFF) > 5:
        return "non-ASCII text"
    if task["out"].endswith(".txt") and not re.search(r"\||^\s*-\s", txt, re.M):
        return "answer has no 'a | b | c' rows or bullet lines"
    return ""


def park(task, history, last_txt):
    d = os.path.join(HERE, "needs_better_model")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, task["id"] + ".json"), "w", encoding="utf-8") as f:
        json.dump(dict(id=task["id"], wanted_output=task["out"], reason="failed %d attempts with the small homelab model" % len(history), attempts=history,
                       last_answer=last_txt[:2000], prompt=task["prompt"]), f, indent=1)


def run(args):
    lock = open(os.path.join(HERE, "worker.lock"), "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sys.exit("another worker is already running")
    signal.signal(signal.SIGTERM, lambda *a: globals().__setitem__("STOP", True))
    signal.signal(signal.SIGINT, lambda *a: globals().__setitem__("STOP", True))
    tasks = load_tasks()
    ok, parked, fails = load_progress()
    log("worker start: %d tasks, %d done, %d parked, model %s" % (len(tasks), len(ok), len(parked), args.model))
    outage = 0
    for t in tasks:
        if t["id"] in ok or t["id"] in parked:
            continue
        history, last_txt = [], ""
        while fails.get(t["id"], 0) < MAX_ATTEMPTS:
            if STOP:
                log("stopping on request"); return
            n = fails.get(t["id"], 0) + 1
            prompt = t["prompt"] if n == 1 else t["prompt"] + "\n\nYour previous answer was rejected (%s). Reply with exactly the requested format and nothing else." % (history[-1]["why"] if history else "invalid")
            t0 = time.time()
            try:
                txt = chat(args.host, args.model, prompt, args.timeout, args.num_predict * (2 if n == 3 else 1))
                why = valid(t, txt)
            except Exception as e:
                txt, why = "", "request failed: %s" % str(e)[:80]
            if why.startswith("request failed") and not healthy(args.host):     # outage, not the task's fault: wait and retry the same attempt
                outage += 1
                wait = min(900, 60 * 2 ** min(outage, 4))
                record(t["id"], False, time.time() - t0, "server not answering", counts=False)
                log("server not answering; waiting %d s (task %s is not blamed)" % (wait, t["id"]))
                for _ in range(wait // 5):
                    if STOP: return
                    time.sleep(5)
                continue
            outage = 0
            if not why:
                path = os.path.join(HERE, "outputs", t["out"])
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(txt + "\n")
                ok.add(t["id"]); record(t["id"], True, time.time() - t0)
                if len(ok) % 25 == 0:
                    log("progress: %d done, %d parked" % (len(ok), len(parked)))
                break
            fails[t["id"]] = n
            history.append(dict(attempt=n, why=why, secs=round(time.time() - t0)))
            last_txt = txt or last_txt
            record(t["id"], False, time.time() - t0, why)
        else:
            park(t, history or [dict(attempt=MAX_ATTEMPTS, why="failed in an earlier run")], last_txt)
            parked.add(t["id"])
            record(t["id"], False, 0, "parked after %d attempts" % MAX_ATTEMPTS, parked=True)
            log("task %s skipped after %d failed attempts -> needs_better_model/" % (t["id"], MAX_ATTEMPTS))
    log("all tasks processed: %d ok, %d parked" % (len(ok), len(parked)))


def status():
    tasks = load_tasks(); ok, parked, fails = load_progress()
    print("tasks %d | ok %d | parked (need a better model) %d | waiting %d" % (len(tasks), len(ok), len(parked), len(tasks) - len(ok) - len(parked)))


def pack():
    out = os.path.join(HERE, "results_%s.zip" % time.strftime("%Y%m%d_%H%M%S"))
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for sub in ("outputs", "needs_better_model"):
            for dp, _, fns in os.walk(os.path.join(HERE, sub)):
                for fn in fns:
                    p = os.path.join(dp, fn)
                    arc = os.path.relpath(p, HERE if sub != "outputs" else os.path.join(HERE, "outputs")).replace(os.sep, "/")
                    z.write(p, arc); n += 1
        if os.path.exists(os.path.join(HERE, "progress.jsonl")):
            z.write(os.path.join(HERE, "progress.jsonl"), "progress.jsonl")
    print("packed %d files -> %s" % (n, out))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://127.0.0.1:11434")
    ap.add_argument("--model", default="qwen3:14b-gpu")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--num-predict", type=int, default=400)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--pack", action="store_true")
    a = ap.parse_args()
    status() if a.status else pack() if a.pack else run(a)
