# Autor: Brian Stiven Avila
# Escribe los .ktr y .kjb para pentaho (plantilla basica)

from pathlib import Path

T_LOAD_KPI_KTR = '''<?xml version="1.0" encoding="UTF-8"?>
<transformation>
  <info>
    <name>t_load_kpi</name>
    <description>Carga KPI desde CSV a SQLite</description>
    <trans_version>1</trans_version>
    <trans_type>Normal</trans_type>
  </info>
  <connection>
    <name>SQLite-kpi</name>
    <type>SQLITE</type>
    <database>${Internal.Transformation.Filename.Directory}/etl_pdi/kpi.db</database>
  </connection>
  <step>
    <name>CSV file input</name>
    <type>CSVInput</type>
    <filename>${Internal.Transformation.Filename.Directory}/../salida/kpi_por_endpoint_dia.csv</filename>
    <delimiter>,</delimiter>
    <header>Y</header>
  </step>
  <step>
    <name>Filter rows</name>
    <type>FilterRows</type>
  </step>
  <step>
    <name>Table output stg</name>
    <type>TableOutput</type>
    <connection>SQLite-kpi</connection>
    <table>stg_kpi_endpoint_dia</table>
  </step>
  <step>
    <name>Table output fct</name>
    <type>TableOutput</type>
    <connection>SQLite-kpi</connection>
    <table>fct_kpi_endpoint_dia</table>
  </step>
</transformation>
'''

J_DAILY_KPI_KJB = '''<?xml version="1.0" encoding="UTF-8"?>
<job>
  <name>j_daily_kpi</name>
  <description>Ejecuta t_load_kpi</description>
  <job_version>1</job_version>
  <entry>
    <name>t_load_kpi</name>
    <type>TRANS</type>
    <filename>${Internal.Job.Filename.Directory}/t_load_kpi.ktr</filename>
  </entry>
</job>
'''


def main():
    base = Path(__file__).parent
    (base / "t_load_kpi.ktr").write_text(T_LOAD_KPI_KTR, encoding="utf-8")
    (base / "j_daily_kpi.kjb").write_text(J_DAILY_KPI_KJB, encoding="utf-8")
    print("listo: t_load_kpi.ktr y j_daily_kpi.kjb (abre spoon para ajustar)")


if __name__ == "__main__":
    main()
