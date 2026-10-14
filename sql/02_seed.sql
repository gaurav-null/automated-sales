-- ============================================================
-- Seed Dimensions Data
-- ============================================================

-- Reps
INSERT INTO dim_reps (rep_id, rep_name, email, region, start_date) VALUES
('REP-101', 'Alice Johnson', 'alice.johnson@salescorp.com', 'North America', '2022-01-15'),
('REP-102', 'Bob Smith',     'bob.smith@salescorp.com',     'North America', '2022-03-01'),
('REP-103', 'Carlos Gomez',  'carlos.gomez@salescorp.com',  'LATAM',         '2021-08-20'),
('REP-104', 'Diana Prince',  'diana.prince@salescorp.com',  'EMEA',          '2023-02-10'),
('REP-105', 'Evan Wright',   'evan.wright@salescorp.com',   'APAC',          '2022-11-05'),
('REP-106', 'Fiona Gallagher','fiona.g@salescorp.com',      'EMEA',          '2023-06-01')
ON CONFLICT (rep_id) DO NOTHING;

-- Products
INSERT INTO dim_products (product_id, product_name, category, base_price) VALUES
('PRD-01', 'Enterprise Cloud Suite',   'Software',    15000.00),
('PRD-02', 'Data Analytics Platform',  'Software',    10000.00),
('PRD-03', 'API Integration Package',  'Software',     5000.00),
('PRD-04', 'Professional Services Tier A', 'Services', 8000.00),
('PRD-05', '24/7 Dedicated Support',   'Support',      3000.00)
ON CONFLICT (product_id) DO NOTHING;

-- Monthly Quotas ($50k - $90k range)
INSERT INTO dim_quotas (rep_id, period_month, quota_amount) VALUES
('REP-101', '2024-01-01', 60000.00),
('REP-102', '2024-01-01', 50000.00),
('REP-103', '2024-01-01', 75000.00),
('REP-104', '2024-01-01', 80000.00),
('REP-105', '2024-01-01', 65000.00),
('REP-106', '2024-01-01', 45000.00),
-- February Quotas
('REP-101', '2024-02-01', 60000.00),
('REP-102', '2024-02-01', 50000.00),
('REP-103', '2024-02-01', 75000.00),
('REP-104', '2024-02-01', 80000.00),
('REP-105', '2024-02-01', 65000.00),
('REP-106', '2024-02-01', 45000.00)
ON CONFLICT (rep_id, period_month) DO NOTHING;

-- Commission Tiers:
-- Tier 1: $0 - $50,000 -> 5.0%
-- Tier 2: $50,000 - $100,000 -> 8.0%
-- Tier 3: > $100,000 (Accelerator) -> 12.0%
INSERT INTO dim_commission_tiers (tier_name, min_amount, max_amount, commission_pct) VALUES
('Base Tier',       0.00,      50000.00,  5.00),
('Growth Tier',     50000.01,  100000.00, 8.00),
('Accelerator Tier',100000.01, NULL,     12.00)
ON CONFLICT (tier_name) DO NOTHING;
