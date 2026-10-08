#!/usr/bin/env python3
"""Generate the 'Executive Insights' text directly from the MI views (no hand-typed numbers)."""
import json, sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def build(root=ROOT):
    con = sqlite3.connect(Path(root) / "data" / "reinsurance.db")
    q = lambda s: pd.read_sql(s, con)
    tot = q("SELECT SUM(gwp) gwp, SUM(earned) earned, SUM(incurred) inc, SUM(open_incurred) openinc FROM v_treaty_summary").iloc[0]
    plr = tot.inc / tot.earned
    out = []
    reg = q("SELECT * FROM v_region_summary WHERE region_name <> 'Unassigned'")
    reg["share"] = reg.gwp / tot.gwp; reg["gap"] = (reg.loss_ratio - plr) * 100
    r = reg.sort_values("gap", key=abs, ascending=False).iloc[0]
    big = reg.sort_values("gwp", ascending=False).iloc[0]
    out.append(f"{big.region_name} is the largest region at {big.share:.0%} of gross written premium, with a loss ratio of "
               f"{big.loss_ratio:.1%} ({big.gap:+.1f} pts vs the portfolio's {plr:.1%}).")
    if r.region_name != big.region_name:
        out.append(f"{r.region_name} deviates most from the portfolio loss ratio: {r.loss_ratio:.1%} ({r.gap:+.1f} pts) on {r.share:.0%} of premium.")
    lob = q("SELECT * FROM v_lob_summary WHERE lob_name <> 'Unmapped' ORDER BY combined_ratio DESC")
    w = lob.iloc[0]
    out.append(f"{w.lob_name} has the weakest result: combined ratio {w.combined_ratio:.1%}, loss ratio {w.loss_ratio:.1%}. "
               f"{lob.iloc[-1].lob_name} is strongest at {lob.iloc[-1].combined_ratio:.1%}.")
    hot = q("""SELECT region_name, lob_name, SUM(gwp) gwp, SUM(incurred)/SUM(earned) lr FROM v_treaty_summary
               GROUP BY 1,2 HAVING SUM(gwp) > 50e6 ORDER BY lr DESC LIMIT 1""").iloc[0]
    out.append(f"Hotspot: {hot.region_name} {hot.lob_name} (${hot.gwp/1e6:,.0f}M premium) runs a loss ratio of {hot.lr:.1%}.")
    wl = q("SELECT COUNT(*) n, SUM(limit_usd) lim FROM v_watchlist").iloc[0]
    out.append(f"{int(wl.n)} treaties have incurred losses at or above 80% of limit and should be reviewed for capacity "
               f"(${wl.lim/1e6:,.0f}M of combined limit).")
    uwy = q("SELECT * FROM v_uwyear_summary ORDER BY underwriting_year")
    worst = uwy[uwy.underwriting_year < 2026].sort_values("loss_ratio", ascending=False).iloc[0]
    out.append(f"Underwriting year {int(worst.underwriting_year)} is the weakest underwriting year (excluding the part-year 2026) at a {worst.loss_ratio:.1%} loss ratio "
               f"with {worst.open_incurred/worst.incurred:.0%} of incurred still open.")
    cy = q("SELECT substr(year_month,1,4) y, SUM(gwp) gwp FROM v_monthly_trend GROUP BY 1").set_index("y").gwp
    out.append(f"Calendar-year gross written premium grew {cy['2025']/cy['2024']-1:+.1%} in 2025 versus 2024.")
    ced = q("SELECT SUM(gwp) g FROM (SELECT gwp FROM v_cedant_summary ORDER BY gwp DESC LIMIT 5)").g[0]
    out.append(f"The five largest cedants write {ced/tot.gwp:.0%} of premium (concentration to monitor).")
    dq = q("SELECT * FROM v_dq_health").iloc[0]
    out.append(f"Data confidence: {int(dq.checks_passed)} of {int(dq.checks_total)} data checks passed; {int(dq.quarantined_records)} source records "
               f"were quarantined and are excluded. {tot.openinc/tot.inc:.0%} of incurred is on open claims, so recent underwriting years are provisional.")
    res = dict(insights=out, portfolio_loss_ratio=plr)
    (Path(root) / "data" / "insights.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    for i in build()["insights"]: print("-", i)
