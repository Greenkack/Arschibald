def honeypot(fn):
    def wrapper(*args, **kwargs):
        print(
            f"ALERT! Funktion {
                fn.__name__} wurde mit {args}, {kwargs} aufgerufen!")
        return fn(*args, **kwargs)
    return wrapper
