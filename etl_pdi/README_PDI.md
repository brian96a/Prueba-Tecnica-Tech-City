# ETL con Pentaho Data Integration (PDI)

## Requisitos previos

1. **Pentaho Data Integration (PDI)** instalado (Spoon, Kitchen, etc.)
   - Descarga: https://sourceforge.net/projects/pentaho/files/Data%20Integration/
   - O Pentaho 10.x desde Hitachi Vantara

2. **Generar los datos de entrada** antes de ejecutar PDI:
   ```bash
   python generar_datos.py --n_registros 500 --salida salida/datos.jsonl --seed 42
   python calcular_kpi.py --input salida/datos.jsonl --output salida/kpi_por_endpoint_dia.csv
   ```

## Configuración

### Conexión a SQLite

1. Abrir Spoon (cliente gráfico de PDI)
2. Crear conexión: **Herramientas → Conexiones → Nueva**
3. Tipo: **SQLite**
4. Configuración típica:
   - Base de datos: `./etl_pdi/kpi.db` (ruta relativa al proyecto)
   - O usar ruta absoluta según tu instalación

### Credenciales

Las credenciales de base de datos se almacenan en el repositorio local de PDI.
Para compartir el proyecto sin exponer credenciales, usa variables de entorno o
un archivo de configuración externo (no incluido en el repo por seguridad).

## Archivos

- **t_load_kpi.ktr**: Transformación que:
  - Lee `salida/kpi_por_endpoint_dia.csv` (CSV Input)
  - Tipifica columnas (fecha, entero, decimal)
  - Filtra filas inválidas (Filter Rows): `requests_total <= 0` o `p90_elapsed_ms < avg_elapsed_ms`
  - Carga en `stg_kpi_endpoint_dia` (staging)
  - Carga en `fct_kpi_endpoint_dia` (fact table, truncate para idempotencia)

- **j_daily_kpi.kjb**: Job que:
  - Ejecuta `t_load_kpi.ktr`
  - Verifica filas cargadas
  - Registra resultado en log

## Creación manual en Spoon (recomendado)

Los archivos .ktr y .kjb deben crearse en **Spoon** para garantizar compatibilidad.
Este directorio incluye documentación y un script Python alternativo que replica
la lógica ETL sin depender de PDI, para validación y CI/CD.

### Pasos para crear la transformación en Spoon

1. **CSV Input**
   - Archivo: `salida/kpi_por_endpoint_dia.csv`
   - Delimitador: `,`
   - Columnas: date_utc (Date), endpoint_base (String), requests_total (Integer),
     success_2xx, client_4xx, server_5xx, parse_errors (Integer),
     avg_elapsed_ms, p90_elapsed_ms (Number)

2. **Filter Rows**
   - Condición 1: `requests_total > 0`
   - Condición 2: `p90_elapsed_ms >= avg_elapsed_ms` (lógica: descartar si p90 < avg, anomalía)

3. **Table Output** (stg_kpi_endpoint_dia)
   - Tabla: stg_kpi_endpoint_dia
   - Opción: "Truncate table" desactivada para staging

4. **Table Output** (fct_kpi_endpoint_dia)
   - Tabla: fct_kpi_endpoint_dia
   - Opción: "Truncate table" para idempotencia

## Ejecución por línea de comandos

```bash
# Desde el directorio data-integration de PDI
./kitchen.sh -file=/ruta/test-tecnico-core/etl_pdi/j_daily_kpi.kjb -level=Basic
```

## Alternativa: ETL en Python (sin PDI)

Si no tienes PDI instalado, puedes usar el script `etl_sqlite.py` incluido
para cargar los datos en SQLite con la misma lógica.
