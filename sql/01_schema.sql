-- 01_schema.sql : mapping, core (star schema), data-quality and reference tables.
-- Written for SQLite so the project runs anywhere; see sql/postgres_schema.sql for PostgreSQL DDL.
-- Layers: stg_* (raw, created by Python)  ->  map_* + dq_*  ->  dim_* / fact_* (core)  ->  v_* (MI views)

CREATE TABLE map_region        (source_value TEXT, mapped_value TEXT, source_system TEXT, effective_date TEXT, added_by TEXT, added_on TEXT);
CREATE TABLE map_lob           (source_value TEXT, mapped_value TEXT, source_system TEXT, effective_date TEXT, added_by TEXT, added_on TEXT);
CREATE TABLE map_claim_status  (source_value TEXT, mapped_value TEXT, source_system TEXT, effective_date TEXT, added_by TEXT, added_on TEXT);
CREATE TABLE map_currency      (source_value TEXT, mapped_value TEXT, rate_to_usd REAL, source_system TEXT, effective_date TEXT, added_by TEXT, added_on TEXT);
CREATE TABLE map_treaty_id     (source_ref TEXT PRIMARY KEY, treaty_id TEXT, rule TEXT);   -- System C 'TR-0045' -> 'T0045'

CREATE TABLE ref_assumptions   (key TEXT PRIMARY KEY, value REAL, note TEXT);
INSERT INTO ref_assumptions VALUES
 ('admin_expense_ratio', 0.05, 'Assumed non-commission expense ratio applied to earned premium in the combined ratio'),
 ('watchlist_limit_utilisation', 0.80, 'Treaties with incurred above this share of limit go on the watchlist'),
 ('fx_basis', 1.0, 'Single valuation-date FX rate per currency (map_currency); no historic rates');

CREATE TABLE dq_check_log (
  run_ts TEXT, check_id TEXT, check_name TEXT, category TEXT, severity TEXT,
  records_tested INTEGER, records_failed INTEGER, status TEXT, action_taken TEXT);
CREATE TABLE dq_failed_records (
  check_id TEXT, source_table TEXT, src_row INTEGER, record_key TEXT, detail TEXT, disposition TEXT);

-- ---------- dimensions ----------
CREATE TABLE dim_region      (region_id INTEGER PRIMARY KEY AUTOINCREMENT, region_name TEXT UNIQUE);
CREATE TABLE dim_lob         (lob_id INTEGER PRIMARY KEY AUTOINCREMENT, lob_name TEXT UNIQUE);
CREATE TABLE dim_underwriter (underwriter_id INTEGER PRIMARY KEY AUTOINCREMENT, underwriter_name TEXT UNIQUE);
CREATE TABLE dim_cedant      (cedant_id INTEGER PRIMARY KEY AUTOINCREMENT, cedant_code TEXT UNIQUE, cedant_name TEXT,
                              country TEXT, cedant_type TEXT, rating TEXT);
CREATE TABLE dim_treaty (
  treaty_id TEXT PRIMARY KEY, cedant_id INTEGER REFERENCES dim_cedant, lob_id INTEGER REFERENCES dim_lob,
  region_id INTEGER REFERENCES dim_region, underwriter_id INTEGER REFERENCES dim_underwriter,
  treaty_type TEXT, underwriting_year INTEGER, inception_date TEXT, expiry_date TEXT, currency TEXT,
  share_pct REAL, limit_usd REAL, retention_usd REAL, est_annual_premium_usd REAL, dq_flag TEXT);
CREATE TABLE dim_date (date_key TEXT PRIMARY KEY, year INTEGER, quarter INTEGER, month INTEGER,
                       year_month TEXT, year_quarter TEXT);

-- ---------- facts (all amounts in USD at valuation-date FX) ----------
CREATE TABLE fact_premium (
  premium_id TEXT PRIMARY KEY, treaty_id TEXT REFERENCES dim_treaty, txn_date TEXT, original_currency TEXT,
  gross_written_premium REAL, ceded_premium REAL, commission REAL, earned_premium REAL, earned_commission REAL);
CREATE TABLE fact_claims (
  claim_id TEXT PRIMARY KEY, treaty_id TEXT REFERENCES dim_treaty, loss_date TEXT, report_date TEXT, claim_type TEXT,
  paid_amount REAL, case_reserve REAL, incurred_amount REAL, status TEXT, exceeds_limit INTEGER, dq_flag TEXT);
CREATE TABLE fact_exposure (
  treaty_id TEXT PRIMARY KEY REFERENCES dim_treaty, as_of_date TEXT, sum_insured_usd REAL,
  limit_exposure_usd REAL, peak_zone TEXT);

CREATE INDEX ix_prem_treaty ON fact_premium(treaty_id);
CREATE INDEX ix_prem_date   ON fact_premium(txn_date);
CREATE INDEX ix_claim_treaty ON fact_claims(treaty_id);
CREATE INDEX ix_claim_date  ON fact_claims(loss_date);
