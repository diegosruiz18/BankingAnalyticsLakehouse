# 01. Arquitectura técnica

## Resumen ejecutivo

Banking Analytics Lakehouse integra tres dominios de información: estadísticas SBS, transacciones de detección de fraude y datos bancarios sintéticos. La solución utiliza Azure Data Lake Storage como almacenamiento físico, Azure Databricks como motor de procesamiento y Unity Catalog como capa de gobierno.

La arquitectura implementa las capas Raw, Bronze, Silver y Golden. La capa Golden funciona como fuente de consumo para el dashboard AI/BI, Genie Agent y Delta Sharing hacia Power BI.

## Componentes

| Componente | Responsabilidad |
|---|---|
| Azure Data Lake Storage Gen2 | Almacenamiento de archivos Raw y tablas Delta externas. |
| Azure Databricks | Ejecución de notebooks PySpark y SQL. |
| Unity Catalog | Catálogo, esquemas, external locations, credenciales y permisos. |
| Delta Lake | Persistencia transaccional de las capas Bronze, Silver y Golden. |
| Databricks Workflows | Orquestación de las tareas de producción. |
| GitHub Actions | Exportación de notebooks desde DEV, importación en PROD y configuración/ejecución del Job. |
| Databricks AI/BI | Dashboard de indicadores bancarios y financieros. |
| Genie | Consultas conversacionales sobre tablas Golden. |
| Databricks Apps / Streamlit | Interfaz que integra Dashboard y Genie. |
| Delta Sharing | Compartir agregaciones Golden a Power BI. |

## Ambientes

| Recurso | DEV | PROD |
|---|---|---|
| Workspace | `adbproject-bank12` | `adbproject-bank12prod` |
| Catálogo | `banking_dev` | `banking_prod` |
| Storage Account | `adlsprojectbank12` | `adlsprojectbank12` |
| Storage credential | `credential-project` | `credential-project` |

La preparación del entorno parametriza `catalog_name` y `storage_account`. En producción, las ubicaciones físicas de Bronze, Silver y Golden utilizan el prefijo `banking_prod/`, separando los datos de DEV.

## Arquitectura Medallion

```text
SBS CSV ───────────┐
Fraud CSV ─────────┼──► ADLS Raw
Banking sintético ─┘       │
                           ▼
                    Bronze (11 tablas)
                    Ingesta + ingestion_date
                           │
                           ▼
                    Silver (11 tablas)
                    Limpieza + estandarización
                    + validaciones de calidad
                           │
                           ▼
                    Golden (11 tablas)
                    4 dimensiones
                    3 hechos
                    4 agregaciones
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      AI/BI Dashboard   Genie Agent    Delta Sharing
          │                │                │
          └──────────── Databricks App     Power BI
```

### Raw

Archivos de origen organizados por dominio:
- `raw/sbs/`: archivos SBS convertidos a CSV.
- `raw/fraud/creditcard.csv`: dataset de detección de fraude.
- `raw/banking/`: archivos sintéticos de clientes, cuentas, tarjetas, transacciones, préstamos y pagos.

### Bronze

La ingesta crea 11 tablas Delta externas:
- 4 tablas SBS.
- 1 tabla de transacciones de fraude.
- 6 tablas del dominio Banking.

Se conservan las estructuras de origen y se agrega `ingestion_date`.

### Silver

El notebook `6.Transform_Silver.ipynb` transforma las 11 tablas Bronze. Ejecuta limpieza de texto, estandarización, tratamiento de nulos y validaciones de claves y relaciones. La escritura se realiza después de superar las validaciones previas.

El dataset de fraude recibe una columna `transaction_date` simulada, dado que la fuente no contiene una fecha calendario.

### Golden

El notebook `7.Load_Golden.ipynb` construye el modelo dimensional y las agregaciones:
- Dimensiones: clientes, cuentas, tarjetas y calendario.
- Hechos: transacciones, préstamos y pagos.
- Agregaciones: fraude diario, créditos SBS, depósitos SBS y morosidad SBS.

Todas las tablas se registran como Delta externas con ubicaciones físicas en ADLS.

## Ubicaciones & Unity Catalog

El notebook `1.Preparacion_Ambiente_Banking.ipynb`:
1. Recibe catálogo, storage account y credencial como parámetros.
2. Define External Locations para `metastore`, `raw`, `bronze`, `silver` y `golden`.
3. Crea el catálogo y los esquemas `raw`, `bronze`, `silver` y `golden`.
4. Crea las tablas Delta externas y asigna sus rutas físicas.
5. Verifica el inventario y el tipo de las tablas.

## Notebooks del proceso

| Orden | Notebook | Función |
|---:|---|---|
| 1 | `1.Preparacion_Ambiente_Banking` | Catálogo, esquemas, external locations y tablas externas. |
| 2 | `2.Ingest_SBS` | Ingesta de SBS a Bronze. |
| 3 | `3.Ingest_Fraud` | Ingesta del dataset de fraude a Bronze. |
| 4 | `4.Generacion_Banking` | Generación de datos sintéticos en Raw. |
| 5 | `5.Ingest_Banking` | Ingesta de los CSV sintéticos a Bronze. |
| 6 | `6.Transform_Silver` | Transformación y validación Bronze → Silver. |
| 7 | `7.Load_Golden` | Construcción y validación Silver → Golden. |
| 8 | `8.Grants_Banking` | Administración de permisos Unity Catalog. |

## Consideraciones de ejecución

- Los procesos de ingesta y transformación documentados utilizan modo `FULL`.
- Silver realiza validaciones antes de sobrescribir sus tablas.
- Golden valida granularidad, claves e integridad referencial antes de escribir.
- La generación sintética sobrescribe los CSV de `raw/banking/` para mantener una fuente reproducible.
- Revisar [CI/CD y despliegue](./05_ci_cd_y_despliegue.md) antes de ejecutar el flujo en producción.
