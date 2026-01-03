import pycodestyle


def check_style(file):
    style = pycodestyle.StyleGuide()
    result = style.check_files()
    print(f"PEP8: {result.total_errors} Fehler gefunden.")
