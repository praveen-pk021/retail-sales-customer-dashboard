-- 1) Monthly revenue trend
SELECT substr(o.order_purchase_timestamp, 1, 7) AS month,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY 1
ORDER BY 1;

-- 2) Top product categories by revenue
SELECT p.product_category_name AS category,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;

-- 3) Repeat customer rate
WITH customer_order_counts AS (
    SELECT c.customer_unique_id,
           COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
)
SELECT ROUND(100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_customer_rate_pct
FROM customer_order_counts;

-- 4) Average delivery time by customer state
SELECT c.customer_state AS state,
       ROUND(AVG(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)), 2) AS avg_delivery_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_days DESC;

-- 5) Late delivery percentage and its relation to review score
WITH delivery_metrics AS (
    SELECT o.order_id,
           CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END AS late_delivery,
           MAX(r.review_score) AS review_score
    FROM orders o
    LEFT JOIN reviews r ON o.order_id = r.order_id
    GROUP BY o.order_id
)
SELECT CASE WHEN late_delivery = 1 THEN 'Late' ELSE 'On Time' END AS delivery_status,
       COUNT(*) AS orders,
       ROUND(AVG(review_score), 2) AS avg_review_score
FROM delivery_metrics
GROUP BY delivery_status;

-- 6) Revenue and order volume by payment type
SELECT p.payment_type,
       COUNT(DISTINCT o.order_id) AS orders,
       ROUND(SUM(p.payment_value), 2) AS revenue
FROM payments p
JOIN orders o ON p.order_id = o.order_id
GROUP BY p.payment_type
ORDER BY revenue DESC;

-- 7) Average review score by product category
SELECT p.product_category_name AS category,
       ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY avg_review_score DESC;
