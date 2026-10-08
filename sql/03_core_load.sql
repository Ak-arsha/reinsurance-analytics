-- 03_core_load.sql : build the clean star schema from validated staging data.
-- Rules (documented in docs/DQ_and_Mapping_Procedure.md):
--   * records with disposition 'Quarantined' in dq_failed_records are NOT loaded
--   * unmapped / blank dimension values load as 'Unmapped' / 'Unassigned' and are flagged
--   * incurred is always recomputed as paid + case reserve

INSERT INTO dim_region(region_name) SELECT DISTINCT mapped_value FROM map_region ORDER BY 1;
INSERT INTO dim_region(region_name) VALUES ('Unassigned');
INSERT INTO dim_lob(lob_name) SELECT DISTINCT mapped_value FROM map_lob ORDER BY 1;
INSERT INTO dim_lob(lob_name) VALUES ('Unmapped');
INSERT INTO dim_underwriter(underwriter_name)
  SELECT DISTINCT TRIM(underwriter) FROM v_stg_treaties_uniq WHERE TRIM(COALESCE(underwriter,'')) <> '' ORDER BY 1;
INSERT INTO dim_underwriter(underwriter_name) VALUES ('Unassigned');

INSERT INTO dim_cedant(cedant_code, cedant_name, country, cedant_type, rating)
SELECT cedant_code, cedant_name, cedant_country, cedant_type, cedant_rating
FROM v_stg_treaties_uniq WHERE src_row IN (SELECT MIN(src_row) FROM v_stg_treaties_uniq GROUP BY cedant_code);

INSERT INTO dim_treaty
SELECT t.treaty_id, ce.cedant_id,
       COALESCE(dl.lob_id, (SELECT lob_id FROM dim_lob WHERE lob_name = 'Unmapped')),
       COALESCE(dr.region_id, (SELECT region_id FROM dim_region WHERE region_name = 'Unassigned')),
       COALESCE(du.underwriter_id, (SELECT underwriter_id FROM dim_underwriter WHERE underwriter_name = 'Unassigned')),
       t.treaty_type, t.uw_year, t.inception, t.expiry, t.currency, t.share_pct,
       t.limit_local * fx.rate_to_usd, t.retention_local * fx.rate_to_usd,
       t.est_annual_premium_local * fx.rate_to_usd,
       CASE WHEN dl.lob_id IS NULL THEN 'unmapped_lob'
            WHEN dr.region_id IS NULL THEN 'unassigned_region'
            WHEN du.underwriter_id IS NULL THEN 'unassigned_underwriter' END
FROM v_stg_treaties_uniq t
JOIN dim_cedant ce ON ce.cedant_code = t.cedant_code
JOIN map_currency fx ON UPPER(TRIM(fx.source_value)) = UPPER(TRIM(t.currency))
LEFT JOIN map_lob ml ON UPPER(TRIM(ml.source_value)) = UPPER(TRIM(t.lob_code))
LEFT JOIN dim_lob dl ON dl.lob_name = ml.mapped_value
LEFT JOIN map_region mr ON UPPER(TRIM(mr.source_value)) = UPPER(TRIM(t.region_raw))
LEFT JOIN dim_region dr ON dr.region_name = mr.mapped_value
LEFT JOIN dim_underwriter du ON du.underwriter_name = TRIM(t.underwriter)
WHERE t.src_row NOT IN (SELECT src_row FROM dq_failed_records WHERE source_table='stg_treaties' AND disposition='Quarantined');

INSERT INTO fact_premium
SELECT p.txn_id, p.treaty_id, p.txn_date, p.currency,
       p.gross_local * fx.rate_to_usd, p.ceded_local * fx.rate_to_usd, p.commission_local * fx.rate_to_usd,
       p.earned_local * fx.rate_to_usd,
       CASE WHEN p.gross_local <> 0 THEN p.commission_local * p.earned_local / p.gross_local * fx.rate_to_usd END
FROM v_stg_premium_usd p
JOIN dim_treaty t ON t.treaty_id = p.treaty_id
JOIN map_currency fx ON UPPER(TRIM(fx.source_value)) = UPPER(TRIM(p.currency))
WHERE p.src_row NOT IN (SELECT src_row FROM dq_failed_records WHERE source_table='stg_premium' AND disposition='Quarantined');

INSERT INTO fact_claims
SELECT c.claim_id, c.treaty_ref, c.loss_date, c.report_date, c.claim_type,
       c.paid_local * fx.rate_to_usd, c.reserve_local * fx.rate_to_usd,
       (c.paid_local + c.reserve_local) * fx.rate_to_usd,                      -- incurred = paid + reserve
       COALESCE(ms.mapped_value, 'Unmapped'),
       CASE WHEN (c.paid_local + c.reserve_local) * fx.rate_to_usd > t.limit_usd THEN 1 ELSE 0 END,
       CASE WHEN ms.mapped_value IS NULL THEN 'unmapped_status' END
FROM stg_claims c
JOIN dim_treaty t ON t.treaty_id = c.treaty_ref
JOIN map_currency fx ON UPPER(TRIM(fx.source_value)) = UPPER(TRIM(c.currency))
LEFT JOIN map_claim_status ms ON UPPER(TRIM(ms.source_value)) = UPPER(TRIM(c.status_code))
WHERE c.src_row NOT IN (SELECT src_row FROM dq_failed_records WHERE source_table='stg_claims' AND disposition='Quarantined');

INSERT INTO fact_exposure
SELECT mt.treaty_id, x.as_of_date, x.sum_insured_local * fx.rate_to_usd, x.limit_exposure_local * fx.rate_to_usd, x.peak_zone
FROM stg_exposure x
JOIN map_treaty_id mt ON mt.source_ref = x.treaty_ref
JOIN dim_treaty t ON t.treaty_id = mt.treaty_id
JOIN map_currency fx ON UPPER(TRIM(fx.source_value)) = UPPER(TRIM(x.currency))
WHERE x.src_row IN (SELECT MIN(src_row) FROM stg_exposure GROUP BY treaty_ref);
