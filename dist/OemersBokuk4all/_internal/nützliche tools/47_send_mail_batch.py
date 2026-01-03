import multiprocessing
import random
import smtplib
import string


def send_mail_batch(to, count):
    def send_mail(i):
        msg = ''.join(random.choices(string.ascii_letters, k=100))
        with smtplib.SMTP('localhost') as s:
            s.sendmail("test@localhost", to, msg)
    with multiprocessing.Pool(8) as pool:
        pool.map(send_mail, range(count))
