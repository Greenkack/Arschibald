import pkg_resources


def vuln_check():
    pkgs = [(d.project_name, d.version) for d in pkg_resources.working_set]
    print(pkgs)
    # Hinweis: safety.safety.check(pkgs) (Safety separat installieren)
