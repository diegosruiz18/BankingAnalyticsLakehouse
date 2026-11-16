# 02. Catálogo de datos

## Alcance

El catálogo documenta las tablas implementadas en los esquemas `bronze`, `silver` y `golden` del catálogo Unity Catalog. Cada capa contiene 11 tablas.

- DEV: `banking_dev`
- PROD: `banking_prod`

## Modelo Golden

```text
dim_customer ─┐
dim_account ──┼──► fact_transactions
dim_card ─────┘          │
dim_date ────────────────┘

dim_customer ───────────► fact_loans ─────► fact_payments
dim_date ─────────────────────┘

agg_fraud_daily
agg_sbs_creditos
agg_sbs_depositos
agg_sbs_morosidad
```

El diagrama representa las entidades conceptuales; las relaciones físicas se implementan en las consultas y transformaciones de los notebooks.

## Bronze — 11 tablas

| Tabla | Dominio | Descripción |
|---|---|---|
| `sbs_creditos_sector_economico` | SBS | Créditos directos por sector económico y jerarquía. |
| `sbs_depositos_mn` | SBS | Movimiento de depósitos en moneda nacional. |
| `sbs_depositos_me` | SBS | Movimiento de depósitos en moneda extranjera. |
| `sbs_morosidad` | SBS | Morosidad por concepto, modalidad y entidad. |
| `fraud_transactions` | Fraude | Dataset de transacciones etiquetadas como legítimas o fraudulentas. |
| `customers` | Banking | Clientes sintéticos. |
| `accounts` | Banking | Cuentas sintéticas asociadas a clientes. |
| `cards` | Banking | Tarjetas sintéticas asociadas a cuentas. |
| `transactions` | Banking | Transacciones sintéticas asociadas a cuentas y, cuando corresponde, tarjetas. |
| `loans` | Banking | Préstamos sintéticos asociados a clientes. |
| `payments` | Banking | Pagos sintéticos asociados a préstamos. |

## Silver — 11 tablas

Silver conserva los dominios y nombres de Bronze:
- `sbs_creditos_sector_economico`
- `sbs_depositos_mn`
- `sbs_depositos_me`
- `sbs_morosidad`
- `fraud_transactions`
- `customers`
- `accounts`
- `cards`
- `transactions`
- `loans`
- `payments`

En esta capa se realizan limpieza de texto, estandarización de tipos, controles de nulos y claves, y validaciones de relaciones entre entidades. Para `fraud_transactions`, se incorpora `transaction_date` simulada a partir de la distribución diaria generada en el proceso.

## Golden — dimensiones

| Tabla | Granularidad / clave | Atributos principales |
|---|---|---|
| `dim_customer` | Una fila por `customer_id`, `customer_key` sustituta | `customer_segment`, `city`, `customer_status`. |
| `dim_account` | Una fila por `account_id`, `account_key` sustituta | `customer_id`, `account_type`, `currency`, `account_status`. |
| `dim_card` | Una fila por `card_id`, `card_key` sustituta | `account_id`, `card_type`, `card_brand`, `card_status`. |
| `dim_date` | Una fila por fecha; `date_key` | `full_date`, año, trimestre, mes, nombre de mes, día y día de semana. |

## Golden — hechos

| Tabla | Granularidad | Métricas / atributos |
|---|---|---|
| `fact_transactions` | Una fila por `transaction_id` | `amount`, `currency`, `transaction_type`, `channel`, `transaction_status`, `is_fraud`, claves de fecha/cliente/cuenta/tarjeta. |
| `fact_loans` | Una fila por `loan_id` | `principal_amount`, `interest_rate`, `term_months`, `loan_status`, `customer_id`. |
| `fact_payments` | Una fila por `payment_id` | `payment_amount`, `principal_paid`, `interest_paid`, `payment_status`, `payment_date`, `loan_id`. |


## Golden — agregaciones

| Tabla | Granularidad | Columnas principales |
|---|---|---|
| `agg_fraud_daily` | Una fila por `transaction_date` | `total_transactions`, `fraud_transactions`, `legitimate_transactions`, `fraud_amount`, `fraud_rate`. |
| `agg_sbs_creditos` | Fecha de corte, concepto y nivel jerárquico | `total_creditos_miles_soles`, `distribucion_pct`. |
| `agg_sbs_depositos` | Fecha de corte, empresa y moneda | `numero_cuentas`, `saldo_final_miles_soles`. |
| `agg_sbs_morosidad` | Fecha de corte, entidad y concepto de crédito | `morosidad_pct`. |

## Reglas de interpretación y calidad

### Dataset de fraude

- La fuente original incluye variables `V1` a `V28`, `Time`, `Amount` y `Class`.
- `Class` identifica la clase objetivo.
- La fecha de calendario utilizada en los análisis diarios se genera durante la transformación Silver; no es una fecha real del archivo fuente.
- `fraud_amount` se calcula a partir del importe del dataset y está expresado en EUR.
- El conjunto de fraude es independiente del dominio de transacciones bancarias sintéticas.

### SBS

- Los CSV utilizados corresponden al corte diciembre de 2025.
- Los importes de créditos y depósitos se expresan en miles de soles.
- En morosidad, el dashboard filtra `Total Créditos Directos` y excluye `TOTAL BANCA MÚLTIPLE` para el ranking de entidades.

### Banking sintético

Parámetros definidos por el notebook `4.Generacion_Banking.ipynb`

| Dataset | Registros configurados |
|---|---:|
| `customers` | 3,000 |
| `accounts` | 4,500 |
| `cards` | 3,000 |
| `transactions` | 150,000 |
| `loans` | 1,500 |
| `payments` | 15,000 |
| **Total** | **177,000** |

Los registros son sintéticos, no representan operaciones reales.

## Archivos fuente SBS versionados

| Archivo | Registros del CSV |
|---|---:|
| `sbs_creditos_sector_economico_2025-12.csv` | 39 |
| `sbs_morosidad_tipo_modalidad_2025-12_long.csv` | 1,113 |
| `sbs_movimiento_depositos_me_2025-12.csv` | 20 |
| `sbs_movimiento_depositos_mn_2025-12.csv` | 20 |

Los archivos originales XLS se encuentran en `datasets/sbs/original/`, los CSV usados por el notebook están en `datasets/sbs/convertido/`
