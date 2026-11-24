"""Run a Python file inside the live editor (live_bridge debug hook) and print its output.
Usage: python tools/ue_run.py script.py [timeout_s]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from start_bridge import ue_exec

print(ue_exec(open(sys.argv[1]).read(), float(sys.argv[2]) if len(sys.argv) > 2 else 30) or "no answer (is live_bridge running?)")
