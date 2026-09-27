from __future__ import annotations

import csv
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
DEMO = ROOT / "demo"
SOURCE = DEMO / "source"
DB_PATH = DEMO / "warehouse.db"

BATCHES = {
    "2026-09-01": {
        "customers": [
            (1, "Anna Kowalska", "Warszawa", "2026-09-01T08:00:00"),
            (2, "Jan Nowak", "Poznan", "2026-09-01T08:05:00"),
            (3, "Ola Zielinska", "Wroclaw", "2026-09-01T08:10:00"),
        ],
        "orders": [
            (1001, 1, "2026-09-01", 349.90, "2026-09-01T09:00:00"),
            (1002, 2, "2026-09-01", 129.00, "2026-09-01T09:15:00"),
            (1003, 3, "2026-09-01", 599.99, "2026-09-01T10:00:00"),
        ],
    },
    "2026-09-02": {
        "customers": [
            (2, "Jan Nowak", "Zielona Gora", "2026-09-02T07:30:00"),
            (4, "Marek Lis", "Gdansk", "2026-09-02T07:45:00"),
        ],
        "orders": [
            (1004, 2, "2026-09-02", 899.00, "2026-09-02T08:20:00"),
            (1005, 4, "2026-09-02", 249.50, "2026-09-02T08:35:00"),
        ],
    },
}


