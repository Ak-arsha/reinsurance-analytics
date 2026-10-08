-- 04_mi_views_postgres.sql : PostgreSQL management-information layer.
-- Compatible with PostgreSQL 12+.

CREATE OR REPLACE VIEW v_treaty_summary AS
WITH p AS (SELECT treaty_id, SUM(gross_written_premium) gwp, SUM(ceded_premium) ceded, SUM(commission) commission,
                  SUM(earned_premium) earned, SUM(earned_commission) earned_commission
           FROM fact_premium GROUP BY treaty_id),
     c AS (SELECT treaty_id, COUNT(*) claim_count, SUM(paid_amount) paid, SUM(case_reserve) reserve,
                  SUM(incurred_amount) incurred,
                  SUM(CASE WHEN status IN ('Open','Reopened') THEN incurred_amount ELSE 0 END) open_incurred
           FROM fact_claims GROUP BY treaty_id)
SELECT t.treaty_id, ce.cedant_code, ce.cedant_name, ce.country AS cedant_country, ce.rating,
       l.lob_name, r.region_name, u.underwriter_name, t.treaty_type, t.underwriting_year,
       t.inception_date, t.expiry_date, t.limit_usd, t.retention_usd, t.dq_flag,
       COALESCE(p.gwp,0) gwp, COALESCE(p.ceded,0) ceded, COALESCE(p.gwp,0)-COALESCE(p.ceded,0) net_premium,
       COALESCE(p.commission,0) commission, COALESCE(p.earned,0) earned, COALESCE(p.earned_commission,0) earned_commission,
       COALESCE(c.claim_count,0) claim_count, COALESCE(c.paid,0) paid, COALESCE(c.reserve,0) reserve,
       COALESCE(c.incurred,0) incurred, COALESCE(c.open_incurred,0) open_incurred,
       e.limit_exposure_usd exposure, e.sum_insured_usd sum_insured, e.peak_zone,
       COALESCE(c.incurred,0) / NULLIF(p.earned,0) AS loss_ratio,
       COALESCE(c.incurred,0) / NULLIF(t.limit_usd,0) AS limit_utilisation,
       CASE WHEN COALESCE(c.incurred,0)/NULLIF(t.limit_usd,0) >= (SELECT value FROM ref_assumptions WHERE key='watchlist_limit_utilisation') THEN 'Critical'
            WHEN COALESCE(c.incurred,0)/NULLIF(t.limit_usd,0) >= 0.50 THEN 'High'
            WHEN COALESCE(c.incurred,0)/NULLIF(t.limit_usd,0) >= 0.20 THEN 'Medium' ELSE 'Low' END AS risk_band
FROM dim_treaty t
JOIN dim_cedant ce ON ce.cedant_id = t.cedant_id
JOIN dim_lob l ON l.lob_id = t.lob_id
JOIN dim_region r ON r.region_id = t.region_id
JOIN dim_underwriter u ON u.underwriter_id = t.underwriter_id
LEFT JOIN p ON p.treaty_id = t.treaty_id
LEFT JOIN c ON c.treaty_id = t.treaty_id
LEFT JOIN fact_exposure e ON e.treaty_id = t.treaty_id;

CREATE OR REPLACE VIEW v_lob_summary AS
SELECT lob_name, COUNT(*) treaties, SUM(gwp) gwp, SUM(ceded) ceded, SUM(earned) earned, SUM(claim_count) claims,
       SUM(paid) paid, SUM(incurred) incurred, SUM(exposure) exposure,
       SUM(incurred)/NULLIF(SUM(earned),0) loss_ratio,
       SUM(earned_commission)/NULLIF(SUM(earned),0) commission_ratio,
       SUM(incurred)/NULLIF(SUM(earned),0) + SUM(earned_commission)/NULLIF(SUM(earned),0)
         + (SELECT value FROM ref_assumptions WHERE key='admin_expense_ratio') combined_ratio
FROM v_treaty_summary GROUP BY lob_name;

CREATE OR REPLACE VIEW v_region_summary AS
SELECT region_name, COUNT(*) treaties, SUM(gwp) gwp, SUM(ceded) ceded, SUM(earned) earned, SUM(claim_count) claims,
       SUM(paid) paid, SUM(incurred) incurred, SUM(exposure) exposure,
       SUM(incurred)/NULLIF(SUM(earned),0) loss_ratio,
       SUM(incurred)/NULLIF(SUM(earned),0) + SUM(earned_commission)/NULLIF(SUM(earned),0)
         + (SELECT value FROM ref_assumptions WHERE key='admin_expense_ratio') combined_ratio
