import time

import pyperclip


def clipboard_watcher():
    old = ""
    while True:
        txt = pyperclip.paste()
        if txt != old:
            print(f"Clipboard: {txt}")
            old = txt
        time.sleep(1)
