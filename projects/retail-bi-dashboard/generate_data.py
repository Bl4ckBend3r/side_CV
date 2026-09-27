from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
OUTPUT_DIR = Path(__file__).parent / "data"
random.seed(SEED)

PRODUCTS = [
    (1, "T-Shirt Basic", "Apparel", 39.90, 17.50),
    (2, "Hoodie Classic", "Apparel", 129.90, 61.00),
    (3, "Sneakers Urban", "Footwear", 219.90, 118.00),
    (4, "Backpack City", "Accessories", 159.90, 72.00),
    (5, "Cap Logo", "Accessories", 59.90, 19.00),
    (6, "Jeans Regular", "Apparel", 179.90, 88.00),
    (7, "Running Shoes", "Footwear", 289.90, 151.00),
    (8, "Winter Jacket", "Apparel", 399.90, 205.00),
]

STORES = [
    (1, "Warszawa Centrum", "Warszawa"),
    (2, "Poznan Plaza", "Poznan"),
    (3, "Wroclaw Rynek", "Wroclaw"),
    (4, "Zielona Gora Focus", "Zielona Gora"),
    (5, "Online", "E-commerce"),
]

START_DATE = date(2024, 1, 1)
END_DATE = date(2026, 8, 31)
N_ORDERS = 12_000


def write_csv(path: Path, header: list[str], rows: list[tuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def random_date() -> date:
    days = (END_DATE - START_DATE).days
    return START_DATE + timedelta(days=random.randint(0, days))


def generate_sales() -> list[tuple]:
    rows = []
    sale_id = 1
    for order_id in range(1, N_ORDERS + 1):
        order_date = random_date()
        store = random.choice(STORES)
        line_count = random.choices([1, 2, 3, 4], weights=[58, 27, 11, 4], k=1)[0]
        for _ in range(line_count):
            product = random.choice(PRODUCTS)
            qty = random.choices([1, 2, 3, 4], weights=[72, 19, 7, 2], k=1)[0]
            discount_pct = random.choices([0, 5, 10, 15, 20], weights=[62, 12, 14, 8, 4], k=1)[0]
            unit_price = product[3]
            unit_cost = product[4]
            gross_revenue = qty * unit_price
            net_revenue = gross_revenue * (1 - discount_pct / 100)
            gross_cost = qty * unit_cost
            rows.append((
                sale_id,
                order_id,
                order_date.strftime("%Y-%m-%d"),
                int(order_date.strftime("%Y%m%d")),
                product[0],
                store[0],
                qty,
                f"{unit_price:.2f}",
                discount_pct,
                f"{net_revenue:.2f}",
                f"{gross_cost:.2f}",
            ))
            sale_id += 1
    return rows


def generate_dates() -> list[tuple]:
    rows = []
    d = START_DATE
    while d <= END_DATE:
        rows.append((
            int(d.strftime("%Y%m%d")),
            d.strftime("%Y-%m-%d"),
            d.year,
            (d.month - 1) // 3 + 1,
            d.month,
            d.strftime("%B"),
            d.isocalendar().week,
            d.day,
            d.strftime("%A"),
        ))
        d += timedelta(days=1)
    return rows


def main() -> None:
    write_csv(
        OUTPUT_DIR / "products.csv",
        ["ProductKey", "ProductName", "Category", "ListPrice", "UnitCost"],
        PRODUCTS,
    )
    write_csv(
        OUTPUT_DIR / "stores.csv",
        ["StoreKey", "StoreName", "City"],
        STORES,
    )
    write_csv(
        OUTPUT_DIR / "dates.csv",
        ["DateKey", "Date", "Year", "Quarter", "MonthNumber", "MonthName", "ISOWeek", "Day", "DayName"],
        generate_dates(),
    )
    sales = generate_sales()
    write_csv(
        OUTPUT_DIR / "sales.csv",
        [
            "SaleKey", "OrderID", "OrderDate", "DateKey", "ProductKey", "StoreKey",
            "Quantity", "UnitPrice", "DiscountPct", "Revenue", "Cost"
        ],
        sales,
    )
    print(f"Generated {len(sales):,} fact rows in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
