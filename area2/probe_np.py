try:
    import numpy
    print("numpy", numpy.__version__)
except Exception as e:
    print("no numpy:", e)
import sys; print(sys.version, sys.executable)
