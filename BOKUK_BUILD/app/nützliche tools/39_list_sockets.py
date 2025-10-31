import psutil


def list_sockets():
    for c in psutil.net_connections():
        if c.status == 'LISTEN':
            print(f"Listening: {c.laddr}")
