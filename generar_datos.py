# Autor: Brian Stiven Avila
# Crea un archivo jsonl con registros dummy de llamadas http para usar en los kpi

import argparse
import json
import os
import random
from datetime import datetime, timedelta, timezone

endpoints = ["/get", "/post", "/status/403", "/basic-auth", "/cookies", "/xml", "/html"]
status_por_endpoint = {
    "/status/403": [403],
    "/basic-auth": [200, 401],
    "/get": [200, 404],
    "/post": [200, 400],
    "/cookies": [200],
    "/xml": [200],
    "/html": [200],
}


def gen_ts(dias=3, rng=None):
    rng = rng or random
    ahora = datetime.now(timezone.utc)
    delta = timedelta(days=dias)
    inicio = ahora - delta
    seg = rng.randint(0, int(delta.total_seconds()))
    ts = inicio + timedelta(seconds=seg)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def gen_status(ep, rng=None):
    rng = rng or random
    opts = status_por_endpoint.get(ep, [200, 200, 200, 404])
    return rng.choice(opts)


def gen_registro(rng=None):
    rng = rng or random
    ep = rng.choice(endpoints)
    return {
        "timestamp_utc": gen_ts(3, rng),
        "endpoint": ep,
        "status_code": gen_status(ep, rng),
        "elapsed_ms": round(rng.uniform(50, 800), 1),
        "parse_result": "error" if rng.random() < 0.05 else "ok",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n_registros", type=int, default=500)
    p.add_argument("--salida", default="salida/datos.jsonl")
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args()

    rng = random.Random(args.seed)
    dir_out = os.path.dirname(args.salida)
    if dir_out:
        os.makedirs(dir_out, exist_ok=True)

    with open(args.salida, "w", encoding="utf-8") as f:
        for _ in range(args.n_registros):
            f.write(json.dumps(gen_registro(rng), ensure_ascii=False) + "\n")
    print(f"listo: {args.n_registros} en {args.salida}")


if __name__ == "__main__":
    main()
