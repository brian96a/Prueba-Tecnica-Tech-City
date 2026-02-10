# Autor: Brian Stiven Avila
# Carga el csv de kpis en sqlite (stg y fct), filtra filas raras

import argparse
import csv
import sqlite3
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="salida/kpi_por_endpoint_dia.csv")
    p.add_argument("--db", default="etl_pdi/kpi.db")
    args = p.parse_args()

    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(args.db)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS stg_kpi_endpoint_dia (
            date_utc TEXT, endpoint_base TEXT, requests_total INT, success_2xx INT,
            client_4xx INT, server_5xx INT, parse_errors INT, avg_elapsed_ms REAL, p90_elapsed_ms REAL
        );
        CREATE TABLE IF NOT EXISTS fct_kpi_endpoint_dia (
            date_utc TEXT, endpoint_base TEXT, requests_total INT, success_2xx INT,
            client_4xx INT, server_5xx INT, parse_errors INT, avg_elapsed_ms REAL, p90_elapsed_ms REAL
        );
    """)

    filas = []
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                total = int(row.get("requests_total", 0))
                avg = float(row.get("avg_elapsed_ms", 0))
                p90 = float(row.get("p90_elapsed_ms", 0))
                if total <= 0 or p90 < avg:
                    continue
                filas.append(row)
    except FileNotFoundError:
        print(f"no existe: {args.input}", file=sys.stderr)
        sys.exit(1)

    cols = ["date_utc", "endpoint_base", "requests_total", "success_2xx", "client_4xx", "server_5xx", "parse_errors", "avg_elapsed_ms", "p90_elapsed_ms"]
    conn.execute("DELETE FROM stg_kpi_endpoint_dia")
    conn.execute("DELETE FROM fct_kpi_endpoint_dia")
    cur = conn.cursor()
    for row in filas:
        vals = [row.get(c) for c in cols]
        cur.execute("INSERT INTO stg_kpi_endpoint_dia VALUES (?,?,?,?,?,?,?,?,?)", vals)
        cur.execute("INSERT INTO fct_kpi_endpoint_dia VALUES (?,?,?,?,?,?,?,?,?)", vals)
    conn.commit()
    n = cur.execute("SELECT COUNT(*) FROM fct_kpi_endpoint_dia").fetchone()[0]
    conn.close()
    print(f"listo: {n} filas en {args.db}")


if __name__ == "__main__":
    main()
