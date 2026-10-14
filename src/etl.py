"""
src/etl.py
Description: Main ETL pipeline runner.
Steps:
1. Read dirty CSV from data/raw/sales_transactions_dirty.csv
2. Run validator to split valid vs. quarantined rows
3. Load valid rows into fact_sales
4. Copy quarantine rows/records into quarantine_sales
5. Print an ETL summary log (addressing Kennect JD requirement for data discrepancy reporting)
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime
from sqlalchemy import text

# Add project root to path so we can import src.* modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.validator import validate
from src.db import get_engine


def run_etl(csv_path: str) -> dict:
    """
    1. Read CSV
    2. Validate
    3. Load clean rows and quarantine rows into the DB
    4. Print ETL summary report
    """
    # 1. Read
    print(f"[1/4] Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    total_records = len(df)
    print(f"       Found {total_records} raw records (including dirty rows).\n")

    # 2. Validate
    print("[2/4] Running validation rules...")
    t0 = time.time()
    valid_df, quarantine_df = validate(df)
    validate_time = round(time.time() - t0, 2)
    print(f"       VALID:      {len(valid_df)} records")
    print(f"       QUARANTINE: {len(quarantine_df)} records")
    print(f"       Validation completed in {validate_time}s.\n")

    if len(quarantine_df) > 0:
        print("[INFO] Quarantine breakdown by rejection reason:")
        for reason, count in quarantine_df['rejection_reason'].value_counts().items():
            print(f"       - {reason}: {count} row(s)")
        print()

    # 3. Load to PostgreSQL
    print("[3/4] Loading data to database...")
    t1 = time.time()
    engine = get_engine()

    valid_loaded = 0
    quar_loaded = 0

    if len(valid_df) > 0:
        valid_df['deal_date'] = pd.to_datetime(valid_df['deal_date'], errors='coerce')
        valid_df['amount'] = pd.to_numeric(valid_df['amount'], errors='coerce')
        valid_df.to_sql('fact_sales', engine, if_exists='append', index=False)
        valid_loaded = len(valid_df)
        print(f"       Inserted {valid_loaded} rows into fact_sales")

    if len(quarantine_df) > 0:
        quar_df = quarantine_df.copy()
        quar_df['quarantined_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Store amount as text since it may contain invalid values
        quar_df['amount'] = quar_df['amount'].astype(str)
        cols = [c for c in ['deal_id', 'deal_date', 'rep_id', 'product_id', 'amount', 'status', 'rejection_reason'] if c in quar_df.columns]
        quar_df[cols].to_sql('quarantine_sales', engine, if_exists='append', index=False)
        quar_loaded = len(quar_df)
        print(f"       Inserted {quar_loaded} rows into quarantine_sales")

    load_time = round(time.time() - t1, 2)
    print(f"       DB load completed in {load_time}s.\n")

    # 4. Save Quarantine CSV Report
    print("[4/4] Saving quarantine exception report...")
    if len(quarantine_df) > 0:
        os.makedirs('data/quarantined', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        quar_path = os.path.join('data', 'quarantined', f'exception_report_{timestamp}.csv')
        quarantine_df.to_csv(quar_path, index=False)
        print(f"       Saved: {quar_path}")
    else:
        print("       No quarantine records — all rows passed validation.\n")

    # 5. Summary
    line = "=" * 70
    print(f"\n{line}")
    print("  ETL PIPELINE SUMMARY")
    print(line)
    print(f"  File Processed    : {os.path.basename(csv_path)}")
    print(f"  Total Records     : {total_records}")
    print(f"  Valid (Ingested)  : {valid_loaded}")
    print(f"  Quarantined       : {quar_loaded}")
    print(f"  Validation Time   : {validate_time}s")
    print(f"  DB Load Time      : {load_time}s")
    print(line)
    print("  ETL completed successfully.")
    print(f"{line}\n")

    return {
        'total': total_records,
        'valid': valid_loaded,
        'quarantined': quar_loaded,
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    csv_path = 'data/raw/sales_transactions_dirty.csv'
    if not os.path.exists(csv_path):
        print(f"ERROR: Sample data not found. Run this first:\n  python generate_sample_data.py")
        sys.exit(1)

    run_etl(csv_path)
