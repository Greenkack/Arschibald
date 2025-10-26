import os
import time

import psutil


def resource_monitor():
    pid = os.getpid()
    p = psutil.Process(pid)
    while True:
        print("MEM:", p.memory_info().rss, "CPU:", p.cpu_percent())
        time.sleep(1)
