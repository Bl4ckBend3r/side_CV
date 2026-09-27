# Retail Sales BI Dashboard

Portfolio project built to demonstrate a complete BI workflow: synthetic source data -> SQL star schema -> Power BI semantic model -> DAX measures and business KPIs.

## Business scenario

A retail company needs one dashboard for management to monitor revenue, margin, units sold, average order value and performance by product, store and time.

## Stack

- Python - reproducible synthetic data generation
- Microsoft SQL Server - dimensional model / star schema
- Power BI - dashboard and semantic model
- Power Query - data preparation
- DAX - KPI calculations and time intelligence

## Architecture

```text
Python generator
      |
      v
CSV source files
      |
      v
SQL Server staging
      |
      v
Star schema
DimDate ----|
DimProduct -|--> FactSales --> Power BI --> Dashboard / KPIs
DimStore ---|
```

## Repository files

- `generate_data.py` - generates reproducible retail transactions and dimension source files
- `schema.sql` - SQL Server staging and star-schema DDL plus loading queries
- `dax_measures.md` - ready-to-use Power BI measures

## KPIs

- Revenue
- Gross Margin
- Gross Margin %
- Units Sold
- Average Order Value
- Revenue YTD
- Revenue Previous Year
- Revenue YoY %
- Revenue by category, store and month

## How to run

1. Run `python generate_data.py`.
2. The script creates files in `data/`.
3. Create a SQL Server database and execute `schema.sql`.
4. Import the generated CSV files into the staging tables.
5. Execute the load statements from `schema.sql`.
6. Connect Power BI to SQL Server.
7. Create relationships according to the star schema.
8. Add the measures from `dax_measures.md`.

## Power BI model

Relationships:

- `DimDate[DateKey]` 1:* `FactSales[DateKey]`
- `DimProduct[ProductKey]` 1:* `FactSales[ProductKey]`
- `DimStore[StoreKey]` 1:* `FactSales[StoreKey]`

Recommended report pages:

1. Executive Overview
2. Product Performance
3. Store Performance
4. Time Analysis

## Portfolio focus

This project demonstrates dimensional modelling, SQL, ETL preparation, Power BI, Power Query, DAX and business-oriented KPI design. Data is synthetic and generated locally, so the project contains no confidential information.
