#!/usr/bin/env python3
"""Export the core tables and MI views to CSV so Power BI / Qlik can load them without an ODBC driver."""
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ["dim_treaty", "dim_cedant", "dim_lob", "dim_region", "dim_underwriter", "dim_date",
          "fact_premium", "fact_claims", "fact_exposure", "dq_check_log", "dq_failed_records"]
VIEWS = ["v_treaty_summary", "v_monthly_trend", "v_watchlist", "v_unmapped_values", "v_dq_health"]


def main(root=ROOT):
    root = Path(root); out = root / "data" / "core_csv"; out.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(root / "data" / "reinsurance.db")
    for t in TABLES + VIEWS:
        pd.read_sql(f"SELECT * FROM {t}", con).to_csv(out / f"{t}.csv", index=False)
    print(f"Exported {len(TABLES) + len(VIEWS)} tables/views to {out}")


if __name__ == "__main__":
    main()
