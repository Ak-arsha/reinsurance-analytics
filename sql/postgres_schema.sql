-- postgres_schema.sql : PostgreSQL DDL for the core star schema (NOT executed by the author - test before use).
-- Load: export CSVs with python/export_core_csv.py, then:  \copy dim_region FROM 'data/core_csv/dim_region.csv' CSV HEADER   (etc.)
-- The MI views in 04_mi_views.sql need three edits for PostgreSQL:
--   substr(txn_date,1,7)      -> to_char(txn_date,'YYYY-MM')
--   julianday(a)-julianday(b) -> (a - b)
--   INTEGER division casts    -> CAST(... AS INTEGER) works unchanged; ROUND(x, n) needs x::numeric
CREATE TABLE dim_region (region_id SERIAL PRIMARY KEY, region_name TEXT UNIQUE NOT NULL);
CREATE TABLE dim_lob (lob_id SERIAL PRIMARY KEY, lob_name TEXT UNIQUE NOT NULL);
CREATE TABLE dim_underwriter (underwriter_id SERIAL PRIMARY KEY, underwriter_name TEXT UNIQUE NOT NULL);
CREATE TABLE dim_cedant (cedant_id SERIAL PRIMARY KEY, cedant_code TEXT UNIQUE, cedant_name TEXT, country TEXT, cedant_type TEXT, rating TEXT);
CREATE TABLE dim_treaty (
  treaty_id TEXT PRIMARY KEY, cedant_id INT REFERENCES dim_cedant, lob_id INT REFERENCES dim_lob,
  region_id INT REFERENCES dim_region, underwriter_id INT REFERENCES dim_underwriter, treaty_type TEXT,
  underwriting_year INT, inception_date DATE, expiry_date DATE, currency CHAR(3), share_pct NUMERIC(5,2),
  limit_usd NUMERIC(18,2), retention_usd NUMERIC(18,2), est_annual_premium_usd NUMERIC(18,2), dq_flag TEXT);
CREATE TABLE dim_date (date_key DATE PRIMARY KEY, year INT, quarter INT, month INT, year_month TEXT, year_quarter TEXT);
CREATE TABLE fact_premium (premium_id TEXT PRIMARY KEY, treaty_id TEXT REFERENCES dim_treaty, txn_date DATE REFERENCES dim_date,
  original_currency CHAR(3), gross_written_premium NUMERIC(18,2), ceded_premium NUMERIC(18,2), commission NUMERIC(18,2),
  earned_premium NUMERIC(18,2), earned_commission NUMERIC(18,2));
CREATE TABLE fact_claims (claim_id TEXT PRIMARY KEY, treaty_id TEXT REFERENCES dim_treaty, loss_date DATE REFERENCES dim_date,
  report_date DATE, claim_type TEXT, paid_amount NUMERIC(18,2), case_reserve NUMERIC(18,2), incurred_amount NUMERIC(18,2),
  status TEXT, exceeds_limit SMALLINT, dq_flag TEXT);
CREATE TABLE fact_exposure (treaty_id TEXT PRIMARY KEY REFERENCES dim_treaty, as_of_date DATE, sum_insured_usd NUMERIC(18,2),
  limit_exposure_usd NUMERIC(18,2), peak_zone TEXT);
CREATE INDEX ix_prem_treaty ON fact_premium(treaty_id);  CREATE INDEX ix_claim_treaty ON fact_claims(treaty_id);
