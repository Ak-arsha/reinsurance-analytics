#!/usr/bin/env python3
"""Load source extracts -> staging -> data-quality checks -> mapping -> core star schema -> MI views."""
import re, sqlite3, sys
from datetime import datetime
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from dq_checks import CHECKS

ROOT = Path(__file__).resolve().parents[1]
TREND_THRESHOLD = 0.35          # month-on-month premium move that triggers the trend check
TREND_FROM = "2022-01"          # ignore the 2021 ramp-up of a new portfolio


def iso(s, fmt):
    return pd.to_datetime(s, format=fmt, errors="coerce").dt.strftime("%Y-%m-%d")


def stage(con, src):
    A = pd.read_csv(src / "sysA_treaties.csv", dtype=str, keep_default_na=False)
    B = pd.read_csv(src / "sysB_claims.csv", dtype=str, keep_default_na=False)
    C = pd.read_csv(src / "sysC_premium.csv", dtype=str, keep_default_na=False)
    X = pd.read_csv(src / "sysC_exposure.csv", dtype=str, keep_default_na=False)
    num = lambda s: pd.to_numeric(s, errors="coerce")
    stg_t = pd.DataFrame(dict(
        treaty_id=A.TreatyID, cedant_code=A.CedantCode, cedant_name=A.CedantName, cedant_country=A.CedantCountry,
        cedant_type=A.CedantType, cedant_rating=A.CedantRating, region_raw=A.Region, lob_code=A.LobCode,
        treaty_type=A.TreatyType, uw_year=num(A.UWYear), inception=iso(A.Inception, "%Y-%m-%d"),
        expiry=iso(A.Expiry, "%Y-%m-%d"), currency=A.Currency, share_pct=num(A.SharePct),
        limit_local=num(A.Limit), retention_local=num(A.Retention),
        est_annual_premium_local=num(A.EstAnnualPremium), underwriter=A.Underwriter))
    stg_c = pd.DataFrame(dict(
        claim_id=B.ClaimID, treaty_ref=B.TreatyRef, loss_date=iso(B.LossDate, "%d-%b-%Y"),
        report_date=iso(B.ReportDate, "%d-%b-%Y"), claim_type=B.ClaimType, currency=B.Currency,
        paid_local=num(B.Paid), reserve_local=num(B.Reserve), incurred_local=num(B.Incurred), status_code=B.Status))
    stg_p = pd.DataFrame(dict(
        txn_id=C.TxnID, treaty_ref=C.TreatyRef, txn_date=iso(C.TxnDate, "%d/%m/%Y"), currency=C.Currency,
        gross_local=num(C.Gross), ceded_local=num(C.Ceded), commission_local=num(C.Commission),
        earned_local=num(C.Earned)))
    stg_x = pd.DataFrame(dict(
        treaty_ref=X.TreatyRef, as_of_date=iso(X.AsOf, "%d/%m/%Y"), currency=X.Currency,
        sum_insured_local=num(X.SumInsured), limit_exposure_local=num(X.LimitExposure), peak_zone=X.PeakZone))
    for name, df in [("stg_treaties", stg_t), ("stg_claims", stg_c), ("stg_premium", stg_p), ("stg_exposure", stg_x)]:
        df.insert(0, "src_row", range(1, len(df) + 1))
        df.to_sql(name, con, index=False, if_exists="replace")


def load_mappings(con, mdir):
    for t in ["map_region", "map_lob", "map_claim_status", "map_currency"]:
        pd.read_csv(mdir / f"{t}.csv", dtype=str, keep_default_na=False).assign(
            **({"rate_to_usd": lambda d: pd.to_numeric(d.rate_to_usd)} if t == "map_currency" else {})
        ).to_sql(t, con, index=False, if_exists="append")
    refs = pd.concat([pd.read_sql("SELECT DISTINCT treaty_ref r FROM stg_premium", con),
                      pd.read_sql("SELECT DISTINCT treaty_ref r FROM stg_exposure", con)]).r.unique()
    rows = []
    for r in refs:
        m = re.fullmatch(r"TR-(\d{4})", str(r).strip())
        rows.append((r, f"T{m.group(1)}" if m else None, "TR-nnnn -> Tnnnn"))
    con.executemany("INSERT INTO map_treaty_id VALUES (?,?,?)", rows)


def run_checks(con, run_ts):
    log = []
    for cid, name, cat, sev, disp, tbl, fail_sql, test_sql in CHECKS:
        tested = con.execute(test_sql).fetchone()[0]
        rows = con.execute(fail_sql).fetchall()
        con.executemany("INSERT INTO dq_failed_records VALUES (?,?,?,?,?,?)",
                        [(cid, tbl, r[0], r[1], r[2], disp) for r in rows])
        log.append((run_ts, cid, name, cat, sev, tested, len(rows), "PASS" if not rows else "FAIL", disp if rows else "None required"))
    con.executemany("INSERT INTO dq_check_log VALUES (?,?,?,?,?,?,?,?,?)", log)