def write_csv(path: Path, header: list[str], rows: list[tuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def create_demo_sources() -> None:
    for batch_date, payload in BATCHES.items():
        folder = SOURCE / batch_date
        write_csv(
            folder / "customers.csv",
            ["CustomerID", "CustomerName", "City", "ModifiedAt"],
            payload["customers"],
        )
        write_csv(
            folder / "orders.csv",
            ["OrderID", "CustomerID", "OrderDate", "Amount", "ModifiedAt"],
            payload["orders"],
        )


def connect() -> sqlite3.Connection:
    DEMO.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_schema(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS ETLWatermark (
            SourceName TEXT PRIMARY KEY,
            LastModifiedAt TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS DimCustomer (
            CustomerSK INTEGER PRIMARY KEY AUTOINCREMENT,
            CustomerID INTEGER NOT NULL,
            CustomerName TEXT NOT NULL,
            City TEXT NOT NULL,
            ValidFrom TEXT NOT NULL,
            ValidTo TEXT,
            IsCurrent INTEGER NOT NULL CHECK (IsCurrent IN (0, 1)),
            UNIQUE(CustomerID, ValidFrom)
        );

        CREATE TABLE IF NOT EXISTS FactOrders (
            OrderID INTEGER PRIMARY KEY,
            CustomerSK INTEGER NOT NULL,
            OrderDate TEXT NOT NULL,
            Amount REAL NOT NULL CHECK (Amount >= 0),
            ModifiedAt TEXT NOT NULL,
            FOREIGN KEY(CustomerSK) REFERENCES DimCustomer(CustomerSK)
        );

        CREATE TABLE IF NOT EXISTS AuditLog (
            AuditID INTEGER PRIMARY KEY AUTOINCREMENT,
            BatchName TEXT NOT NULL,
            EntityName TEXT NOT NULL,
            RowsRead INTEGER NOT NULL,
            RowsLoaded INTEGER NOT NULL,
            RowsRejected INTEGER NOT NULL,
            LoadedAt TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS DataQualityLog (
            DQID INTEGER PRIMARY KEY AUTOINCREMENT,
            BatchName TEXT NOT NULL,
            EntityName TEXT NOT NULL,
            RecordKey TEXT,
            Issue TEXT NOT NULL,
            LoggedAt TEXT NOT NULL
        );
        """
    )
    for source in ("customers", "orders"):
        con.execute(
            "INSERT OR IGNORE INTO ETLWatermark(SourceName, LastModifiedAt) VALUES (?, ?)",
            (source, "1900-01-01T00:00:00"),
        )
    con.commit()


def get_watermark(con: sqlite3.Connection, source: str) -> str:
    row = con.execute(
        "SELECT LastModifiedAt FROM ETLWatermark WHERE SourceName = ?", (source,)
    ).fetchone()
    return row[0]


def set_watermark(con: sqlite3.Connection, source: str, value: str) -> None:
    con.execute(
        "UPDATE ETLWatermark SET LastModifiedAt = ? WHERE SourceName = ?",
        (value, source),
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def log_audit(con: sqlite3.Connection, batch: str, entity: str, read: int, loaded: int, rejected: int) -> None:
    con.execute(
        """
        INSERT INTO AuditLog(BatchName, EntityName, RowsRead, RowsLoaded, RowsRejected, LoadedAt)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (batch, entity, read, loaded, rejected, datetime.now().isoformat(timespec="seconds")),
    )


def log_dq(con: sqlite3.Connection, batch: str, entity: str, key: str, issue: str) -> None:
    con.execute(
        """
        INSERT INTO DataQualityLog(BatchName, EntityName, RecordKey, Issue, LoggedAt)
        VALUES (?, ?, ?, ?, ?)
        """,
        (batch, entity, key, issue, datetime.now().isoformat(timespec="seconds")),
    )


def load_customers(con: sqlite3.Connection, batch: str, path: Path) -> None:
    rows = read_csv(path)
    watermark = get_watermark(con, "customers")
    incremental = [r for r in rows if r["ModifiedAt"] > watermark]
    loaded = rejected = 0
    max_modified = watermark

    for row in incremental:
        try:
            customer_id = int(row["CustomerID"])
            name = row["CustomerName"].strip()
            city = row["City"].strip()
            modified = row["ModifiedAt"]
            datetime.fromisoformat(modified)
            if not name or not city:
                raise ValueError("CustomerName and City are required")

            current = con.execute(
                """
                SELECT CustomerSK, CustomerName, City
                FROM DimCustomer
                WHERE CustomerID = ? AND IsCurrent = 1
                """,
                (customer_id,),
            ).fetchone()

            if current is None:
                con.execute(
                    """
                    INSERT INTO DimCustomer(CustomerID, CustomerName, City, ValidFrom, ValidTo, IsCurrent)
                    VALUES (?, ?, ?, ?, NULL, 1)
                    """,
                    (customer_id, name, city, modified),
                )
                loaded += 1
            elif current[1] != name or current[2] != city:
                con.execute(
                    "UPDATE DimCustomer SET ValidTo = ?, IsCurrent = 0 WHERE CustomerSK = ?",
                    (modified, current[0]),
                )
                con.execute(
                    """
                    INSERT INTO DimCustomer(CustomerID, CustomerName, City, ValidFrom, ValidTo, IsCurrent)
                    VALUES (?, ?, ?, ?, NULL, 1)
                    """,
                    (customer_id, name, city, modified),
                )
                loaded += 1

            max_modified = max(max_modified, modified)
        except Exception as exc:
            rejected += 1
            log_dq(con, batch, "customers", row.get("CustomerID", ""), str(exc))

    set_watermark(con, "customers", max_modified)
    log_audit(con, batch, "customers", len(rows), loaded, rejected)


def customer_sk_for_order(con: sqlite3.Connection, customer_id: int, modified_at: str) -> int | None:
    row = con.execute(
        """
        SELECT CustomerSK
        FROM DimCustomer
        WHERE CustomerID = ?
          AND ValidFrom <= ?
          AND (ValidTo IS NULL OR ValidTo > ?)
        ORDER BY ValidFrom DESC
        LIMIT 1
        """,
        (customer_id, modified_at, modified_at),
    ).fetchone()
    return row[0] if row else None


def load_orders(con: sqlite3.Connection, batch: str, path: Path) -> None:
    rows = read_csv(path)
    watermark = get_watermark(con, "orders")
    incremental = [r for r in rows if r["ModifiedAt"] > watermark]
    loaded = rejected = 0
    max_modified = watermark
    seen: set[int] = set()

    for row in incremental:
        try:
            order_id = int(row["OrderID"])
            customer_id = int(row["CustomerID"])
            amount = float(row["Amount"])
            modified = row["ModifiedAt"]
            datetime.fromisoformat(modified)
            datetime.fromisoformat(row["OrderDate"])

            if order_id in seen:
                raise ValueError("Duplicate OrderID in source batch")
            seen.add(order_id)
            if amount < 0:
                raise ValueError("Amount cannot be negative")

            customer_sk = customer_sk_for_order(con, customer_id, modified)
            if customer_sk is None:
                raise ValueError("Customer dimension row not found")

            con.execute(
                """
                INSERT INTO FactOrders(OrderID, CustomerSK, OrderDate, Amount, ModifiedAt)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(OrderID) DO UPDATE SET
                    CustomerSK = excluded.CustomerSK,
                    OrderDate = excluded.OrderDate,
                    Amount = excluded.Amount,
                    ModifiedAt = excluded.ModifiedAt
                WHERE excluded.ModifiedAt > FactOrders.ModifiedAt
                """,
                (order_id, customer_sk, row["OrderDate"], amount, modified),
            )
            loaded += 1
            max_modified = max(max_modified, modified)
        except Exception as exc:
            rejected += 1
            log_dq(con, batch, "orders", row.get("OrderID", ""), str(exc))

    set_watermark(con, "orders", max_modified)
    log_audit(con, batch, "orders", len(rows), loaded, rejected)


def print_summary(con: sqlite3.Connection) -> None:
    print("\nCurrent customers:")
    for row in con.execute(
        "SELECT CustomerID, CustomerName, City, ValidFrom FROM DimCustomer WHERE IsCurrent = 1 ORDER BY CustomerID"
    ):
        print(row)

    print("\nCustomer history (SCD2):")
    for row in con.execute(
        "SELECT CustomerID, City, ValidFrom, ValidTo, IsCurrent FROM DimCustomer ORDER BY CustomerID, ValidFrom"
    ):
        print(row)

    revenue = con.execute("SELECT COUNT(*), ROUND(SUM(Amount), 2) FROM FactOrders").fetchone()
    print(f"\nFactOrders: {revenue[0]} rows, total amount = {revenue[1]}")

    print("\nWatermarks:")
    for row in con.execute("SELECT SourceName, LastModifiedAt FROM ETLWatermark ORDER BY SourceName"):
        print(row)


def main() -> None:
    create_demo_sources()
    con = connect()
    init_schema(con)

    for batch in sorted(BATCHES):
        load_customers(con, batch, SOURCE / batch / "customers.csv")
        load_orders(con, batch, SOURCE / batch / "orders.csv")
        con.commit()

    print_summary(con)
    con.close()
    print(f"\nWarehouse created at: {DB_PATH}")


if __name__ == "__main__":
    main()
