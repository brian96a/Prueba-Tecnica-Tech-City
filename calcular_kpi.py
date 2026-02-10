# Autor: Brian Stiven Avila
# Lee el jsonl de llamadas, agrupa por dia y endpoint, saca kpis y escribe csv

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np


def normalizar(ep):
    # /status/403 -> /status, /basic-auth/user/pass -> /basic-auth
    partes = ep.strip("/").split("/")
    return "/" + partes[0] if partes else "/"


def cargar(path):
    regs = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for i, ln in enumerate(f, 1):
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    regs.append(json.loads(ln))
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        print(f"no existe: {path}", file=sys.stderr)
        sys.exit(1)
    return regs


def agrupar(regs):
    grupos = {}
    for r in regs:
        ts = r.get("timestamp_utc", "")
        fecha = ts[:10] if len(ts) >= 10 else ""
        ep = normalizar(r.get("endpoint", ""))
        k = (fecha, ep)
        if k not in grupos:
            grupos[k] = {
                "fecha": fecha,
                "ep": ep,
                "total": 0,
                "ok": 0,
                "4xx": 0,
                "5xx": 0,
                "parse_err": 0,
                "elapsed": [],
            }
        g = grupos[k]
        g["total"] += 1
        sc = r.get("status_code", 0)
        if 200 <= sc < 300:
            g["ok"] += 1
        elif 400 <= sc < 500:
            g["4xx"] += 1
        elif 500 <= sc < 600:
            g["5xx"] += 1
        if r.get("parse_result") != "ok":
            g["parse_err"] += 1
        g["elapsed"].append(r.get("elapsed_ms", 0))
    return grupos


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="salida/datos.jsonl")
    p.add_argument("--output", default="salida/kpi_por_endpoint_dia.csv")
    args = p.parse_args()

    regs = cargar(args.input)
    if not regs:
        print("sin datos", file=sys.stderr)
        sys.exit(1)

    grupos = agrupar(regs)
    filas = []
    for g in grupos.values():
        arr = np.array(g["elapsed"])
        avg = float(np.mean(arr)) if len(arr) > 0 else 0
        p90 = float(np.percentile(arr, 90)) if len(arr) > 0 else 0
        filas.append({
            "date_utc": g["fecha"],
            "endpoint_base": g["ep"],
            "requests_total": g["total"],
            "success_2xx": g["ok"],
            "client_4xx": g["4xx"],
            "server_5xx": g["5xx"],
            "parse_errors": g["parse_err"],
            "avg_elapsed_ms": round(avg, 2),
            "p90_elapsed_ms": round(p90, 2),
        })
    filas.sort(key=lambda x: (x["date_utc"], x["endpoint_base"]))

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    campos = ["date_utc", "endpoint_base", "requests_total", "success_2xx", "client_4xx", "server_5xx", "parse_errors", "avg_elapsed_ms", "p90_elapsed_ms"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    print(f"listo: {len(filas)} filas en {args.output}")


if __name__ == "__main__":
    main()
