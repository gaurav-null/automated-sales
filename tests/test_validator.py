"""
tests/test_validator.py
Unit tests for data validation rules.
Run with: pytest
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from src.validator import validate


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.today_str = datetime.today().strftime('%Y-%m-%d')
        self.clean_row = {
            'deal_id': 'DEAL-1001',
            'deal_date': self.today_str,
            'rep_id': 'REP-101',
            'product_id': 'PRD-01',
            'amount': 15000.0,
            'status': 'closed'
        }

    def test_clean_record_passes(self):
        df = pd.DataFrame([self.clean_row])
        valid_df, quar_df = validate(df)
        self.assertEqual(len(valid_df), 1)
        self.assertEqual(len(quar_df), 0)

    def test_duplicate_deal_id_quarantined(self):
        row2 = self.clean_row.copy()
        df = pd.DataFrame([self.clean_row, row2])
        valid_df, quar_df = validate(df)
        self.assertEqual(len(valid_df), 1)
        self.assertEqual(len(quar_df), 1)
        self.assertIn('Duplicate', quar_df.iloc[0]['rejection_reason'])

    def test_missing_rep_id_quarantined(self):
        row = self.clean_row.copy()
        row['rep_id'] = None
        df = pd.DataFrame([row])
        valid_df, quar_df = validate(df)
        self.assertEqual(len(valid_df), 0)
        self.assertEqual(len(quar_df), 1)
        self.assertIn('Missing rep_id', quar_df.iloc[0]['rejection_reason'])

    def test_negative_amount_quarantined(self):
        row = self.clean_row.copy()
        row['amount'] = -500.0
        df = pd.DataFrame([row])
        valid_df, quar_df = validate(df)
        self.assertEqual(len(valid_df), 0)
        self.assertEqual(len(quar_df), 1)
        self.assertIn('Invalid or non-positive amount', quar_df.iloc[0]['rejection_reason'])

    def test_zero_amount_quarantined(self):
        row = self.clean_row.copy()
        row['amount'] = 0.0
        df = pd.DataFrame([row])
        valid_df, quar_df = validate(df)
        self.assertEqual(len(valid_df), 0)
        self.assertEqual(len(quar_df), 1)

    def test_future_date_quarantined(self):
        row = self.clean_row.copy()
        future = (datetime.today() + timedelta(days=365)).strftime('%Y-%m-%d')
        row['deal_date'] = future
        df = pd.DataFrame([row])
        valid_df, quar_df = validate(df)
        self.assertEqual(len(valid_df), 0)
        self.assertEqual(len(quar_df), 1)
        self.assertIn('Future date', quar_df.iloc[0]['rejection_reason'])

    def test_unmapped_rep_quarantined(self):
        row = self.clean_row.copy()
        row['rep_id'] = 'REP-UNKNOWN'
        df = pd.DataFrame([row])
        valid_df, quar_df = validate(df)
        self.assertEqual(len(valid_df), 0)
        self.assertEqual(len(quar_df), 1)
        self.assertIn('not found in dim_reps', quar_df.iloc[0]['rejection_reason'])

    def test_unmapped_product_quarantined(self):
        row = self.clean_row.copy()
        row['product_id'] = 'PRD-INVALID'
        df = pd.DataFrame([row])
        valid_df, quar_df = validate(df)
        self.assertEqual(len(valid_df), 0)
        self.assertEqual(len(quar_df), 1)
        self.assertIn('not found in dim_products', quar_df.iloc[0]['rejection_reason'])


if __name__ == '__main__':
    unittest.main()
