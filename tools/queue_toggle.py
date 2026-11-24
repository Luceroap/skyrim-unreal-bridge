"""On/off panel for the two overnight AI workers.   Double-click the desktop shortcut "AI Queue (on-off)"  (or: pythonw tools\\queue_toggle.py)
  * PC model (Warforge, qwen3 30B)    - heavy tasks; needs ~25 GB of memory headroom, so it will not start when free commit memory is low
  * Homelab server (qwen3 14B)        - tiny tasks, runs on the server, no load on this PC
START opens the worker in its own window and it keeps going until you press STOP. STOP kills it at once (the task in progress is simply redone later),
unloads the model so memory comes back, and keeps it stopped. Close Skyrim/Unreal before starting the PC model: the graphics card is shared."""
import ctypes, json, os, subprocess, sys, time, tkinter as tk
from tkinter import messagebox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OLLAMA = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")
WORKERS = {
    "local": dict(label="PC model (Warforge, 30B)", bat="Local_Queue.bat", args=["--retry-failed"], stop="notes/STOP", min_free=30.0, models=["qwen3:30b-a3b-32k", "qwen3:30b-a3b-12k"]),
    "homelab": dict(label="PC copy of the homelab worker (leave OFF: the server now runs its own)", bat="Homelab_Worker.bat", args=[], stop="notes/STOP_HOMELAB", min_free=0.0, models=[]),
}
k32 = ctypes.windll.kernel32


def alive(pid):
    h = k32.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False
    code = ctypes.c_ulong()
    k32.GetExitCodeProcess(h, ctypes.byref(code)); k32.CloseHandle(h)
    return code.value == 259                          # STILL_ACTIVE


def pids(w):
    try:
        a = [int(x) for x in open("notes/run_%s.pid" % w).read().split()]
        return a if a and alive(a[0]) else None
    except Exception:
        return None


class MEM(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in
               ("ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile", "ullTotalVirtual", "ullAvailVirtual", "ullAvailExtendedVirtual")]


def memory():
    m = MEM(); m.dwLength = ctypes.sizeof(MEM); k32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2 ** 30, m.ullAvailPageFile / 2 ** 30, m.ullTotalPageFile / 2 ** 30


def run_quiet(cmd):
    subprocess.run(cmd, capture_output=True, creationflags=0x08000000)


def start(w):
    cfg = WORKERS[w]
    if cfg["min_free"] and memory()[1] < cfg["min_free"]:
        messagebox.showwarning("Not enough memory", "Only %.0f GB of memory headroom is free (need %.0f GB).\nClose other programs, or check that the paging file is 64 GB." % (memory()[1], cfg["min_free"]))
        return
    for f in (cfg["stop"],):
        if os.path.exists(f):
            os.remove(f)
    if os.path.isdir("notes/claims"):               # drop this worker's stale claims so its tasks are free again
        for f in os.listdir("notes/claims"):
            p = os.path.join("notes/claims", f)
            try:
                if open(p).read().startswith(w):
                    os.remove(p)
            except OSError:
                pass
    subprocess.Popen(["cmd.exe", "/k", os.path.join(ROOT, cfg["bat"])] + cfg["args"], cwd=ROOT, creationflags=0x10)   # CREATE_NEW_CONSOLE


def stop(w):
    cfg = WORKERS[w]
    open(cfg["stop"], "w").close()                   # also stops the restart loop
    p = pids(w)
    if p:
        for pid in reversed(p):                      # the worker, then the window that launched it
            run_quiet(["taskkill", "/F", "/T", "/PID", str(pid)])
    try:
        os.remove("notes/run_%s.pid" % w)
    except OSError:
        pass
    for m in cfg["models"]:
        run_quiet([OLLAMA, "stop", m])


def progress():
    try:
        q = json.load(open("notes/queue.json"))
        done = {}
        for f in os.listdir("notes"):
            if f.startswith("progress") and f.endswith(".json"):
                for k, v in json.load(open("notes/" + f)).items():
                    if v.get("ok"):
                        done[k] = 1
        return len(done), len(q)
    except Exception:
        return None


class App:
    def __init__(self, root):
        self.root = root
        root.title("AI queue on/off")
        root.configure(padx=14, pady=12)
        self.rows = {}
        for i, (w, cfg) in enumerate(WORKERS.items()):
            tk.Label(root, text=cfg["label"], font=("Segoe UI", 12, "bold")).grid(row=i * 2, column=0, sticky="w")
            st = tk.Label(root, text="...", font=("Segoe UI", 10), anchor="w", justify="left")
            st.grid(row=i * 2 + 1, column=0, sticky="w")
            b = tk.Button(root, text="START", width=12, height=2, font=("Segoe UI", 11, "bold"), command=lambda w=w: self.toggle(w))
            b.grid(row=i * 2, column=1, rowspan=2, padx=(18, 0), pady=6)
            self.rows[w] = (st, b)
        self.info = tk.Label(root, text="", font=("Segoe UI", 9), fg="#555", justify="left")
        self.info.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))
        bar = tk.Frame(root); bar.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky="w")
        tk.Button(bar, text="Start both", command=lambda: [start(w) for w in WORKERS if not pids(w)]).pack(side="left")
        tk.Button(bar, text="Stop both", command=lambda: [stop(w) for w in WORKERS]).pack(side="left", padx=8)
        self.refresh()

    def toggle(self, w):
        stop(w) if pids(w) else start(w)
        self.root.after(1500, self.refresh)

    def refresh(self):
        for w, (st, b) in self.rows.items():
            p = pids(w)
            if p:
                st.config(text="RUNNING   (since %s)" % time.strftime("%H:%M", time.localtime(os.path.getmtime("notes/run_%s.pid" % w))), fg="#0a7d28")
                b.config(text="STOP", bg="#d9534f", fg="white", activebackground="#c9302c")
            else:
                st.config(text="stopped", fg="#777")
                b.config(text="START", bg="#3c9d4e", fg="white", activebackground="#2e7d3e")
        ram, commit, limit = memory()
        pr = progress()
        self.info.config(text="memory headroom %.0f of %.0f GB   |   free RAM %.0f GB%s" % (commit, limit, ram, ("   |   tasks done %d of %d" % pr) if pr else ""))
        self.root.after(3000, self.refresh)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
