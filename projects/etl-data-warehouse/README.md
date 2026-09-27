# Incremental ETL & Data Warehouse

Portfolio project demonstrating an end-to-end ETL pipeline with incremental loading, data-quality checks, a star-schema warehouse and Slowly Changing Dimension Type 2 logic. The project is runnable locally and includes a deployment blueprint for Azure Data Factory.

## Business scenario

An e-commerce company receives daily customer and order extracts. The BI layer must load only new or changed records, preserve customer history and expose clean warehouse tables for Power BI reporting.

## Stack

- Python - orchestration, validation and incremental ETL
- SQL / SQLite - runnable local warehouse
- Microsoft SQL Server - target production-style DDL in `warehouse.sql`
- Azure Data Factory - architecture/deployment mapping in `adf_blueprint.md`
- Power BI - intended reporting layer

## ETL flow

```text
Raw CSV extracts
      |
      v
Validation / deduplication
      |
      v
Watermark check
      |
      +--> DimCustomer (SCD Type 2)
      |
      +--> FactOrders (incremental append/upsert)
      |
      v
AuditLog + DataQualityLog
      |
      v
Power BI semantic model
```

## Files

- `etl_pipeline.py` - complete local ETL demo with synthetic source data, watermark loading, SCD2 and audit logging
- `warehouse.sql` - SQL Server warehouse schema and validation queries
- `adf_blueprint.md` - mapping of the local pipeline to Azure Data Factory components

## How to run

```bash
python etl_pipeline.py
```

The script creates a local `demo/` directory, generates two daily source batches and processes them into `warehouse.db`. Run it repeatedly to see idempotent incremental behaviour.

## What this project demonstrates

- incremental loads
- watermark strategy
- SCD Type 2
- dimensional modelling
- ETL orchestration
- data-quality checks
- audit logging
- SQL warehouse design
- Azure Data Factory architecture concepts

## Important note

The Azure section is an implementation blueprint, not a claim that the project has been deployed to a live Azure subscription. The local version is fully runnable and mirrors the control flow that would be implemented in Azure Data Factory.
