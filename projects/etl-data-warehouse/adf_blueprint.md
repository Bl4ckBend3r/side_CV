# Azure Data Factory deployment blueprint

This document maps the local ETL implementation to an Azure Data Factory design. It is an architecture blueprint for portfolio purposes and does not claim a live Azure deployment.

## Proposed Azure architecture

```text
Azure Blob Storage / ADLS Gen2
          |
          v
Azure Data Factory
  |-- Get Metadata
  |-- Lookup Watermark
  |-- Copy Activity
  |-- Data Flow / Stored Procedure
  |-- Data Quality checks
  |-- Update Watermark
          |
          v
Azure SQL Database / SQL Server
  |-- DimCustomer (SCD2)
  |-- FactOrders
  |-- AuditLog
  |-- DataQualityLog
          |
          v
Power BI
```

## Pipeline: `PL_Load_Daily_Sales`

### 1. Get Metadata
Checks whether the expected customer and order files are present in the landing zone.

### 2. Lookup Watermark
Reads `dbo.ETLWatermark` to obtain the latest successfully processed `ModifiedAt` value for each source.

### 3. Copy Activity - Customers
Copies only customer rows newer than the customer watermark into a staging table.

Suggested source filter:

```sql
SELECT *
FROM source.Customers
WHERE ModifiedAt > @Watermark;
```

### 4. Customer SCD2 processing
Use either a Mapping Data Flow or a stored procedure to:

1. match source records on `CustomerID`,
2. detect changed descriptive attributes,
3. expire the current row by setting `ValidTo` and `IsCurrent = 0`,
4. insert a new current version.

### 5. Copy Activity - Orders
Loads order records newer than the fact-table watermark.

### 6. Fact upsert
Upserts new or corrected orders to `FactOrders` using `OrderID` as the business key and `ModifiedAt` for conflict resolution.

### 7. Data-quality checks
Execute SQL checks for:

- negative order amounts,
- missing customer dimension keys,
- duplicate business keys,
- more than one current SCD2 record per customer,
- null mandatory attributes.

Rejected rows are written to `DataQualityLog`.

### 8. Audit logging
A Stored Procedure Activity writes counts of read, loaded and rejected rows to `AuditLog`.

### 9. Update Watermark
Only after successful completion, update `ETLWatermark` with the maximum processed `ModifiedAt` value.

## Error handling

Use ADF dependency conditions:

- **Succeeded** -> update watermark and complete pipeline,
- **Failed** -> write failure details to audit storage and do not advance the watermark,
- **Completed** -> optional notification step.

## Parameters

Recommended pipeline parameters:

- `p_source_container`
- `p_batch_date`
- `p_customer_file`
- `p_order_file`
- `p_environment`

## Security for a real deployment

- store secrets in Azure Key Vault,
- use Managed Identity where possible,
- use private endpoints for Azure SQL / Storage in production,
- grant least-privilege permissions,
- do not store credentials inside pipeline JSON.

## Power BI layer

Power BI connects to the curated warehouse layer rather than raw files. Recommended refresh strategy:

- Import mode for a small/medium demo,
- incremental refresh for growing fact tables,
- scheduled refresh after successful ADF pipeline execution.

## Skills demonstrated

This architecture maps the runnable local project to common BI engineering concepts: Azure Data Factory orchestration, incremental ETL, watermarks, SCD Type 2, data quality, auditability, SQL warehousing and Power BI consumption.
