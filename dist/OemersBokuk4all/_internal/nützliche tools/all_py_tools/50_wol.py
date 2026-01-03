import socket


def wol(mac):
    addr = mac.replace(":", "")
    data = b"FF" * 6 + (addr * 16).encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(data, ("<broadcast>", 9))
