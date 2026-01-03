import os
import shutil
import sys


def install_self():
    target = os.path.expanduser("~/autostart/" + os.path.basename(sys.argv[0]))
    shutil.copy2(sys.argv[0], target)
