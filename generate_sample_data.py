"""
Script: generate_sample_data.py
Description: Generates realistic sales transaction CSVs with dirty/corrupt records
to demonstrate the ETL & Validation engine.
"""

import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_sample_sales():
    random.seed(42)
    os.makedirs('data/raw', exist_ok=True)

    reps = ['REP-101', 'REP-102', 'REP-103', 'REP-104', 'REP-105', 'REP-106']
    products = ['PRD-01', 'PRD-02', 'PRD-03', 'PRD-04', 'PRD-05']
    
    records = []
    start_date = datetime(2024, 1, 1)

    # 1. Generate ~200 Clean Records
    for i in range(1, 201):
        deal_id = f"DEAL-{1000 + i}"
        deal_date = (start_date + timedelta(days=random.randint(0, 59))).strftime('%Y-%m-%d')
        rep_id = random.choice(reps)
        product_id = random.choice(products)
        amount = round(random.uniform(2000, 10000), 2)
        records.append({
            'deal_id': deal_id,
            'deal_date': deal_date,
            'rep_id': rep_id,
            'product_id': product_id,
            'amount': amount,
            'status': 'closed'
        })

    # 2. Inject Dirty / Bad Records (addresses Kennect JD requirement)
    
    # 5 Duplicate deal_ids
    for i in range(5):
        records.append({
            'deal_id': f"DEAL-100{i+1}", # Duplicate!
            'deal_date': '2024-01-15',
            'rep_id': random.choice(reps),
            'product_id': random.choice(products),
            'amount': 12000.00,
            'status': 'closed'
        })

    # 4 Rows with Missing/Null Rep IDs
    for i in range(4):
        records.append({
            'deal_id': f"DEAL-900{i+1}",
            'deal_date': '2024-01-20',
            'rep_id': None, # Missing rep
            'product_id': random.choice(products),
            'amount': 9500.00,
            'status': 'closed'
        })

    # 3 Negative / Zero Amounts
    records.append({
        'deal_id': 'DEAL-8001',
        'deal_date': '2024-01-22',
        'rep_id': 'REP-101',
        'product_id': 'PRD-01',
        'amount': -4500.00, # Negative amount
        'status': 'closed'
    })
    records.append({
        'deal_id': 'DEAL-8002',
        'deal_date': '2024-01-23',
        'rep_id': 'REP-102',
        'product_id': 'PRD-02',
        'amount': 0.00, # Zero amount
        'status': 'closed'
    })

    # 3 Invalid / Future Dates
    records.append({
        'deal_id': 'DEAL-8003',
        'deal_date': '2099-12-31', # Future Date
        'rep_id': 'REP-103',
        'product_id': 'PRD-03',
        'amount': 15000.00,
        'status': 'closed'
    })
    records.append({
        'deal_id': 'DEAL-8004',
        'deal_date': 'not-a-valid-date', # Bad Date Format
        'rep_id': 'REP-104',
        'product_id': 'PRD-04',
        'amount': 18000.00,
        'status': 'closed'
    })

    # 3 Unmapped / Non-existent Product SKUs or Rep IDs
    records.append({
        'deal_id': 'DEAL-8005',
        'deal_date': '2024-02-05',
        'rep_id': 'REP-999', # Unknown Rep
        'product_id': 'PRD-01',
        'amount': 22000.00,
        'status': 'closed'
    })
    records.append({
        'deal_id': 'DEAL-8006',
        'deal_date': '2024-02-06',
        'rep_id': 'REP-101',
        'product_id': 'PRD-UNKNOWN-SKU', # Unknown Product
        'amount': 7000.00,
        'status': 'closed'
    })

    # Shuffle records
    random.shuffle(records)

    df = pd.DataFrame(records)
    output_path = 'data/raw/sales_transactions_dirty.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records (including intentional dirty records) at {output_path}")

if __name__ == "__main__":
    generate_sample_sales()
