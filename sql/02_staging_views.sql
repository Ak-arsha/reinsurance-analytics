-- 02_staging_views.sql : helper views over the raw staging tables.
-- First occurrence wins when a treaty arrives twice from System A.
CREATE VIEW v_stg_treaties_uniq AS
SELECT * FROM stg_treaties
WHERE src_row IN (SELECT MIN(src_row) FROM stg_treaties GROUP BY treaty_id);

-- Premium rows with the System C reference translated to a canonical treaty_id and FX applied.
CREATE VIEW v_stg_premium_usd AS
SELECT p.*, mt.treaty_id AS treaty_id, p.gross_local * fx.rate_to_usd AS gross_usd
FROM stg_premium p
LEFT JOIN map_treaty_id mt ON mt.source_ref = p.treaty_ref
LEFT JOIN map_currency fx ON UPPER(TRIM(fx.source_value)) = UPPER(TRIM(p.currency));
