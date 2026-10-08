"""Data-quality check catalogue.

Each check = (id, name, category, severity, disposition, failing-rows SQL, tested-rows SQL).
Failing-rows SQL must return: src_row, record_key, detail.   Disposition says what the
pipeline does with failing rows:  Quarantined | Corrected | Loaded as Unmapped | Mapped to Unassigned | Flagged
"""
UNIQ = "v_stg_treaties_uniq"
T_ALL, C_ALL, P_ALL = ("SELECT COUNT(*) FROM stg_treaties", "SELECT COUNT(*) FROM stg_claims",
                       "SELECT COUNT(*) FROM stg_premium")

CHECKS = [
 # ---------------- Completeness ----------------
 ("C01", "Treaty has blank region", "Completeness", "Medium", "Mapped to Unassigned", "stg_treaties",
  "SELECT src_row, treaty_id, 'blank region' FROM stg_treaties WHERE TRIM(COALESCE(region_raw,''))=''", T_ALL),
 ("C02", "Treaty has blank underwriter", "Completeness", "Low", "Mapped to Unassigned", "stg_treaties",
  "SELECT src_row, treaty_id, 'blank underwriter' FROM stg_treaties WHERE TRIM(COALESCE(underwriter,''))=''", T_ALL),
 ("C03", "Treaty has blank currency", "Completeness", "High", "Quarantined", "stg_treaties",
  "SELECT src_row, treaty_id, 'blank currency' FROM stg_treaties WHERE TRIM(COALESCE(currency,''))=''", T_ALL),
 ("C04", "Premium transaction has null gross premium", "Completeness", "High", "Quarantined", "stg_premium",
  "SELECT src_row, txn_id, 'null gross' FROM stg_premium WHERE gross_local IS NULL", P_ALL),
 # ---------------- Validity ----------------
 ("V01", "Claim loss date before treaty inception", "Validity", "High", "Quarantined", "stg_claims",
  f"SELECT c.src_row, c.claim_id, 'loss '||c.loss_date||' < inception '||t.inception FROM stg_claims c JOIN {UNIQ} t ON t.treaty_id=c.treaty_ref WHERE c.loss_date < t.inception", C_ALL),
 ("V02", "Claim loss date after treaty expiry", "Validity", "High", "Quarantined", "stg_claims",
  f"SELECT c.src_row, c.claim_id, 'loss '||c.loss_date||' > expiry '||t.expiry FROM stg_claims c JOIN {UNIQ} t ON t.treaty_id=c.treaty_ref WHERE c.loss_date > t.expiry", C_ALL),
 ("V03", "Premium transaction zero or negative", "Validity", "High", "Quarantined", "stg_premium",
  "SELECT src_row, txn_id, 'gross='||gross_local FROM stg_premium WHERE gross_local <= 0", P_ALL),
 ("V04", "Claim status code not in mapping", "Validity", "Medium", "Loaded as Unmapped", "stg_claims",
  "SELECT c.src_row, c.claim_id, 'status '||c.status_code FROM stg_claims c LEFT JOIN map_claim_status m ON UPPER(TRIM(m.source_value))=UPPER(TRIM(c.status_code)) WHERE m.source_value IS NULL", C_ALL),
 ("V05", "Line-of-business code not in mapping", "Validity", "Medium", "Loaded as Unmapped", "stg_treaties",
  "SELECT t.src_row, t.treaty_id, 'LOB '||t.lob_code FROM stg_treaties t LEFT JOIN map_lob m ON UPPER(TRIM(m.source_value))=UPPER(TRIM(t.lob_code)) WHERE m.source_value IS NULL", T_ALL),
 ("V06", "Currency not in mapping (no FX rate)", "Validity", "High", "Quarantined", "stg_treaties",
  "SELECT t.src_row, t.treaty_id, 'ccy '||t.currency FROM stg_treaties t LEFT JOIN map_currency m ON UPPER(TRIM(m.source_value))=UPPER(TRIM(t.currency)) WHERE m.source_value IS NULL AND TRIM(COALESCE(t.currency,''))<>''", T_ALL),
 ("V07", "Non-blank region not in mapping", "Validity", "Medium", "Mapped to Unassigned", "stg_treaties",
  "SELECT t.src_row, t.treaty_id, 'region '||t.region_raw FROM stg_treaties t LEFT JOIN map_region m ON UPPER(TRIM(m.source_value))=UPPER(TRIM(t.region_raw)) WHERE m.source_value IS NULL AND TRIM(COALESCE(t.region_raw,''))<>''", T_ALL),
 ("V08", "Negative claim amount", "Validity", "High", "Quarantined", "stg_claims",
  "SELECT src_row, claim_id, 'negative amount' FROM stg_claims WHERE paid_local < 0 OR reserve_local < 0 OR incurred_local < 0", C_ALL),
 ("V09", "Treaty expiry on/before inception", "Validity", "High", "Quarantined", "stg_treaties",
  "SELECT src_row, treaty_id, 'expiry<=inception' FROM stg_treaties WHERE expiry <= inception", T_ALL),
 ("V10", "Claim incurred exceeds treaty limit", "Validity", "Medium", "Flagged", "stg_claims",
  f"SELECT c.src_row, c.claim_id, 'incurred '||ROUND(c.incurred_local)||' > limit '||ROUND(t.limit_local) FROM stg_claims c JOIN {UNIQ} t ON t.treaty_id=c.treaty_ref WHERE c.incurred_local > t.limit_local", C_ALL),
 # ---------------- Consistency ----------------
 ("K01", "Incurred does not equal paid + case reserve", "Consistency", "Medium", "Corrected", "stg_claims",
  "SELECT src_row, claim_id, 'incurred '||ROUND(incurred_local,2)||' vs paid+reserve '||ROUND(paid_local+reserve_local,2) FROM stg_claims WHERE ABS(incurred_local-(paid_local+reserve_local))>0.01", C_ALL),
 ("K02", "System C premium differs from System A annual estimate (>2%)", "Consistency", "Medium", "Flagged", "stg_treaties",
  f"""SELECT t.src_row, t.treaty_id, 'booked '||ROUND(x.tot)||' vs est '||ROUND(t.est_annual_premium_local)
      FROM {UNIQ} t JOIN (SELECT mt.treaty_id tid, COUNT(*) n, SUM(g) tot FROM (SELECT treaty_ref, txn_date, MAX(gross_local) g FROM stg_premium WHERE gross_local>0 GROUP BY 1,2) d
                          JOIN map_treaty_id mt ON mt.source_ref=d.treaty_ref GROUP BY mt.treaty_id) x ON x.tid=t.treaty_id
      WHERE x.n=12 AND t.est_annual_premium_local>0 AND ABS(x.tot-t.est_annual_premium_local)/t.est_annual_premium_local>0.02""",
  f"SELECT COUNT(*) FROM (SELECT mt.treaty_id FROM (SELECT treaty_ref, txn_date FROM stg_premium WHERE gross_local>0 GROUP BY 1,2) d JOIN map_treaty_id mt ON mt.source_ref=d.treaty_ref GROUP BY mt.treaty_id HAVING COUNT(*)=12)"),
 ("K03", "Earned premium exceeds gross premium", "Consistency", "Medium", "Flagged", "stg_premium",
  "SELECT src_row, txn_id, 'earned>gross' FROM stg_premium WHERE gross_local>0 AND earned_local > gross_local*1.0001", P_ALL),
 ("K04", "Ceded premium exceeds gross premium", "Consistency", "Medium", "Flagged", "stg_premium",
  "SELECT src_row, txn_id, 'ceded>gross' FROM stg_premium WHERE gross_local>0 AND ceded_local > gross_local", P_ALL),
 # ---------------- Uniqueness ----------------
 ("U01", "Duplicate treaty ID in System A", "Uniqueness", "High", "Quarantined", "stg_treaties",
  "SELECT src_row, treaty_id, 'duplicate row' FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY treaty_id ORDER BY src_row) rn FROM stg_treaties) WHERE rn>1", T_ALL),
 ("U02", "Duplicate claim ID in System B", "Uniqueness", "High", "Quarantined", "stg_claims",
  "SELECT src_row, claim_id, 'duplicate row' FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY claim_id ORDER BY src_row) rn FROM stg_claims) WHERE rn>1", C_ALL),
 ("U03", "Duplicate premium transaction (same treaty, date, amount)", "Uniqueness", "High", "Quarantined", "stg_premium",
  "SELECT src_row, txn_id, 'duplicate of earlier txn' FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY treaty_ref, txn_date, gross_local ORDER BY src_row) rn FROM stg_premium) WHERE rn>1", P_ALL),
 # ---------------- Referential integrity ----------------
 ("R01", "Claim references a treaty that does not exist", "Referential integrity", "High", "Quarantined", "stg_claims",
  f"SELECT c.src_row, c.claim_id, 'treaty '||c.treaty_ref||' not found' FROM stg_claims c LEFT JOIN {UNIQ} t ON t.treaty_id=c.treaty_ref WHERE t.treaty_id IS NULL", C_ALL),
 ("R02", "Premium transaction references an unknown treaty", "Referential integrity", "High", "Quarantined", "stg_premium",
  f"SELECT p.src_row, p.txn_id, 'treaty ref '||p.treaty_ref||' not found' FROM stg_premium p LEFT JOIN map_treaty_id mt ON mt.source_ref=p.treaty_ref LEFT JOIN {UNIQ} t ON t.treaty_id=mt.treaty_id WHERE t.treaty_id IS NULL", P_ALL),
 ("R03", "Exposure record references an unknown treaty", "Referential integrity", "Medium", "Quarantined", "stg_exposure",
  f"SELECT x.src_row, x.treaty_ref, 'no matching treaty' FROM stg_exposure x LEFT JOIN map_treaty_id mt ON mt.source_ref=x.treaty_ref LEFT JOIN {UNIQ} t ON t.treaty_id=mt.treaty_id WHERE t.treaty_id IS NULL",
  "SELECT COUNT(*) FROM stg_exposure"),
 ("R04", "Treaty incepted but has no premium booked", "Referential integrity", "Low", "Flagged", "stg_treaties",
  f"SELECT t.src_row, t.treaty_id, 'no premium' FROM {UNIQ} t WHERE t.inception <= '2026-09-30' AND t.treaty_id NOT IN (SELECT mt.treaty_id FROM stg_premium p JOIN map_treaty_id mt ON mt.source_ref=p.treaty_ref)", T_ALL),
]
