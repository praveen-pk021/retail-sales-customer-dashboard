import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "retail_dashboard.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

FILE_MAP = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_payments_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "product_category_name_translation": "product_category_name_translation.csv",
}


def resolve_data_dir(explicit_path: str | None) -> Path:
    candidate = Path(explicit_path).expanduser() if explicit_path else DEFAULT_DATA_DIR
    if candidate.exists() and candidate.is_dir():
        return candidate
    if candidate.exists() and candidate.is_file():
        raise FileNotFoundError(f"Expected a folder path, but got a file: {candidate}")
    raise FileNotFoundError(
        f"Dataset folder not found: {candidate}. Place the Olist CSV files in the data folder or pass the folder path as an argument."
    )


def find_csv_path(data_dir: Path, csv_name: str) -> Path:
    direct_path = data_dir / csv_name
    if direct_path.exists():
        return direct_path

    matches = list(data_dir.rglob(csv_name))
    if matches:
        return matches[0]

    raise FileNotFoundError(f"Missing dataset file: {csv_name} in {data_dir}")


def load_csv_to_db(table_name: str, csv_name: str, data_dir: Path, conn: sqlite3.Connection) -> None:
    csv_path = find_csv_path(data_dir, csv_name)
    df = pd.read_csv(csv_path)
    conn.execute(f"DELETE FROM {table_name}")
    df.to_sql(table_name, conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {table_name} from {csv_path}")


def main() -> None:
    explicit_path = sys.argv[1] if len(sys.argv) > 1 else None
    data_dir = resolve_data_dir(explicit_path)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    for table_name, csv_name in FILE_MAP.items():
        load_csv_to_db(table_name, csv_name, data_dir, conn)

    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")


if __name__ == "__main__":
    main()
