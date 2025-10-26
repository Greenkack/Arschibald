import pydoc


def make_api_doc(modulename):
    with open(f"{modulename}_API.html", "w") as f:
        f.write(
            pydoc.html.page(
                pydoc.describe(modulename),
                pydoc.render_doc(modulename)))
