import requests


def wget_site(url, out="site.html"):
    html = requests.get(url).text
    with open(out, "w") as f:
        f.write(html)
