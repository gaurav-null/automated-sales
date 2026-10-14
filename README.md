<h1 align=center>automated-sales</h1>

<div align=center>

![Python](https://img.shields.io/badge/python-%2314354A.svg?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)
![GitHub last commit](https://img.shields.io/github/last-commit/gaurav-null/automated-sales?style=for-the-badge&labelColor=101418&color=9ccbfb)
![GitHub Repo stars](https://img.shields.io/github/stars/gaurav-null/automated-sales?style=for-the-badge&labelColor=101418&color=b9c8da)
![GitHub repo size](https://img.shields.io/github/repo-size/gaurav-null/automated-sales?style=for-the-badge&labelColor=101418&color=d3bfe6)
![Windows](https://img.shields.io/badge/Windows-%230078D6.svg?style=for-the-badge&logo=windows&logoColor=white)

</div>

> Automated Sales Incentive & Commission Calculation Engine — a SaaS-style ETL & Analytics pipeline (SPM/ICM) built with Python, Pandas, PostgreSQL Window Functions, Docker, and Streamlit.

> [!NOTE]
> Requires Docker (PostgreSQL) and Python 3.10+. Metabase / Looker Studio optional — Streamlit dashboard is included by default.

Scroll down for Screenshots!

## Components

-   **Language:** [`Python`](https://www.python.org/)
-   **Data Processing:** [`Pandas`](https://pandas.pydata.org/)
-   **Database:** [`PostgreSQL 16`](https://www.postgresql.org/) (Window Functions, CTEs)
-   **Containerization:** [`Docker`](https://www.docker.com/) / `docker-compose`
-   **Dashboard / BI:** [`Streamlit`](https://streamlit.io/) (Metabase / Looker Studio compatible)
-   **CI/CD:** [`GitHub Actions`](https://github.com/features/actions)
-   **Tested OS:** [`Windows 11`](https://www.microsoft.com/windows) (runs on any OS!)

## Installation

> [!NOTE]
> Fully manual install. No packaged installer **YET**.

> [!WARNING]
> Make sure PostgreSQL port `5432` is free, or change the port mapping in `docker-compose.yml`.

### Manual installation

Requirements:
-   [`Python 3.10+`](https://www.python.org/downloads/)
-   [`Docker Desktop`](https://www.docker.com/products/docker-desktop/)
-   [`pip`](https://pip.pypa.io/)

Build dependencies:

-   [`pandas`](https://pandas.pydata.org/)
-   [`sqlalchemy`](https://www.sqlalchemy.org/)
-   [`psycopg2-binary`](https://pypi.org/project/psycopg2-binary/)
-   [`streamlit`](https://streamlit.io/)
-   [`plotly`](https://plotly.com/python/)

### Installation
```sh
git clone https://github.com/gaurav-null/automated-sales.git
cd automated-sales
pip install -r requirements.txt

# Start PostgreSQL
docker compose up -d

# Initialize schema, seed dimensions & commission tiers
python src/init_db.py

# Generate messy sample data (with intentional dirty records)
python generate_sample_data.py

# Run the ETL pipeline (validate → quarantine → load → calculate)
python src/etl.py

# Launch the BI dashboard
streamlit run app/app.py
```

### Pipeline Flow

```
[Raw ERP / Client CSVs (dirty)]
        │
        ▼
[Pandas Validation Engine]  ──► quarantine_sales + exception_report.csv
        │ (clean rows)
        ▼
[PostgreSQL: fact_sales + dims]
        │
        ▼
[SQL CTEs + Window Functions]  ──► vw_monthly_rep_summary
        │
        ▼
[Streamlit Dashboard]  ──► Attainment gauges, leaderboards, payout breakdowns
```

### Commission Tiers

| Tier | Monthly Sales Range | Rate |
|------|---------------------|------|
| Base Tier | $0 – $50,000 | 5% |
| Growth Tier | $50,000.01 – $100,000 | 8% |
| Accelerator Tier | > $100,000 | 12% |

### Running Tests
```sh
python -m unittest discover tests
```

## Screenshots

<img width="1297" height="811" alt="1" src="https://github.com/user-attachments/assets/5d732d40-403f-4a33-b9ce-122f22272089" />


### Commission Statement Breakdown
<img width="1246" height="427" alt="3" src="https://github.com/user-attachments/assets/33ab6c77-cb83-4da8-ba42-8cf00cfd1a46" />


### Data Discrepancy & Quarantine Log
<img width="1314" height="943" alt="4" src="https://github.com/user-attachments/assets/4f6cd66c-345c-43f2-831d-1920812ef93a" />




