import time
import os
import sys

time.sleep(30)

print("Hello World", flush=True)
print(os.getcwd(), flush=True)
print(sys.path, flush=True)

for name, value in os.environ.items():
    print("{0}: {1}".format(name, value), flush=True)


time.sleep(10_000)
