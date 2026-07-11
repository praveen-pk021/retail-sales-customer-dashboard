# Retail Sales & Customer Insights Dashboard

This project builds a practical retail analytics portfolio piece around the Olist Brazilian E-commerce dataset. It includes a SQLite database layer, SQL analysis queries, a Python analysis script, and an interactive Streamlit dashboard for business exploration.

## What this project covers

- Load raw Olist CSV files into a local SQLite database
- Write reusable SQL for business questions
- Explore delivery performance, revenue trends, and customer behavior
- Build a dashboard with filters for date range, state, and product category
- Prepare a portfolio-ready project for GitHub and Streamlit Cloud

## Project structure

```text
retails_sales_customer/
├── app/
│   └── app.py
├── data/
├── notebooks/
│   ├── analysis.py
│   └── build_db.py
├── sql/
│   ├── analysis_queries.sql
│   └── schema.sql
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

1. Download the Olist dataset from Kaggle and place the CSV files in the data folder.
   Required files include:
   - olist_customers_dataset.csv
   - olist_geolocation_dataset.csv
   - olist_orders_dataset.csv
   - olist_order_items_dataset.csv
   - olist_payments_dataset.csv
   - olist_products_dataset.csv
   - olist_sellers_dataset.csv
   - olist_order_reviews_dataset.csv
   - product_category_name_translation.csv

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Build the SQLite database:

```bash
python notebooks/build_db.py
```

4. Run the analysis script:

```bash
python notebooks/analysis.py
```

5. Start the Streamlit dashboard:

```bash
streamlit run app/app.py
```

## Deployment

1. Push the repo to GitHub.
2. Open Streamlit Community Cloud.
3. Connect the repository and select app/app.py as the entry point.
4. Deploy and share the live URL in your README.

## Key findings

Analysis of the full Olist dataset found:

- Peak revenue was R$1,179,143.77 in November 2017.
- `beleza_saude` was the top product category by revenue at R$1,441,248.07.
- The repeat customer rate was 3.12%.
- Roraima (RR) had the slowest average delivery time at 29.39 days.
- Late deliveries received a 2.57 average review score, compared with 4.22 for on-time orders.
