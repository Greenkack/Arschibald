import dis
import marshal


def disassemble_pyc(file):
    with open(file, "rb") as f:
        f.read(16)
        code = marshal.load(f)
        dis.dis(code)
