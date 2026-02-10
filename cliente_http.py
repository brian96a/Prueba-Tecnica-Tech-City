# Autor: Brian Stiven Avila
# Hace llamadas a httpbin.org para probar auth, cookies, descargar json/xml/html, enviar forms y seguir redirects

import json
import os
import sys

import requests
from bs4 import BeautifulSoup

url_base = "https://httpbin.org"
salida = "salida"
user = "usuario_test"
passwd = "clave123"
form = {
    "nombre": "Juan",
    "apellido": "Pérez",
    "correo_electronico": "juan.perez@example.com",
    "mensaje": "Este es un mensaje de prueba.",
}


def auth():
    url = f"{url_base}/basic-auth/{user}/{passwd}"
    try:
        r = requests.get(url, auth=(user, passwd), timeout=30)
        data = r.json()
        return r.status_code == 200 and data.get("authenticated")
    except:
        return False


def cookies():
    s = requests.Session()
    try:
        s.get(f"{url_base}/cookies/set", params={"session": "activa"}, timeout=30)
        r = s.get(f"{url_base}/cookies", timeout=30)
        data = r.json()
        return "session" in data.get("cookies", {})
    except:
        return False
    finally:
        s.close()


def status_403():
    url = f"{url_base}/status/403"
    try:
        for _ in range(2):
            r = requests.get(url, timeout=30)
            if r.status_code == 403:
                return True
        return False
    except:
        return False


def get_json():
    try:
        r = requests.get(f"{url_base}/get", timeout=30)
        r.raise_for_status()
        data = r.json()
        path = os.path.join(salida, "datos.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False


def get_xml():
    try:
        r = requests.get(f"{url_base}/xml", timeout=30)
        r.raise_for_status()
        path = os.path.join(salida, "datos.xml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(r.text)
        return True
    except:
        return False


def get_html():
    try:
        r = requests.get(f"{url_base}/html", timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        titulo = soup.title.string if soup.title else "Sin título"
        path = os.path.join(salida, "titulo.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"<html><head><meta charset='utf-8'><title>{titulo}</title></head>")
            f.write(f"<body><h1>{titulo}</h1></body></html>")
        return True
    except:
        return False


def post_form():
    try:
        r = requests.post(f"{url_base}/post", data=form, timeout=30)
        r.raise_for_status()
        return True
    except:
        return False


def redirect():
    try:
        r = requests.get(f"{url_base}/redirect-to", params={"url": "/get"}, timeout=30, allow_redirects=True)
        return r.status_code == 200
    except:
        return False


def main():
    os.makedirs(salida, exist_ok=True)
    todo = [
        ("auth", auth),
        ("cookies", cookies),
        ("403", status_403),
        ("json", get_json),
        ("xml", get_xml),
        ("html", get_html),
        ("form", post_form),
        ("redirect", redirect),
    ]
    ok = 0
    for name, fn in todo:
        if fn():
            ok += 1
        else:
            print(f"fallo: {name}")
    sys.exit(0 if ok == len(todo) else 1)


if __name__ == "__main__":
    main()
