import hashlib
import os
import uuid


def mass_rename(directory="."):
    for fn in os.listdir(directory):
        if os.path.isfile(fn):
            newname = hashlib.md5(
                (fn + str(uuid.uuid4())).encode()).hexdigest() + os.path.splitext(fn)[1]
            os.rename(fn, newname)
