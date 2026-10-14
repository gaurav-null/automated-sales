automated-sales/
├── data/
│   ├── raw/                 # Incoming messy client CSVs
│   ├── quarantined/         # Rejected rows with rejection reasons
│   └── seed/                # Master reference data (reps, products, quotas)
├── sql/
│   ├── 01_schema.sql        # Table definitions (Dims, Fact, Quarantine)
│   ├── 02_seed.sql          # Seed data for dims
│   └── 03_calculations.sql  # Views & CTEs with Window Functions for payout & attainment
├── src/
│   ├── __init__.py
│   ├── db.py                # Database connection utility (SQLAlchemy / psycopg2 / SQLite fallback)
│   ├── validator.py         # Pandas-based data validation & quarantine logic
│   └── etl.py               # Main pipeline: Read -> Validate -> Load -> Calculate
├── app/
│   ├── __init__.py
│   └── app.py               # Streamlit dashboard
├── tests/
│   └── test_validator.py    # Unit tests for the validation engine
├── generate_sample_data.py  # Script to generate realistic dirty & clean sales data
├── docker-compose.yml       # PostgreSQL container setup
├── requirements.txt
└── README.md