def trend_check(con, run_ts):
    df = pd.read_sql("""SELECT substr(txn_date,1,7) ym, SUM(gross_usd) g FROM v_stg_premium_usd
                        WHERE gross_usd IS NOT NULL GROUP BY 1 ORDER BY 1""", con)
    df["mom"] = df.g.pct_change()
    bad = df[(df.ym >= TREND_FROM) & (df.mom.abs() > TREND_THRESHOLD)]
    tested = int((df.ym >= TREND_FROM).sum())
    con.executemany("INSERT INTO dq_failed_records VALUES (?,?,?,?,?,?)",
                    [("T01", "stg_premium", None, r.ym, f"MoM {r.mom:+.0%}", "Flagged") for r in bad.itertuples()])
    con.execute("INSERT INTO dq_check_log VALUES (?,?,?,?,?,?,?,?,?)",
                (run_ts, "T01", f"Monthly gross premium moves >{TREND_THRESHOLD:.0%} vs prior month", "Trend", "Medium",
                 tested, len(bad), "PASS" if bad.empty else "FAIL", "None required" if bad.empty else "Flagged - investigate"))


def reconcile(con, run_ts):
    q = lambda s: con.execute(s).fetchone()[0] or 0.0
    src_p = q("SELECT SUM(gross_usd) FROM v_stg_premium_usd WHERE treaty_id IS NOT NULL OR 1")
    quar_p = q("""SELECT SUM(gross_usd) FROM v_stg_premium_usd WHERE src_row IN
                  (SELECT src_row FROM dq_failed_records WHERE source_table='stg_premium' AND disposition='Quarantined')""")
    core_p = q("SELECT SUM(gross_written_premium) FROM fact_premium")
    src_c = q("SELECT SUM((c.paid_local+c.reserve_local)*fx.rate_to_usd) FROM stg_claims c JOIN map_currency fx ON UPPER(fx.source_value)=UPPER(c.currency)")
    quar_c = q("""SELECT SUM((c.paid_local+c.reserve_local)*fx.rate_to_usd) FROM stg_claims c JOIN map_currency fx ON UPPER(fx.source_value)=UPPER(c.currency)
                  WHERE c.src_row IN (SELECT src_row FROM dq_failed_records WHERE source_table='stg_claims' AND disposition='Quarantined')""")
    core_c = q("SELECT SUM(paid_amount+case_reserve) FROM fact_claims")
    for cid, nm, diff in [("Z01", "Premium: source = core + quarantined (USD)", src_p - quar_p - core_p),
                          ("Z02", "Paid + reserve: source = core + quarantined (USD)", src_c - quar_c - core_c)]:
        ok = abs(diff) < 1.0
        con.execute("INSERT INTO dq_check_log VALUES (?,?,?,?,?,?,?,?,?)",
                    (run_ts, cid, nm, "Reconciliation", "High", 1, 0 if ok else 1, "PASS" if ok else "FAIL",
                     "None required" if ok else f"Investigate difference of {diff:,.2f}"))


def make_dim_date(con):
    d = pd.date_range("2021-01-01", "2027-12-31")
    pd.DataFrame(dict(date_key=d.strftime("%Y-%m-%d"), year=d.year, quarter=d.quarter, month=d.month,
                      year_month=d.strftime("%Y-%m"), year_quarter=[f"{y}-Q{q}" for y, q in zip(d.year, d.quarter)])
                 ).to_sql("dim_date", con, index=False, if_exists="append")


def run_pipeline(root=ROOT, quiet=False):
    root = Path(root)
    db = root / "data" / "reinsurance.db"
    db.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = lambda f: con.executescript((root / "sql" / f).read_text())
    sql("01_schema.sql")
    stage(con, root / "data" / "source")
    load_mappings(con, root / "mappings")
    sql("02_staging_views.sql")
    run_checks(con, run_ts); trend_check(con, run_ts)
    sql("03_core_load.sql"); make_dim_date(con)
    reconcile(con, run_ts)
    sql("04_mi_views.sql")
    con.commit()
    log = pd.read_sql("SELECT check_id, check_name, records_tested t, records_failed f, status, action_taken FROM dq_check_log ORDER BY check_id", con)
    if not quiet:
        print(log.to_string(index=False))
        n = lambda t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"\nCore loaded: treaties={n('dim_treaty')} premium={n('fact_premium')} claims={n('fact_claims')} exposure={n('fact_exposure')}")
        print(f"Checks passed: {(log.status=='PASS').sum()}/{len(log)}")
    con.close()
    return db


if __name__ == "__main__":
    run_pipeline()
