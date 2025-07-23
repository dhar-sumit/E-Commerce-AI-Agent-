DROP TABLE IF EXISTS product_eligibility;
DROP TABLE IF EXISTS ad_sales_metrics;
DROP TABLE IF EXISTS total_sales_metrics;

CREATE TABLE product_eligibility (
    eligibility_datetime_utc TEXT,
    item_id INTEGER,
    eligibility BOOLEAN,
    message TEXT
);

CREATE TABLE ad_sales_metrics (
    date TEXT,
    item_id INTEGER,
    ad_sales FLOAT,
    impressions INTEGER,
    ad_spend FLOAT,
    clicks INTEGER,
    units_sold INTEGER
);

CREATE TABLE total_sales_metrics (
    date TEXT,
    item_id INTEGER,
    total_sales FLOAT,
    total_units_ordered INTEGER
);