FROM v_treaty_summary GROUP BY region_name;

CREATE OR REPLACE VIEW v_uwyear_summary AS
SELECT underwriting_year, COUNT(*) treaties, SUM(gwp) gwp, SUM(earned) earned, SUM(claim_count) claims,
       SUM(incurred) incurred, SUM(open_incurred) open_incurred,
       SUM(incurred)/NULLIF(SUM(earned),0) loss_ratio,
       SUM(incurred)/NULLIF(SUM(earned),0) + SUM(earned_commission)/NULLIF(SUM(earned),0)
         + (SELECT value FROM ref_assumptions WHERE key='admin_expense_ratio') combined_ratio
FROM v_treaty_summary GROUP BY underwriting_year;

CREATE OR REPLACE VIEW v_cedant_summary AS
SELECT cedant_code, cedant_name, cedant_country, rating, COUNT(*) treaties, SUM(gwp) gwp, SUM(earned) earned,
       SUM(incurred) incurred, SUM(exposure) exposure, SUM(incurred)/NULLIF(SUM(earned),0) loss_ratio
FROM v_treaty_summary GROUP BY cedant_code, cedant_name, cedant_country, rating;

CREATE OR REPLACE VIEW v_underwriter_summary AS
SELECT underwriter_name, COUNT(*) treaties, SUM(gwp) gwp, SUM(earned) earned, SUM(incurred) incurred,
       SUM(exposure) exposure, SUM(incurred)/NULLIF(SUM(earned),0) loss_ratio,
       SUM(CASE WHEN risk_band IN ('High','Critical') THEN 1 ELSE 0 END) high_risk_treaties
FROM v_treaty_summary GROUP BY underwriter_name;

CREATE OR REPLACE VIEW v_monthly_trend AS
WITH months AS (SELECT DISTINCT year_month ym FROM dim_date WHERE year_month BETWEEN '2021-01' AND '2026-09'),
     p AS (SELECT to_char(txn_date, 'YYYY-MM') ym, SUM(gross_written_premium) gwp, SUM(earned_premium) earned
           FROM fact_premium GROUP BY 1),
     c AS (SELECT to_char(loss_date, 'YYYY-MM') ym, COUNT(*) claims, SUM(incurred_amount) incurred FROM fact_claims GROUP BY 1)
SELECT m.ym year_month, COALESCE(p.gwp,0) gwp, COALESCE(p.earned,0) earned,
       COALESCE(c.claims,0) claims, COALESCE(c.incurred,0) incurred,
       COALESCE(p.gwp,0) / NULLIF(LAG(p.gwp) OVER (ORDER BY m.ym),0) - 1 gwp_mom_growth,
       AVG(COALESCE(c.incurred,0)) OVER (ORDER BY m.ym ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) incurred_rolling_3m
FROM months m LEFT JOIN p ON p.ym = m.ym LEFT JOIN c ON c.ym = m.ym ORDER BY m.ym;

CREATE OR REPLACE VIEW v_watchlist AS
SELECT * FROM v_treaty_summary
WHERE limit_utilisation >= (SELECT value FROM ref_assumptions WHERE key='watchlist_limit_utilisation');

CREATE OR REPLACE VIEW v_large_losses AS
SELECT c.claim_id, c.treaty_id, ts.cedant_name, ts.lob_name, ts.region_name, c.loss_date, c.claim_type, c.status,
       c.paid_amount, c.case_reserve, c.incurred_amount, c.exceeds_limit
FROM fact_claims c JOIN v_treaty_summary ts ON ts.treaty_id = c.treaty_id;

CREATE OR REPLACE VIEW v_loss_emergence AS
WITH x AS (
  SELECT t.underwriting_year uwy,
         CAST((c.loss_date - t.inception_date) / 91.3 AS INTEGER) * 3 + 3 AS months_since_inception,
         SUM(c.incurred_amount) incurred
  FROM fact_claims c JOIN dim_treaty t ON t.treaty_id = c.treaty_id GROUP BY 1, 2)
SELECT uwy, months_since_inception, incurred,
       SUM(incurred) OVER (PARTITION BY uwy ORDER BY months_since_inception) cumulative_incurred
FROM x;
