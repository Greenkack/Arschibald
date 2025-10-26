#!/usr/bin/env python3
"""
pdf_recover.py
Versucht, ein Open-/User-Passwort für eine eigene PDF zu finden.
Modi:
 - dict : Wörterbuchangriff (Datei mit einem Passwort pro Zeile)
 - numeric : numerischer Brute-Force (z.B. 4..6 Stellen)
Beendet sofort, wenn Passwort gefunden.
"""
import argparse
import itertools
import sys
from functools import partial
from multiprocessing import Manager, Pool

from PyPDF2 import PdfReader


def try_password(path, password):
    """Versucht, die PDF mit password zu öffnen. Gibt True zurück bei Erfolg."""
    try:
        # PdfReader instanziieren ist günstig; nur decrypt testen.
        r = PdfReader(path)
        if not r.is_encrypted:
            return ("ALREADY_OPEN", None)
        res = r.decrypt(password)
        # PyPDF2: res==0 => fehlgeschlagen, else => erfolgreich (compat)
        if isinstance(res, bool):
            ok = res
        else:
            ok = (res != 0)
        return ("OK", password) if ok else (None, None)
    except Exception:
        # Manche PDFs werfen Fehler; behandeln und weiter machen.
        return (None, None)


def worker_dict(path, queue, pw):
    status, found = try_password(path, pw)
    if status == "ALREADY_OPEN":
        queue.put(("found", ""))
        return True
    if status == "OK":
        queue.put(("found", found))
        return True
    return False


def dict_attack(path, dict_file, processes):
    manager = Manager()
    queue = manager.Queue()
    with open(dict_file, encoding="utf-8", errors="ignore") as f:
        words = [line.strip() for line in f if line.strip()]
    pool = Pool(processes=processes)
    try:
        fn = partial(worker_dict, path, queue)
        for _ in pool.imap_unordered(lambda p: fn(p), words):
            pass
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
    pool.close()
    pool.join()
    if not queue.empty():
        tag, pw = queue.get()
        if tag == "found":
            return pw
    return None


def numeric_generator(min_len, max_len, charset="0123456789"):
    for length in range(min_len, max_len + 1):
        for t in itertools.product(charset, repeat=length):
            yield "".join(t)


def worker_numeric(args):
    path, pw = args
    status, found = try_password(path, pw)
    if status == "ALREADY_OPEN":
        return ("found", "")
    if status == "OK":
        return ("found", found)
    return (None, None)


def numeric_attack(
        path,
        min_len,
        max_len,
        processes,
        charset="0123456789",
        limit=None):
    manager = Manager()
    queue = manager.Queue()
    pool = Pool(processes=processes)
    try:
        gen = numeric_generator(min_len, max_len, charset=charset)
        if limit:
            gen = itertools.islice(gen, limit)
        for res in pool.imap_unordered(
                worker_numeric, ((path, p) for p in gen), chunksize=100):
            if res[0] == "found":
                pool.terminate()
                pool.join()
                return res[1]
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
    pool.close()
    pool.join()
    return None


def main():
    parser = argparse.ArgumentParser(
        description="PDF Passwort Recovery (nur eigene Dateien)")
    parser.add_argument("pdf", help="Pfad zur PDF")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_dict = sub.add_parser("dict", help="Wörterbuch-Angriff")
    p_dict.add_argument("-w", "--wordlist", required=True,
                        help="Pfad zur Wortliste (ein PW pro Zeile)")
    p_dict.add_argument(
        "-p",
        "--processes",
        type=int,
        default=4,
        help="Anzahl paralleler Prozesse")

    p_num = sub.add_parser(
        "numeric",
        help="Numerischer Brute-Force (Chunks parallel)")
    p_num.add_argument(
        "--min",
        type=int,
        default=4,
        help="Minimale Stellenanzahl")
    p_num.add_argument(
        "--max",
        type=int,
        default=6,
        help="Maximale Stellenanzahl")
    p_num.add_argument(
        "-p",
        "--processes",
        type=int,
        default=4,
        help="Anzahl paralleler Prozesse")
    p_num.add_argument(
        "--charset",
        default="0123456789",
        help="Zeichensatz für Bruteforce")
    p_num.add_argument(
        "--limit",
        type=int,
        help="Optionale Begrenzung, n Versuche")

    args = parser.parse_args()

    if args.mode == "dict":
        print(f"[+] Wörterbuch-Angriff: {args.wordlist}")
        pw = dict_attack(args.pdf, args.wordlist, args.processes)
    else:
        print(
            f"[+] Numerischer Angriff: {
                args.min}..{
                args.max} Stellen charset={
                args.charset}")
        pw = numeric_attack(
            args.pdf,
            args.min,
            args.max,
            args.processes,
            charset=args.charset,
            limit=args.limit)

    if pw is None:
        print("Kein Passwort gefunden.")
        sys.exit(2)
    if pw == "":
        print("PDF war nicht verschlüsselt oder öffnete ohne Passwort.")
        sys.exit(0)
    print("Passwort gefunden:", pw)
    print("Sie können die Datei jetzt z.B. in PyPDF2 mit diesem Passwort öffnen oder mit qpdf eine unverschlüsselte Kopie erzeugen.")


if __name__ == "__main__":
    main()
