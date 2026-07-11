import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "retail_dashboard.db"


def load_query(query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def main() -> None:
    print("Loading analysis from SQLite database...")
    if not DB_PATH.exists():
        raise FileNotFoundError("Database not found. Run notebooks/build_db.py first.")

    queries = {
        "monthly_revenue": """
            SELECT substr(o.order_purchase_timestamp, 1, 7) AS month,
                   ROUND(SUM(oi.price + oi.freight_value), 2) AS revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY 1
            ORDER BY 1
        """,
        "top_categories": """
            SELECT p.product_category_name AS category,
                   ROUND(SUM(oi.price + oi.freight_value), 2) AS revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT 10
        """,
        "repeat_customer_rate": """
            WITH customer_order_counts AS (
                SELECT c.customer_unique_id,
                       COUNT(DISTINCT o.order_id) AS order_count
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_unique_id
            )
            SELECT ROUND(100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_customer_rate_pct
            FROM customer_order_counts
        """,
        "delivery_by_state": """
            SELECT c.customer_state AS state,
                   ROUND(AVG(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)), 2) AS avg_delivery_days
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_delivered_customer_date IS NOT NULL
            GROUP BY c.customer_state
            ORDER BY avg_delivery_days DESC
        """,
    }

    results = {name: load_query(query) for name, query in queries.items()}

    print("\nMonthly revenue trend")
    print(results["monthly_revenue"].head())

    print("\nTop categories")
    print(results["top_categories"].head())

    print("\nRepeat customer rate")
    print(results["repeat_customer_rate"])

    print("\nAverage delivery time by state")
    print(results["delivery_by_state"].head())


if __name__ == "__main__":
    main()
