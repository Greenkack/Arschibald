import modulefinder


def dep_graph(file):
    finder = modulefinder.ModuleFinder()
    finder.run_script(file)
    for name, mod in finder.modules.items():
        print(name, '->', [dep for dep in mod.globalnames])
