# Power BI DAX Measures

Create a dedicated `Measures` table in Power BI and add the following measures.

```DAX
Revenue =
SUM ( FactSales[Revenue] )
```

```DAX
Cost =
SUM ( FactSales[Cost] )
```

```DAX
Gross Margin =
[Revenue] - [Cost]
```

```DAX
Gross Margin % =
DIVIDE ( [Gross Margin], [Revenue] )
```

```DAX
Units Sold =
SUM ( FactSales[Quantity] )
```

```DAX
Orders =
DISTINCTCOUNT ( FactSales[OrderID] )
```

```DAX
Average Order Value =
DIVIDE ( [Revenue], [Orders] )
```

```DAX
Revenue YTD =
TOTALYTD ( [Revenue], DimDate[Date] )
```

```DAX
Revenue Previous Year =
CALCULATE ( [Revenue], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
```

```DAX
Revenue YoY % =
DIVIDE ( [Revenue] - [Revenue Previous Year], [Revenue Previous Year] )
```

```DAX
Margin per Unit =
DIVIDE ( [Gross Margin], [Units Sold] )
```

## Suggested dashboard visuals

- KPI cards: Revenue, Gross Margin %, Units Sold, Average Order Value
- Line chart: Revenue by Month
- Clustered bar chart: Revenue and Gross Margin by Category
- Matrix: Store x Category with Revenue and Margin
- Waterfall: YoY revenue change
- Slicers: Year, Quarter, Store, Category
