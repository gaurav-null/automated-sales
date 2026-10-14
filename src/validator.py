"""
src/validator.py
Description: Pandas-based validation engine.
Each rule is a separate function that receives the DataFrame,
tags invalid rows with a rejection_reason, and returns (valid_df, quarantine_df).
"""

import pandas as pd
from datetime import datetime


# Lookup sets (in production, these come from the database)
VALID_REP_IDS = {'REP-101', 'REP-102', 'REP-103', 'REP-104', 'REP-105', 'REP-106'}
VALID_PRODUCT_IDS = {'PRD-01', 'PRD-02', 'PRD-03', 'PRD-04', 'PRD-05'}


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Core validation pipeline.
    Runs all rule checks, collects bad rows into quarantine_df,
    and returns (valid_df, quarantine_df).
    """
    # Initialize rejection_reason column (empty means valid)
    df = df.copy()
    df['rejection_reason'] = ''

    # List of validation functions to run in order
    rules = [
        _rule_duplicate_deal_id,
        _rule_missing_rep_id,
        _rule_invalid_amount,
        _rule_invalid_date,
        _rule_unmapped_rep_id,
        _rule_unmapped_product_id,
    ]

    for rule_fn in rules:
        df = rule_fn(df)

    quarantine_df = df[df['rejection_reason'] != ''].copy()
    valid_df = df[df['rejection_reason'] == ''].drop(columns=['rejection_reason'])

    return valid_df.reset_index(drop=True), quarantine_df.reset_index(drop=True)


# ---- Individual Rule Functions ----

def _rule_duplicate_deal_id(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows where deal_id appears more than once."""
    dupes = df.duplicated(subset=['deal_id'], keep='first')
    is_blank = df['rejection_reason'] == ''
    mask = dupes & is_blank
    df.loc[mask, 'rejection_reason'] = 'Duplicate deal_id'
    return df


def _rule_missing_rep_id(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows where rep_id is null or empty."""
    mask = df['rep_id'].isnull() | (df['rep_id'].astype(str).str.strip() == '')
    mask = mask & (df['rejection_reason'] == '')
    df.loc[mask, 'rejection_reason'] = 'Missing rep_id'
    return df


def _rule_invalid_amount(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows where amount is not a positive number."""
    is_blank = df['rejection_reason'] == ''
    amount_numeric = pd.to_numeric(df['amount'], errors='coerce')
    mask = (amount_numeric.isnull() | (amount_numeric <= 0)) & is_blank
    df.loc[mask, 'rejection_reason'] = 'Invalid or non-positive amount'
    return df


def _rule_invalid_date(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows where deal_date cannot be parsed or is in the future."""
    is_blank = df['rejection_reason'] == ''
    today = pd.Timestamp(datetime.today().date())
    parsed_dates = pd.to_datetime(df['deal_date'], errors='coerce')

    bad_format = parsed_dates.isnull() & is_blank
    df.loc[bad_format, 'rejection_reason'] = 'Invalid date format'

    is_blank = df['rejection_reason'] == ''
    future_date = (parsed_dates > today) & is_blank
    df.loc[future_date, 'rejection_reason'] = 'Future date not allowed'

    return df


def _rule_unmapped_rep_id(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows where rep_id does not exist in the reference set."""
    is_blank = df['rejection_reason'] == ''
    not_null = df['rep_id'].notnull()
    mask = not_null & (~df['rep_id'].isin(VALID_REP_IDS)) & is_blank
    df.loc[mask, 'rejection_reason'] = 'rep_id not found in dim_reps'
    return df


def _rule_unmapped_product_id(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows where product_id does not exist in the reference set."""
    is_blank = df['rejection_reason'] == ''
    mask = (~df['product_id'].isin(VALID_PRODUCT_IDS)) & is_blank
    df.loc[mask, 'rejection_reason'] = 'product_id not found in dim_products'
    return df
