import sys
import os
import pathlib

PIDFILE = pathlib.Path("/lcars/temp/run.pid")
if not PIDFILE.exists():
    print('PIDFILE fehlt')
    sys.exit(1)

with PIDFILE.open() as f:
    pid = int(f.read())

try:
    os.kill(pid, 0)
except OSError:
    print('pid läuft nicht')
    sys.exit(1)

sys.exit(0)