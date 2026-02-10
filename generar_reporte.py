# Autor: Brian Stiven Avila
# Lee el csv de kpis, arma un html con tablas y graficos para ver el resumen

import argparse
import base64
import io
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def grafico_barras(df):
    tot = df.groupby("endpoint_base")["requests_total"].sum().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(tot.index, tot.values, color="steelblue")
    ax.set_xlabel("solicitudes")
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def grafico_p90(df, umbral):
    p90 = df.groupby("endpoint_base")["p90_elapsed_ms"].mean().sort_values(ascending=True)
    colores = ["#e74c3c" if v > umbral else "steelblue" for v in p90.values]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(p90.index, p90.values, color=colores)
    ax.axhline(y=umbral, color="red", linestyle="--")
    ax.set_ylabel("p90 ms")
    plt.xticks(rotation=45, ha="right")
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="salida/kpi_por_endpoint_dia.csv")
    p.add_argument("--output", default="salida/reporte/kpi_diario.html")
    p.add_argument("--umbral_p90", type=float, default=300)
    args = p.parse_args()

    try:
        df = pd.read_csv(args.input)
    except FileNotFoundError:
        print(f"no existe: {args.input}", file=sys.stderr)
        sys.exit(1)

    total = df["requests_total"].sum()
    ok = df["success_2xx"].sum()
    c4 = df["client_4xx"].sum()
    s5 = df["server_5xx"].sum()
    pct_ok = (ok / total * 100) if total > 0 else 0
    pct_4 = (c4 / total * 100) if total > 0 else 0
    pct_5 = (s5 / total * 100) if total > 0 else 0
    p90_max = df["p90_elapsed_ms"].max()

    tabla = df.groupby("endpoint_base").agg({
        "requests_total": "sum",
        "success_2xx": "sum",
        "client_4xx": "sum",
        "server_5xx": "sum",
        "avg_elapsed_ms": "mean",
        "p90_elapsed_ms": "max",
    }).reset_index()
    tabla["pct_ok"] = (tabla["success_2xx"] / tabla["requests_total"] * 100).round(1)
    tabla["pct_4xx"] = (tabla["client_4xx"] / tabla["requests_total"] * 100).round(1)
    tabla["pct_5xx"] = (tabla["server_5xx"] / tabla["requests_total"] * 100).round(1)

    filas = ""
    for _, row in tabla.iterrows():
        cls = "alerta" if row["p90_elapsed_ms"] > args.umbral_p90 else ""
        filas += f'<tr class="{cls}"><td>{row["endpoint_base"]}</td><td>{int(row["requests_total"])}</td><td>{row["pct_ok"]}%</td><td>{row["pct_4xx"]}%</td><td>{row["pct_5xx"]}%</td><td>{row["avg_elapsed_ms"]:.2f}</td><td>{row["p90_elapsed_ms"]:.2f}</td></tr>'

    img1 = grafico_barras(df)
    img2 = grafico_p90(df, args.umbral_p90)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><title>KPI</title>
<style>
body{{font-family:sans-serif;margin:20px;background:#f5f5f5}}
.m{{display:flex;gap:20px;flex-wrap:wrap}}
.m span{{background:white;padding:15px;border-radius:8px}}
table{{border-collapse:collapse;background:white}}
th,td{{padding:10px;text-align:left;border:1px solid #ddd}}
th{{background:#3498db;color:white}}
.alerta{{background:#fde8e8}}
</style>
</head>
<body>
<h1>KPI</h1>
<div class="m">
<span>Total: {int(total)}</span>
<span>Ok 2xx: {pct_ok:.1f}%</span>
<span>4xx: {pct_4:.1f}%</span>
<span>5xx: {pct_5:.1f}%</span>
<span>p90 max: {p90_max:.1f}</span>
</div>
<table>
<tr><th>endpoint</th><th>total</th><th>%ok</th><th>%4xx</th><th>%5xx</th><th>avg ms</th><th>p90 ms</th></tr>
{filas}
</table>
<p><img src="data:image/png;base64,{img1}" width="600"></p>
<p><img src="data:image/png;base64,{img2}" width="600"></p>
</body>
</html>"""

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"listo: {args.output}")


if __name__ == "__main__":
    main()
