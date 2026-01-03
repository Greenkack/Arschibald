import gc
import pickle


def dump_all_objects(path="ramdump.pkl"):
    with open(path, "wb") as f:
        pickle.dump(gc.get_objects(), f)
    print("RAM gedumpt!")
