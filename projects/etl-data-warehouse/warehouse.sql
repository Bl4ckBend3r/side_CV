/* Incremental ETL & Data Warehouse - Microsoft SQL Server target schema */

CREATE TABLE dbo.ETLWatermark (
    SourceName       VARCHAR(100)  NOT NULL PRIMARY KEY,
    LastModifiedAt   DATETIME2(0)  NOT NULL
);

CREATE TABLE dbo.DimCustomer (
    CustomerSK       INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    CustomerID       INT               NOT NULL,
    CustomerName     NVARCHAR(150)     NOT NULL,
    City             NVARCHAR(100)     NOT NULL,
    ValidFrom        DATETIME2(0)      NOT NULL,
    ValidTo          DATETIME2(0)      NULL,
    IsCurrent        BIT               NOT NULL,
    CONSTRAINT UQ_DimCustomer_Version UNIQUE (CustomerID, ValidFrom)
);

CREATE INDEX IX_DimCustomer_BusinessKey
    ON dbo.DimCustomer(CustomerID, IsCurrent, ValidFrom);

CREATE TABLE dbo.FactOrders (
    OrderID          BIGINT         NOT NULL PRIMARY KEY,
    CustomerSK       INT            NOT NULL,
    OrderDate        DATE           NOT NULL,
    Amount           DECIMAL(14,2)  NOT NULL,
    ModifiedAt       DATETIME2(0)   NOT NULL,
    CONSTRAINT FK_FactOrders_DimCustomer
        FOREIGN KEY (CustomerSK) REFERENCES dbo.DimCustomer(CustomerSK),
    CONSTRAINT CK_FactOrders_Amount CHECK (Amount >= 0)
);

CREATE TABLE dbo.AuditLog (
    AuditID          BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    BatchName        VARCHAR(100)  NOT NULL,
    EntityName       VARCHAR(100)  NOT NULL,
    RowsRead         INT           NOT NULL,
    RowsLoaded       INT           NOT NULL,
    RowsRejected     INT           NOT NULL,
    LoadedAt         DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.DataQualityLog (
    DQID             BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    BatchName        VARCHAR(100)   NOT NULL,
    EntityName       VARCHAR(100)   NOT NULL,
    RecordKey        VARCHAR(150)   NULL,
    Issue            NVARCHAR(500)  NOT NULL,
    LoggedAt         DATETIME2(0)   NOT NULL DEFAULT SYSUTCDATETIME()
);

/* Seed watermarks */
INSERT INTO dbo.ETLWatermark(SourceName, LastModifiedAt)
VALUES
    ('customers', '19000101'),
    ('orders', '19000101');

/* BI validation query */
SELECT
    YEAR(f.OrderDate) AS [Year],
    MONTH(f.OrderDate) AS [Month],
    d.City,
    COUNT_BIG(*) AS Orders,
    SUM(f.Amount) AS Revenue,
    AVG(f.Amount) AS AverageOrderValue
FROM dbo.FactOrders f
JOIN dbo.DimCustomer d
    ON d.CustomerSK = f.CustomerSK
GROUP BY YEAR(f.OrderDate), MONTH(f.OrderDate), d.City
ORDER BY [Year], [Month], d.City;

/* SCD2 quality check: one current version per business key */
SELECT CustomerID, COUNT(*) AS CurrentVersions
FROM dbo.DimCustomer
WHERE IsCurrent = 1
GROUP BY CustomerID
HAVING COUNT(*) <> 1;
