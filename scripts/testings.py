import sqlite3
import pandas as pd

conn = sqlite3.connect("ecom.db")
query = """
SELECT item_id, SUM(ad_spend) * 1.0 / SUM(clicks) AS cpc
FROM ad_sales_metrics
WHERE clicks > 0
GROUP BY item_id
ORDER BY cpc DESC
LIMIT 1;
"""
# query = """
# SELECT SUM(ad_sales) * 100.0 / SUM(ad_spend)
# FROM ad_sales_metrics
# WHERE ad_spend > 0;
# """
# query = """
# SELECT SUM(total_sales) FROM total_sales_metrics;
# """
# query = """
# SELECT ad_sales, total_sales FROM ad_sales_metrics INNER JOIN total_sales_metrics ON ad_sales_metrics.item_id = total_sales_metrics.item_id AND ad_sales_metrics.date = total_sales_metrics.date WHERE ad_sales_metrics.item_id = 4 AND ad_sales_metrics.date = '2025-06-01';
# """
# query = """
# SELECT SUM(ad_sales) FROM ad_sales_metrics WHERE item_id = 0 AND date = '2025-06-01';
# """
# query = """
# SELECT eligibility, message FROM product_eligibility WHERE item_id = 29 AND DATE(eligibility_datetime_utc) = '2025-06-04';
# """
# query = """
# SELECT item_id FROM ad_sales_metrics WHERE date = '2025-06-01' ORDER BY ad_spend DESC LIMIT 1
# """
# query = """
# SELECT SUM(total_units_ordered) 
# FROM total_sales_metrics 
# WHERE date BETWEEN '2025-06-01' AND '2025-06-30';
# """
# query = """
# SELECT item_id, ad_spend
# FROM ad_sales_metrics
# WHERE date = '2025-06-01'
# ORDER BY ad_spend DESC
# """
df = pd.read_sql_query(query, conn)
print(df.head(10))  # Show top 10 for clarity
conn.close()
