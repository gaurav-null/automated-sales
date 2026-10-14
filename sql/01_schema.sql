-- ============================================================
-- Schema: Automated Sales Incentive & Commission Calculation
-- ============================================================

-- Dimension: Sales Representatives
CREATE TABLE IF NOT EXISTS dim_reps (
    rep_id      VARCHAR(10) PRIMARY KEY,
    rep_name    VARCHAR(100) NOT NULL,
    email       VARCHAR(150),
    region      VARCHAR(50) NOT NULL,
    start_date  DATE NOT NULL
);

-- Dimension: Products
CREATE TABLE IF NOT EXISTS dim_products (
    product_id   VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category     VARCHAR(50),
    base_price   NUMERIC(12,2)
);

-- Dimension: Monthly Quotas per Rep
CREATE TABLE IF NOT EXISTS dim_quotas (
    quota_id     SERIAL PRIMARY KEY,
    rep_id       VARCHAR(10) REFERENCES dim_reps(rep_id),
    period_month DATE NOT NULL,          -- first day of month e.g. '2024-01-01'
    quota_amount NUMERIC(12,2) NOT NULL,
    UNIQUE(rep_id, period_month)
);

-- Dimension: Commission Tiers (tiered rate structure)
CREATE TABLE IF NOT EXISTS dim_commission_tiers (
    tier_id        SERIAL PRIMARY KEY,
    tier_name      VARCHAR(50) NOT NULL UNIQUE,
    min_amount     NUMERIC(12,2) NOT NULL,
    max_amount     NUMERIC(12,2),           -- NULL means unlimited
    commission_pct NUMERIC(5,2) NOT NULL    -- e.g. 5.00 means 5%
);

-- Fact: Clean Sales Transactions
CREATE TABLE IF NOT EXISTS fact_sales (
    deal_id      VARCHAR(20) PRIMARY KEY,
    deal_date    DATE NOT NULL,
    rep_id       VARCHAR(10) REFERENCES dim_reps(rep_id),
    product_id   VARCHAR(10) REFERENCES dim_products(product_id),
    amount       NUMERIC(12,2) NOT NULL,
    status       VARCHAR(20) DEFAULT 'closed'
);

-- Quarantine: Rejected rows from ingestion
CREATE TABLE IF NOT EXISTS quarantine_sales (
    id               SERIAL PRIMARY KEY,
    deal_id          VARCHAR(20),
    deal_date        VARCHAR(50),
    rep_id           VARCHAR(20),
    product_id       VARCHAR(20),
    amount           VARCHAR(50),
    status           VARCHAR(20),
    rejection_reason TEXT NOT NULL,
    quarantined_at   TIMESTAMP DEFAULT NOW()
);
