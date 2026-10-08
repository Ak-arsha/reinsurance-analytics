#!/usr/bin/env python3
"""Build the interactive, self-contained HTML dashboard from the warehouse (data cubes are injected as JSON)."""
import json, sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
Q = "substr({d},1,4)||'-Q'||((CAST(substr({d},6,2) AS INT)+2)/3)"
m = lambda s: round(float(s) / 1e6, 3)


def cubes(con):
    rd = lambda s: pd.read_sql(s, con)
    lobs = list(rd("SELECT lob_name FROM dim_lob ORDER BY lob_id").lob_name)
    regs = list(rd("SELECT region_name FROM dim_region ORDER BY region_id").region_name)
    li, ri = {n: i for i, n in enumerate(lobs)}, {n: i for i, n in enumerate(regs)}
    qs = sorted(rd(f"SELECT DISTINCT {Q.format(d='txn_date')} q FROM fact_premium").q)
    qi = {q: i for i, q in enumerate(qs)}
    base = "JOIN dim_treaty t ON t.treaty_id=f.treaty_id JOIN dim_lob l ON l.lob_id=t.lob_id JOIN dim_region r ON r.region_id=t.region_id"
    P = rd(f"""SELECT {Q.format(d='f.txn_date')} q, l.lob_name l, r.region_name r, SUM(gross_written_premium) a, SUM(earned_premium) b,
               SUM(ceded_premium) c, SUM(earned_commission) d FROM fact_premium f {base} GROUP BY 1,2,3""")
    C = rd(f"""SELECT {Q.format(d='f.loss_date')} q, l.lob_name l, r.region_name r, COUNT(*) n, SUM(incurred_amount) a, SUM(paid_amount) b
               FROM fact_claims f {base} GROUP BY 1,2,3""")
    types = sorted(rd("SELECT DISTINCT claim_type FROM fact_claims").claim_type); ti = {n: i for i, n in enumerate(types)}
    stats = ["Settled", "Open", "Reopened", "Unmapped"]
    T = rd(f"""SELECT l.lob_name l, r.region_name r, claim_type ct, status s, COUNT(*) n, SUM(incurred_amount) a
               FROM fact_claims f {base} GROUP BY 1,2,3,4""")
    bands = ["Low", "Medium", "High", "Critical"]
    R = rd("""SELECT lob_name l, region_name r, risk_band b, COUNT(*) n, SUM(exposure) e, SUM(gwp) g, SUM(earned) x, SUM(incurred) i
              FROM v_treaty_summary GROUP BY 1,2,3""")
    U = rd("SELECT underwriting_year y, lob_name l, region_name r, SUM(gwp) g, SUM(earned) x, SUM(incurred) i, SUM(earned_commission) c FROM v_treaty_summary GROUP BY 1,2,3")
    top = rd("SELECT claim_id, cedant_name, lob_name, region_name, loss_date, claim_type, status, incurred_amount FROM v_large_losses ORDER BY incurred_amount DESC LIMIT 60")
    wl = rd("SELECT treaty_id, cedant_name, lob_name, region_name, limit_usd, incurred, limit_utilisation FROM v_watchlist ORDER BY limit_utilisation DESC")
    ced = rd("SELECT cedant_name, cedant_country, treaties, gwp, loss_ratio, exposure FROM v_cedant_summary ORDER BY gwp DESC LIMIT 10")
    dq = rd("SELECT check_id, check_name, category, severity, records_tested, records_failed, status, action_taken FROM dq_check_log ORDER BY status DESC, check_id")
    health = rd("SELECT * FROM v_dq_health").iloc[0]
    d = dict(
        lobs=lobs, regs=regs, qs=qs, types=types, stats=stats, bands=bands,
        P=[[qi[r.q], li[r.l], ri[r.r], m(r.a), m(r.b), m(r.c), m(r.d)] for r in P.itertuples()],
        C=[[qi.get(r.q, -1), li[r.l], ri[r.r], int(r.n), m(r.a), m(r.b)] for r in C.itertuples() if r.q in qi],
        T=[[li[r.l], ri[r.r], ti[r.ct], stats.index(r.s), int(r.n), m(r.a)] for r in T.itertuples()],
        R=[[li[r.l], ri[r.r], bands.index(r.b), int(r.n), m(r.e), m(r.g), m(r.x), m(r.i)] for r in R.itertuples()],
        U=[[int(r.y), li[r.l], ri[r.r], m(r.g), m(r.x), m(r.i), m(r.c)] for r in U.itertuples()],
        top=[[r.claim_id, r.cedant_name, li[r.lob_name], ri[r.region_name], r.loss_date, r.claim_type, r.status, m(r.incurred_amount)] for r in top.itertuples()],
        wl=[[r.treaty_id, r.cedant_name, li[r.lob_name], ri[r.region_name], m(r.limit_usd), m(r.incurred), round(r.limit_utilisation, 3)] for r in wl.itertuples()],
        ced=[[r.cedant_name, r.cedant_country, int(r.treaties), m(r.gwp), round(r.loss_ratio, 3), m(r.exposure)] for r in ced.itertuples()],
        dq=[list(map(lambda v: v if not hasattr(v, "item") else v.item(), r)) for r in dq.itertuples(index=False)],
        health=dict(passed=int(health.checks_passed), total=int(health.checks_total), high=int(health.high_severity_fails), quar=int(health.quarantined_records)),
        insights=json.loads((ROOT / "data" / "insights.json").read_text())["insights"],
        admin=0.05, val="30 Sep 2026")
    return d


TEMPLATE = (ROOT / "python" / "dashboard_template.html").read_text() if (ROOT / "python" / "dashboard_template.html").exists() else ""


def main(root=ROOT):
    root = Path(root)
    con = sqlite3.connect(root / "data" / "reinsurance.db")
    html = (root / "python" / "dashboard_template.html").read_text().replace("/*DATA*/null", json.dumps(cubes(con), separators=(",", ":")))
    out = root / "dashboard" / "reinsurance_dashboard.html"
    out.write_text(html)
    print(f"Dashboard written: {out.name} ({out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
