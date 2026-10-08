-- 05_analysis_queries.sql : the analytical SQL layer (portfolio questions + data-engineering questions).
-- Each block starts with "-- @Qn title" so python/run_queries.py can execute and document them.
-- Dialect: SQLite. PostgreSQL differences: substr(d,1,7) -> to_char(d::date,'YYYY-MM'); julianday() -> date subtraction.

-- @Q1 Total premium (gross written, ceded, net, earned) in USD millions
SELECT ROUND(SUM(gross_written_premium)/1e6,1) gwp_m, ROUND(SUM(ceded_premium)/1e6,1) ceded_m,
       ROUND((SUM(gross_written_premium)-SUM(ceded_premium))/1e6,1) net_m, ROUND(SUM(earned_premium)/1e6,1) earned_m
FROM fact_premium;

-- @Q2 Total claims: paid, case reserve, incurred
SELECT COUNT(*) claim_count, ROUND(SUM(paid_amount)/1e6,1) paid_m, ROUND(SUM(case_reserve)/1e6,1) reserve_m,
       ROUND(SUM(incurred_amount)/1e6,1) incurred_m FROM fact_claims;

-- @Q3 Loss ratio and combined ratio, by underwriting year (incurred / earned premium)
SELECT underwriting_year, ROUND(earned/1e6,1) earned_m, ROUND(incurred/1e6,1) incurred_m,
       ROUND(100*loss_ratio,1) loss_ratio_pct, ROUND(100*combined_ratio,1) combined_ratio_pct,
       ROUND(100.0*open_incurred/NULLIF(incurred,0),0) open_share_pct
FROM v_uwyear_summary ORDER BY underwriting_year;

-- @Q4 Which business line has the highest claims? (incurred, with share of total using a window function)
SELECT lob_name, ROUND(incurred/1e6,1) incurred_m,
       ROUND(100.0*incurred/SUM(incurred) OVER (),1) share_of_incurred_pct,
       RANK() OVER (ORDER BY incurred DESC) rnk
FROM v_lob_summary ORDER BY rnk;

-- @Q5 Which region generates the highest premium? (share and loss ratio vs portfolio, CTE + subquery)
WITH tot AS (SELECT SUM(gwp) gwp, SUM(incurred)/SUM(earned) lr FROM v_region_summary)
SELECT r.region_name, ROUND(r.gwp/1e6,1) gwp_m, ROUND(100*r.gwp/tot.gwp,1) share_pct,
       ROUND(100*r.loss_ratio,1) loss_ratio_pct, ROUND(100*(r.loss_ratio-tot.lr),1) pts_vs_portfolio
FROM v_region_summary r, tot ORDER BY r.gwp DESC;

-- @Q6 Which treaties have the highest claims? (top 10 by incurred)
SELECT treaty_id, cedant_name, lob_name, region_name, claim_count, ROUND(incurred/1e6,2) incurred_m,
       ROUND(100*loss_ratio,0) loss_ratio_pct
FROM v_treaty_summary ORDER BY incurred DESC LIMIT 10;

-- @Q7 Which cedants have the highest exposure? (HAVING removes tiny cedants)
SELECT cedant_name, cedant_country, treaties, ROUND(exposure/1e6,0) exposure_m, ROUND(100*loss_ratio,1) loss_ratio_pct
FROM v_cedant_summary GROUP BY cedant_code HAVING SUM(treaties) >= 5 ORDER BY exposure DESC LIMIT 10;

-- @Q8 Top 10 loss-making treaties (incurred above earned premium, size of underwriting loss)
SELECT treaty_id, cedant_name, lob_name, underwriting_year, ROUND(earned/1e6,2) earned_m, ROUND(incurred/1e6,2) incurred_m,
       ROUND((incurred-earned)/1e6,2) underwriting_loss_m
FROM v_treaty_summary WHERE incurred > earned ORDER BY incurred - earned DESC LIMIT 10;

-- @Q9 Monthly premium growth: month-on-month and year-on-year (LAG window functions), last 12 months
SELECT year_month, ROUND(gwp/1e6,2) gwp_m, ROUND(100*gwp_mom_growth,1) mom_pct,
       ROUND(100*(gwp/NULLIF(LAG(gwp,12) OVER (ORDER BY year_month),0)-1),1) yoy_pct
FROM v_monthly_trend ORDER BY year_month DESC LIMIT 12;

-- @Q10 Which underwriters manage the highest-risk portfolios? (CASE risk score + ranking)
SELECT underwriter_name, treaties, ROUND(exposure/1e6,0) exposure_m, ROUND(100*loss_ratio,1) loss_ratio_pct, high_risk_treaties,
       CASE WHEN loss_ratio > 0.80 THEN 'Review' WHEN loss_ratio > 0.70 THEN 'Watch' ELSE 'On track' END status,
       RANK() OVER (ORDER BY loss_ratio DESC) loss_ratio_rank
FROM v_underwriter_summary WHERE underwriter_name <> 'Unassigned' ORDER BY loss_ratio_rank;

-- @Q11 Treaties near their limit (watchlist): incurred >= 80% of limit
SELECT treaty_id, cedant_name, lob_name, ROUND(limit_usd/1e6,1) limit_m, ROUND(incurred/1e6,1) incurred_m,
       ROUND(100*limit_utilisation,0) utilisation_pct
FROM v_watchlist ORDER BY limit_utilisation DESC;

-- @Q12 Loss emergence: cumulative incurred as % of final, by months since inception (underwriting years 2022-2024)
SELECT uwy, months_since_inception, ROUND(cumulative_incurred/1e6,1) cum_incurred_m,
       ROUND(100*cumulative_incurred/MAX(cumulative_incurred) OVER (PARTITION BY uwy),0) pct_of_to_date
FROM v_loss_emergence WHERE uwy BETWEEN 2022 AND 2024 AND months_since_inception <= 18 ORDER BY uwy, months_since_inception;

-- @Q13 Data engineering: records quarantined by source table and reason (check)
SELECT f.source_table, f.check_id, l.check_name, COUNT(*) records
FROM dq_failed_records f JOIN dq_check_log l USING (check_id)
WHERE f.disposition = 'Quarantined' GROUP BY 1,2,3 ORDER BY records DESC;

-- @Q14 Data engineering: unmapped values waiting for a mapping decision
SELECT * FROM v_unmapped_values ORDER BY records DESC;

-- @Q15 Claim frequency and severity by line of business, with claim size bands (CASE bucketing + join)
SELECT v.lob_name,
       SUM(CASE WHEN v.incurred_amount < 250000 THEN 1 ELSE 0 END) small_lt_250k,
       SUM(CASE WHEN v.incurred_amount BETWEEN 250000 AND 1000000 THEN 1 ELSE 0 END) mid_250k_1m,
       SUM(CASE WHEN v.incurred_amount > 1000000 THEN 1 ELSE 0 END) large_gt_1m,
       ROUND(1.0*COUNT(*)/s.treaties,2) claims_per_treaty,
       ROUND(AVG(v.incurred_amount)/1e3,0) avg_severity_k
FROM v_large_losses v JOIN v_lob_summary s ON s.lob_name = v.lob_name
GROUP BY v.lob_name, s.treaties ORDER BY avg_severity_k DESC;
