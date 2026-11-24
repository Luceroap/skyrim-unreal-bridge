"""python area2/cap.py <names,comma> <dist> <prefix> -> area2/<prefix>_all.png"""
import os, subprocess, sys, time
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__))
names, dist, pre = sys.argv[1:4]


def step(s):
    open(os.path.join(A, "npc_step.txt"), "w").write(s)
    r = subprocess.run([sys.executable, os.path.join(A, "..", "tools", "ue_run.py"), os.path.join(A, "npc_capture.py"), "60"], capture_output=True, text=True)
    print(r.stdout.strip())


step("setup %s %s" % (names, dist))
time.sleep(1.5)
step("grab " + pre)
step("done")
ims = [Image.open(os.path.join(A, "%s_%d.png" % (pre, i))) for i in range(3) if os.path.exists(os.path.join(A, "%s_%d.png" % (pre, i)))]
w = sum(i.width for i in ims)
out = Image.new("RGB", (w, ims[0].height))
x = 0
for i in ims:
    out.paste(i.convert("RGB"), (x, 0)); x += i.width
out.thumbnail((1400, 700))
out.save(os.path.join(A, pre + "_all.png"))
