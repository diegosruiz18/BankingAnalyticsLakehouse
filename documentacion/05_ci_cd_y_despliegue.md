# 05. CI/CD & despliegue

## GitHub Actions

El workflow `.github/workflows/deploy-banking.yml` automatiza el despliegue de notebooks y la configuración/ejecución del Job de producción.

### Disparadores

- Push a la rama `main`.
- Ejecución manual mediante `workflow_dispatch`.

### Variables y secretos

**Secrets**
- `DATABRICKS_DEV_HOST`
- `DATABRICKS_DEV_TOKEN`
- `DATABRICKS_PROD_HOST`
- `DATABRICKS_PROD_TOKEN`

**Variables**
- `DATABRICKS_PROD_CLUSTER_NAME`

El workflow también define parámetros de catálogo, storage account, storage credential, rutas de notebooks y nombre del Job. No se almacenan tokens ni credenciales directamente en el repositorio.

### Flujo de despliegue

```text
Push a main / ejecución manual
            │
            ▼
Validar secrets y variables
            │
            ▼
Exportar 8 notebooks desde DEV
            │
            ▼
Importar notebooks en PROD
            │
            ▼
Obtener ID del clúster PROD
            │
            ▼
Eliminar Job anterior si existe
            │
            ▼
Crear Job multi-task en PROD
            │
            ▼
Validar configuración del Job
            │
            ▼
Ejecutar Job
            │
            ▼
Monitorear hasta SUCCESS / error
```

### Notebooks desplegados

1. `1.Preparacion_Ambiente_Banking`
2. `2.Ingest_SBS`
3. `3.Ingest_Fraud`
4. `4.Generacion_Banking`
5. `5.Ingest_Banking`
6. `6.Transform_Silver`
7. `7.Load_Golden`
8. `8.Grants_Banking`

El primer notebook se importa como SQL y los notebooks restantes como Python.

### Job de producción

- Nombre: `job_banking_analytics_lakehouse_prod`
- Tipo: `MULTI_TASK`
- Cluster: se resuelve por nombre usando `DATABRICKS_PROD_CLUSTER_NAME`
- Catálogo: `banking_prod`
- Storage Account: `adlsprojectbank12`
- Storage Credential: `credential-project`

Dependencias principales:
- La preparación del entorno precede a las ingestas SBS, fraude y generación sintética.
- La ingesta Banking depende de la generación de los CSV sintéticos.
- Silver espera la ingesta SBS, fraude y Banking.
- Golden espera la transformación Silver.
- Grants se ejecuta después de Golden.

## Validación posterior

- Revisar que las ocho tareas del Job estén definidas.
- Confirmar ejecución exitosa del Job.
- Verificar los conteos de Bronze, Silver y Golden.
- Confirmar que el dashboard y Genie consultan `banking_prod.golden`
