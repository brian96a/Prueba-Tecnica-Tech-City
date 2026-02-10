# Test Técnico - Cliente HTTP y Procesamiento de Datos

**Autor:** Brian Stiven Avila  
**Postulación:** Team Core - Somos TechCity  
**Fecha límite:** Viernes 6/2/2026

---

## Estructura del Proyecto

```
test-tecnico-core/
├── README.md
├── requirements.txt
├── cliente_http.py           # Ejercicio 1: Cliente HTTP con httpbin.org
├── generar_datos.py          # Sección 1.1: Generación de datos ficticios JSONL
├── calcular_kpi.py           # Sección 1.2: Cálculo de KPIs diarios
├── generar_reporte.py        # Sección 3: Reporte HTML con gráficos
├── salida/                   # Directorio de salida (generado)
│   ├── datos.json            # Del cliente HTTP
│   ├── datos.xml
│   ├── titulo.html
│   ├── datos.jsonl           # De generar_datos.py
│   ├── kpi_por_endpoint_dia.csv
│   └── reporte/
│       └── kpi_diario.html
└── etl_pdi/                  # Sección 2: Pentaho Data Integration
    ├── README_PDI.md         # Documentación ETL
    ├── generar_pdi.py        # Genera .ktr y .kjb
    ├── etl_sqlite.py         # Alternativa ETL en Python (sin PDI)
    ├── t_load_kpi.ktr        # Transformación (generar con generar_pdi.py)
    └── j_daily_kpi.kjb       # Job (generar con generar_pdi.py)
```

---

## Requisitos

- Python 3.10+
- Dependencias: `pip install -r requirements.txt`

```bash
pip install -r requirements.txt
```

---

## Ejecución

### 1. Cliente HTTP (Ejercicio principal)

Interactúa con httpbin.org: autenticación, cookies, extracción JSON/XML/HTML, formularios, redirecciones.

```bash
python cliente_http.py
```

**Salidas:** `salida/datos.json`, `salida/datos.xml`, `salida/titulo.html`

---

### 2. Generación de datos ficticios (Sección 1.1)

Genera 500 registros JSONL simulando bitácora HTTP.

```bash
python generar_datos.py --n_registros 500 --salida salida/datos.jsonl --seed 42
```

**Ejemplo de registro:**
```json
{"timestamp_utc": "2026-01-05T10:15:23Z", "endpoint": "/get", "status_code": 200, "elapsed_ms": 120.5, "parse_result": "ok"}
```

---

### 3. Cálculo de KPIs (Sección 1.2)

Lee `datos.jsonl` y genera `kpi_por_endpoint_dia.csv`.

```bash
python calcular_kpi.py --input salida/datos.jsonl --output salida/kpi_por_endpoint_dia.csv
```

**Métricas calculadas:**
- `requests_total`, `success_2xx`, `client_4xx`, `server_5xx`, `parse_errors`
- `avg_elapsed_ms`, `p90_elapsed_ms` (percentil 90 con `numpy.percentile`)

**Normalización de endpoint:** `/status/403` → `/status`, `/basic-auth/user/pass` → `/basic-auth`

---

### 4. Reporte HTML (Sección 3)

Genera reporte visual con métricas y gráficos.

```bash
python generar_reporte.py --input salida/kpi_por_endpoint_dia.csv --output salida/reporte/kpi_diario.html --umbral_p90 300
```

**Incluye:** Métricas globales, tabla por endpoint, gráficos de barras (requests, p90). Valores p90 > umbral se marcan en rojo.

---

### 5. ETL - Pentaho Data Integration (Sección 2)

#### Opción A: Con PDI instalado

1. Generar archivos `.ktr` y `.kjb`:
   ```bash
   python etl_pdi/generar_pdi.py
   ```
2. Abrir Spoon, ajustar rutas y conexión SQLite.
3. Ejecutar: `j_daily_kpi.kjb`

Ver `etl_pdi/README_PDI.md` para detalles.

#### Opción B: Sin PDI - Script Python

```bash
python etl_pdi/etl_sqlite.py --input salida/kpi_por_endpoint_dia.csv --db etl_pdi/kpi.db
```

Carga datos en SQLite con la misma lógica de filtrado (requests_total > 0, p90 >= avg).

---

## Flujo completo (ejemplo)

```bash
# 1. Cliente HTTP
python cliente_http.py

# 2. Generar datos
python generar_datos.py --n_registros 500 --salida salida/datos.jsonl --seed 42

# 3. Calcular KPIs
python calcular_kpi.py --input salida/datos.jsonl --output salida/kpi_por_endpoint_dia.csv

# 4. Reporte HTML
python generar_reporte.py --input salida/kpi_por_endpoint_dia.csv --output salida/reporte/kpi_diario.html --umbral_p90 300

# 5. ETL (alternativa Python)
python etl_pdi/etl_sqlite.py
```

---

## Bibliotecas utilizadas

- **requests**: Cliente HTTP
- **beautifulsoup4**, **lxml**: Parseo XML/HTML
- **numpy**: Cálculo de percentiles
- **pandas**: Procesamiento de datos
- **matplotlib**: Gráficos (reporte HTML)
- Estándar: `json`, `csv`, `datetime`, `argparse`

---

## Criterios cumplidos

- [x] Implementación correcta de cada tarea
- [x] Manejo de errores y excepciones
- [x] Código organizado y documentado
- [x] Uso apropiado de bibliotecas permitidas
- [x] Archivos de salida en formato especificado
- [x] Parámetros por línea de comandos
- [x] Documentación en README

---

## Licencia

Uso exclusivo para evaluación del Test Técnico - Somos TechCity.
