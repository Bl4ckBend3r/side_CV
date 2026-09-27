/* Retail Sales BI Dashboard - SQL Server star schema */

IF OBJECT_ID('dbo.FactSales', 'U') IS NOT NULL DROP TABLE dbo.FactSales;
IF OBJECT_ID('dbo.DimStore', 'U') IS NOT NULL DROP TABLE dbo.DimStore;
IF OBJECT_ID('dbo.DimProduct', 'U') IS NOT NULL DROP TABLE dbo.DimProduct;
IF OBJECT_ID('dbo.DimDate', 'U') IS NOT NULL DROP TABLE dbo.DimDate;

CREATE TABLE dbo.DimDate (
    DateKey       INT          NOT NULL PRIMARY KEY,
    [Date]        DATE         NOT NULL,
    [Year]        SMALLINT     NOT NULL,
    [Quarter]     TINYINT      NOT NULL,
    MonthNumber   TINYINT      NOT NULL,
    MonthName     VARCHAR(20)  NOT NULL,
    ISOWeek       TINYINT      NOT NULL,
    [Day]         TINYINT      NOT NULL,
    DayName       VARCHAR(20)  NOT NULL
);

CREATE TABLE dbo.DimProduct (
    ProductKey    INT           NOT NULL PRIMARY KEY,
    ProductName   VARCHAR(120)  NOT NULL,
    Category      VARCHAR(80)   NOT NULL,
    ListPrice     DECIMAL(12,2) NOT NULL,
    UnitCost      DECIMAL(12,2) NOT NULL
);

CREATE TABLE dbo.DimStore (
    StoreKey      INT           NOT NULL PRIMARY KEY,
    StoreName     VARCHAR(120)  NOT NULL,
    City          VARCHAR(80)   NOT NULL
);

CREATE TABLE dbo.FactSales (
    SaleKey       BIGINT        NOT NULL PRIMARY KEY,
    OrderID       BIGINT        NOT NULL,
    DateKey       INT           NOT NULL,
    ProductKey    INT           NOT NULL,
    StoreKey      INT           NOT NULL,
    Quantity      INT           NOT NULL,
    UnitPrice     DECIMAL(12,2) NOT NULL,
    DiscountPct   DECIMAL(5,2)  NOT NULL,
    Revenue       DECIMAL(14,2) NOT NULL,
    Cost          DECIMAL(14,2) NOT NULL,
    CONSTRAINT FK_FactSales_DimDate FOREIGN KEY (DateKey) REFERENCES dbo.DimDate(DateKey),
    CONSTRAINT FK_FactSales_DimProduct FOREIGN KEY (ProductKey) REFERENCES dbo.DimProduct(ProductKey),
    CONSTRAINT FK_FactSales_DimStore FOREIGN KEY (StoreKey) REFERENCES dbo.DimStore(StoreKey)
);

CREATE INDEX IX_FactSales_DateKey ON dbo.FactSales(DateKey);
CREATE INDEX IX_FactSales_ProductKey ON dbo.FactSales(ProductKey);
CREATE INDEX IX_FactSales_StoreKey ON dbo.FactSales(StoreKey);

/*
Suggested staging tables mirror the generated CSV files. After BULK INSERT,
load dimensions first and FactSales last.

Example business validation query:
*/
SELECT
    d.[Year],
    d.MonthNumber,
    p.Category,
    s.StoreName,
    SUM(f.Revenue) AS Revenue,
    SUM(f.Revenue - f.Cost) AS GrossMargin,
    SUM(f.Quantity) AS Units
FROM dbo.FactSales f
JOIN dbo.DimDate d ON d.DateKey = f.DateKey
JOIN dbo.DimProduct p ON p.ProductKey = f.ProductKey
JOIN dbo.DimStore s ON s.StoreKey = f.StoreKey
GROUP BY d.[Year], d.MonthNumber, p.Category, s.StoreName
ORDER BY d.[Year], d.MonthNumber, p.Category, s.StoreName;
