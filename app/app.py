"""
app/app.py
Description: Streamlit BI Dashboard for Automated Sales Incentive & Commission Calculation
Kennect Features Demonstrated:
- Executive Summary: Total Revenue, Total Payout, Effective Commission %
- Quota Attainment % gauge & Leaderboard
- Individual Rep Commission Statements
- Discrepancy & Quarantine Audit Log
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from dotenv import load_dotenv

# Load env variables and local modules
load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.db import get_engine

# --- Page Config ---
st.set_page_config(
    page_title="Sales Commission & Incentive Engine",
    page_icon="💼",
    layout="wide",
)

st.title("💼 Sales Incentive & Commission Calculation Engine")
st.markdown("Automated SPM/ICM pipeline showcasing **ETL Data Cleaning**, **Tiered Commission Logic (SQL)**, and **Attainment Analytics**.")

# --- Database Connection ---
@st.cache_resource
def get_db_connection():
    try:
        engine = get_engine()
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        return None

engine = get_db_connection()

if not engine:
    st.error(
        "Could not connect to the database. Make sure PostgreSQL is running:\n\n"
        "```bash\ndocker compose up -d\n```\n"
        "And that you ran the ETL pipeline:\n\n"
        "```bash\npython generate_sample_data.py\npython src/etl.py\n```"
    )
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filter Criteria")

# Fetch available months
with engine.connect() as conn:
    months_df = pd.read_sql("SELECT DISTINCT period_month FROM vw_monthly_rep_summary ORDER BY period_month", conn)
    reps_df = pd.read_sql("SELECT rep_id, rep_name, region FROM dim_reps ORDER BY rep_name", conn)

months = months_df['period_month'].astype(str).tolist() if not months_df.empty else []
regions = ['All'] + list(reps_df['region'].unique()) if not reps_df.empty else ['All']

selected_month = st.sidebar.selectbox("Period Month", options=months) if months else None
selected_region = st.sidebar.selectbox("Region", options=regions)

# --- Query Filtered Data ---
query = """
    SELECT
        s.rep_id,
        s.rep_name,
        r.region,
        s.period_month,
        s.quota_amount,
        s.total_sales_amount,
        s.attainment_pct,
        s.tier_name,
        s.commission_pct,
        s.commission_payout
    FROM vw_monthly_rep_summary s
    JOIN dim_reps r ON s.rep_id = r.rep_id
    WHERE 1=1
"""
params = {}
if selected_month:
    query += " AND s.period_month = :month"
    params['month'] = selected_month
if selected_region != 'All':
    query += " AND r.region = :region"
    params['region'] = selected_region

query += " ORDER BY s.attainment_pct DESC"

with engine.connect() as conn:
    df = pd.read_sql(text(query), conn, params=params)

if df.empty:
    st.warning("No data found for the selected filters. Make sure the database is seeded and the ETL has run.")
    st.stop()

# --- KPI Cards ---
st.markdown("### Executive Summary")
col1, col2, col3, col4 = st.columns(4)

total_sales = df['total_sales_amount'].sum()
total_payout = df['commission_payout'].sum()
avg_attainment = df['attainment_pct'].mean()
effective_rate = (total_payout / total_sales * 100) if total_sales > 0 else 0

col1.metric("Total Revenue Closed", f"${total_sales:,.2f}")
col2.metric("Total Commission Payout", f"${total_payout:,.2f}")
col3.metric("Avg Quota Attainment", f"{avg_attainment:.1f}%")
col4.metric("Effective Commission Rate", f"{effective_rate:.2f}%")

st.divider()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Leaderboard & Attainment", "Commission Statements", "Data Discrepancy & Quarantine Log"])

# TAB 1: Leaderboard
with tab1:
    st.subheader("Quota Attainment by Sales Representative")
    
    # Leaderboard bar chart
    fig = px.bar(
        df,
        x='rep_name',
        y='attainment_pct',
        color='tier_name',
        title="Quota Attainment % (100% = Quota Reached)",
        labels={'rep_name': 'Sales Rep', 'attainment_pct': 'Attainment %', 'tier_name': 'Tier'},
        text=df['attainment_pct'].apply(lambda x: f"{x:.1f}%"),
        color_discrete_map={
            'Base Tier': '#6baed6',
            'Growth Tier': '#3182bd',
            'Accelerator Tier': '#08519c'
        }
    )
    # Add 100% Quota Target Reference Line
    fig.add_shape(
        type='line',
        x0=-0.5,
        x1=len(df) - 0.5,
        y0=100,
        y1=100,
        line=dict(color='Red', width=2, dash='dash'),
    )
    fig.add_annotation(
        x=len(df)-1,
        y=105,
        text="100% Target Quota",
        showarrow=False,
        font=dict(color='Red')
    )
    st.plotly_chart(fig, use_container_width=True)

# TAB 2: Commission Statements Breakdown
with tab2:
    st.subheader("Detailed Rep Commission Breakdown")
    
    display_df = df[[
        'rep_id', 'rep_name', 'region', 'quota_amount',
        'total_sales_amount', 'attainment_pct', 'tier_name',
        'commission_pct', 'commission_payout'
    ]].copy()

    # Formatting currency & percentages for display
    display_df['quota_amount'] = display_df['quota_amount'].apply(lambda x: f"${x:,.2f}")
    display_df['total_sales_amount'] = display_df['total_sales_amount'].apply(lambda x: f"${x:,.2f}")
    display_df['attainment_pct'] = display_df['attainment_pct'].apply(lambda x: f"{x:.1f}%")
    display_df['commission_pct'] = display_df['commission_pct'].apply(lambda x: f"{x:.1f}%")
    display_df['commission_payout'] = display_df['commission_payout'].apply(lambda x: f"${x:,.2f}")

    display_df.columns = [
        'Rep ID', 'Rep Name', 'Region', 'Monthly Quota',
        'Sales Closed', 'Attainment %', 'Tier Applied',
        'Commission Rate', 'Payout Amount'
    ]
    st.dataframe(display_df, use_container_width=True)

# TAB 3: Data Discrepancy & Quarantine Log
with tab3:
    st.subheader("Data Ingestion & Discrepancy Audit Log")
    st.markdown("Records quarantined automatically by the **Pandas Validation Engine** due to schema violations, missing rep IDs, duplicates, or negative amounts.")
    
    with engine.connect() as conn:
        quarantine_df = pd.read_sql(
            "SELECT deal_id, deal_date, rep_id, product_id, amount, rejection_reason, quarantined_at FROM quarantine_sales ORDER BY id DESC",
            conn
        )
    
    if not quarantine_df.empty:
        col_summary, col_pie = st.columns([1, 1])
        with col_summary:
            st.metric("Total Quarantined Records", len(quarantine_df))
            st.dataframe(quarantine_df[['rejection_reason']].value_counts().reset_index(name='count'), use_container_width=True)

        with col_pie:
            pie_fig = px.pie(
                quarantine_df,
                names='rejection_reason',
                title='Quarantine Distribution by Rejection Reason',
                hole=0.4
            )
            st.plotly_chart(pie_fig, use_container_width=True)

        st.markdown("#### Quarantined Deal Records")
        st.dataframe(quarantine_df, use_container_width=True)
    else:
        st.success("No records have been quarantined yet. Ingestion is clean!")
