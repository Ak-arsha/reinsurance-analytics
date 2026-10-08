#!/usr/bin/env python3
"""Generate three deliberately messy source-system extracts (System A/B/C).

System A  Policy admin   -> sysA_treaties.csv   (ISO dates, free-text regions)
System B  Claims         -> sysB_claims.csv     (dd-Mon-yyyy dates, 1-letter status codes)
System C  Finance        -> sysC_premium.csv, sysC_exposure.csv (dd/mm/yyyy, 'TR-0001' IDs)

A realistic set of data errors is planted and recorded in data/answer_key.json so
the data-quality checks can be proven to catch them.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
VAL_DATE = pd.Timestamp("2026-09-30")          # valuation / data cut-off date
ROOT = Path(__file__).resolve().parents[1]

FX = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27, "INR": 0.012}
REGIONS = {
    "North America": (0.32, ["USA", "Canada", "Mexico"], ["North America", "N. America", "NA", "NORTH AMERICA"]),
    "Europe": (0.28, ["UK", "Germany", "France", "Italy", "Switzerland", "Spain"], ["Europe", "EU", "EMEA-Europe"]),
    "Asia Pacific": (0.22, ["India", "Japan", "Singapore", "Australia", "China"], ["Asia Pacific", "APAC", "Asia-Pacific"]),
    "Latin America": (0.08, ["Brazil", "Chile", "Colombia"], ["Latin America", "LATAM", "Latin Am."]),
    "Middle East & Africa": (0.10, ["UAE", "South Africa", "Saudi Arabia"], ["Middle East & Africa", "MEA", "ME&A"]),
}
CCY = {"UK": "GBP", "Germany": "EUR", "France": "EUR", "Italy": "EUR", "Spain": "EUR",
       "Switzerland": "EUR", "India": "INR"}
LOBS = {  # code: (name, weight, base loss ratio, claim types)
    "PROP": ("Property", .32, .62, ["Natural Catastrophe", "Fire & Explosion", "Business Interruption"]),
    "CAS": ("Casualty", .22, .68, ["General Liability", "Auto Liability", "Workers Compensation"]),
    "SPEC": ("Specialty", .16, .58, ["Marine Hull", "Aviation", "Political Risk", "Energy"]),
    "PROF": ("Professional", .15, .60, ["Professional Indemnity", "Medical Malpractice"]),
    "FINL": ("Financial Lines", .15, .55, ["Directors & Officers", "Credit & Surety", "Cyber"]),
}
UNDERWRITERS = ["Aarav Mehta", "Sophie Laurent", "James Whitfield", "Priya Nair",
                "Carlos Ibarra", "Hannah Weber", "Kenji Sato", "Omar Haddad"]
ZONES = ["US Gulf Coast", "Florida", "California", "Japan", "Europe Windstorm", "Australia", "Other"]


def pick(rng, seq, p=None):
    return seq[rng.choice(len(seq), p=p)]


def build_clean(rng):
    pre = ["Atlas", "Meridian", "Harbor", "Crown", "Summit", "Pioneer", "Northwind", "Sterling",
           "Vantage", "Orion", "Lumen", "Cobalt", "Granite", "Evergreen"]
    suf = ["Insurance", "Assurance", "Mutual", "General", "Indemnity"]
    names = [f"{a} {b}" for a in pre for b in suf]
    rng.shuffle(names)
    reg_names = list(REGIONS)
    reg_p = [REGIONS[r][0] for r in reg_names]
    cedants = []
    for i in range(70):
        reg = pick(rng, reg_names, reg_p)
        cedants.append(dict(code=f"C{101 + i}", name=names[i], region=reg,
                            country=pick(rng, REGIONS[reg][1]),
                            ctype=pick(rng, ["Insurer", "Mutual", "Captive"], [.7, .2, .1]),
                            rating=pick(rng, ["A+", "A", "A-", "BBB+", "BBB"], [.15, .3, .3, .15, .1])))
    cw = rng.lognormal(0, .6, len(cedants)); cw /= cw.sum()

    n = 700
    uwy_choices = [2021, 2022, 2023, 2024, 2025, 2026]
    uwy_p = [.12, .17, .19, .21, .21, .10]
    lob_codes = list(LOBS); lob_p = [LOBS[c][1] for c in lob_codes]
    treaties = []
    for i in range(n):
        ced = cedants[rng.choice(len(cedants), p=cw)]
        lob = pick(rng, lob_codes, lob_p)
        uwy = pick(rng, uwy_choices, uwy_p)
        last = 243 if uwy == 2026 else 364            # 2026 incepts Jan..Aug only
        inc = pd.Timestamp(f"{uwy}-01-01") + pd.Timedelta(days=int(rng.integers(0, last)))
        prem = float(np.clip(rng.lognormal(np.log(1.4e6), .85), 2e5, 2.5e7))
        ttype = pick(rng, ["Proportional", "Excess of Loss", "Facultative"], [.4, .5, .1])
        share = int(rng.choice([10, 15, 20, 25, 30, 40, 50])) if ttype == "Proportional" else 100
        limit = round(prem * rng.uniform(5, 14), -5)
        ccy = CCY.get(ced["country"], "USD")
        comm = {"Proportional": rng.uniform(.22, .32), "Facultative": rng.uniform(.15, .2),
                "Excess of Loss": rng.uniform(.05, .12)}[ttype]
        treaties.append(dict(
            TreatyID=f"T{i + 1:04d}", ced=ced, lob=lob, uwy=uwy, inception=inc,
            expiry=inc + pd.DateOffset(years=1) - pd.Timedelta(days=1), prem_usd=prem, ttype=ttype,
            share=share, limit_usd=limit, retention_usd=round(limit * rng.uniform(.05, .2), -4),
            ccy=ccy, uw=pick(rng, UNDERWRITERS), comm_rate=comm, ceded_rate=rng.uniform(.05, .12)))
    return cedants, treaties


def lr_factor(region, lob, uwy):
    f = 1.0
    if region == "North America" and lob == "PROP": f *= 1.30     # built-in management insight
    if region == "Europe" and lob == "CAS": f *= 1.12
    if region == "Middle East & Africa": f *= 0.90
    if uwy == 2024 and lob == "PROP": f *= 1.10
    return f


def build_tables(rng, cedants, treaties):
    A, prem, expo, claims = [], [], [], []
    for t in treaties:
        ced, rate = t["ced"], FX[t["ccy"]]
        est_local = round(t["prem_usd"] / rate, 2)
        regvar = pick(rng, REGIONS[ced["region"]][2])
        A.append(dict(TreatyID=t["TreatyID"], CedantCode=ced["code"], CedantName=ced["name"],
                      CedantCountry=ced["country"], CedantType=ced["ctype"], CedantRating=ced["rating"],
                      Region=regvar, LobCode=t["lob"], TreatyType=t["ttype"], UWYear=t["uwy"],
                      Inception=t["inception"], Expiry=t["expiry"], Currency=t["ccy"],
                      SharePct=t["share"], Limit=round(t["limit_usd"] / rate, 2),
                      Retention=round(t["retention_usd"] / rate, 2), EstAnnualPremium=est_local,
                      Underwriter=t["uw"]))
        ef_total = 0.0
        for k in range(12):                                    # monthly premium bordereaux
            start = t["inception"] + pd.DateOffset(months=k)
            if start > VAL_DATE: break
            end = start + pd.DateOffset(months=1)
            frac = float(np.clip((VAL_DATE - start) / (end - start), 0, 1))
            g = round(est_local / 12, 2)
            prem.append(dict(TreatyRef=f"TR-{t['TreatyID'][1:]}", TxnDate=start, Currency=t["ccy"], Gross=g,
                             Ceded=round(g * t["ceded_rate"], 2), Commission=round(g * t["comm_rate"], 2),
                             Earned=round(g * frac, 2)))
            ef_total += frac / 12
        expo.append(dict(TreatyRef=f"TR-{t['TreatyID'][1:]}", AsOf=VAL_DATE, Currency=t["ccy"],
                         SumInsured=round(t["limit_usd"] / rate * rng.uniform(2, 6), 2),
                         LimitExposure=round(t["limit_usd"] / rate * t["share"] / 100, 2),
                         PeakZone=pick(rng, ZONES, [.2, .12, .12, .1, .12, .09, .25])))
        if ef_total <= 0: continue
        lr = LOBS[t["lob"]][2] * lr_factor(ced["region"], t["lob"], t["uwy"]) * rng.lognormal(-.08, .4)
        total_usd = t["prem_usd"] * ef_total * lr
        k = int(rng.poisson(9 * ef_total))
        if k == 0: continue
        w = rng.lognormal(0, 1.1, k); w /= w.sum()
        for wi in w:
            usd = min(total_usd * wi, t["limit_usd"] * .98)
            loss = (t["inception"] + pd.Timedelta(days=float(rng.uniform(0, 364 * ef_total)))).normalize()
            rep = min(loss + pd.Timedelta(days=int(rng.exponential(25))), VAL_DATE)
            age = (VAL_DATE - loss).days
            p_set = .9 if age > 540 else .6 if age > 270 else .3 if age > 90 else .1
            status = "S" if rng.random() < p_set else "O"
            if status == "S" and rng.random() < .03: status = "R"
            inc_l = round(usd / rate, 2)
            if status == "S": paid, res = inc_l, 0.0
            elif status == "R": paid = round(inc_l * .7, 2); res = round(inc_l - paid, 2)
            else: paid = round(inc_l * rng.uniform(0, .5), 2); res = round(inc_l - paid, 2)
            claims.append(dict(TreatyRef=t["TreatyID"], LossDate=loss, ReportDate=rep,
                               ClaimType=pick(rng, LOBS[t["lob"]][3]), Currency=t["ccy"],
                               Paid=paid, Reserve=res, Incurred=round(paid + res, 2), Status=status))
    claims = pd.DataFrame(claims).sort_values(["ReportDate", "TreatyRef"]).reset_index(drop=True)
    claims.insert(0, "ClaimID", [f"CL{i + 1:06d}" for i in range(len(claims))])
    prem = pd.DataFrame(prem).reset_index(drop=True)
    prem.insert(0, "TxnID", [f"PT{i + 1:06d}" for i in range(len(prem))])
    return pd.DataFrame(A), claims, prem, pd.DataFrame(expo)


def plant_errors(rng, A, B, C, X, treaties):
    key, tmap, used = {}, {t["TreatyID"]: t for t in treaties}, set()

    def sample(df, n, mask=None, tag=""):
        idx = df.index if mask is None else df.index[mask]
        idx = [i for i in idx if (tag, i) not in used]
        ch = list(rng.choice(idx, n, replace=False))
        used.update((tag, i) for i in ch)
        return ch

    # --- System A ---
    ch = sample(A, 20, tag="A"); A.loc[ch, "Region"] = ""; key["blank_region_treaties"] = list(A.loc[ch, "TreatyID"])
    ch = sample(A, 15, tag="A"); A.loc[ch, "Underwriter"] = ""; key["blank_underwriter_treaties"] = list(A.loc[ch, "TreatyID"])
    ch = sample(A, 8, tag="A"); A.loc[ch, "LobCode"] = "FIN"; key["unmapped_lob_treaties"] = list(A.loc[ch, "TreatyID"])
    dup = A.sample(3, random_state=1); key["duplicate_treaty_ids"] = list(dup.TreatyID)
    A = pd.concat([A, dup], ignore_index=True)

    # --- System C premium ---
    m = C.TxnDate.dt.strftime("%Y-%m") == "2025-06"
    d = C[m].copy(); d["TxnID"] = [f"PT9{i:05d}" for i in range(len(d))]
    key["duplicate_premium_month"] = {"month": "2025-06", "rows": int(len(d))}
    C = pd.concat([C, d], ignore_index=True)
    ok = (C.TxnDate.dt.strftime("%Y-%m") != "2025-06").values
    cols = ["Gross", "Ceded", "Commission", "Earned"]
    ch = sample(C, 12, ok, "C"); C.loc[ch, cols] *= -1
    key["negative_premium_txns"] = list(C.loc[ch, "TxnID"])
    ch = sample(C, 5, ok, "C"); C.loc[ch, "Gross"] = 0.0
    key["zero_premium_txns"] = list(C.loc[ch, "TxnID"])
    orphan = C.sample(6, random_state=2).copy()
    orphan["TreatyRef"] = [f"TR-9{i:03d}" for i in range(6)]
    orphan["TxnID"] = [f"PT8{i:05d}" for i in range(6)]
    key["orphan_premium_txns"] = list(orphan.TxnID)
    C = pd.concat([C, orphan], ignore_index=True)
    cnt = C[~C.TxnDate.dt.strftime("%Y-%m").eq("2025-06")].groupby("TreatyRef").size()
    badrefs = set(C[C.Gross <= 0].TreatyRef)
    cand = [r for r in cnt[cnt == 12].index if r not in badrefs and not r.startswith("TR-9")]
    bad = list(rng.choice(cand, 10, replace=False))
    mm = C.TreatyRef.isin(bad)
    C.loc[mm, cols] = (C.loc[mm, cols] * 1.10).round(2)
    key["premium_mismatch_treaties"] = [b.replace("TR-", "T") for b in bad]

    # --- System B claims ---
    inc = B.TreatyRef.map(lambda r: tmap[r]["inception"]); exp = B.TreatyRef.map(lambda r: tmap[r]["expiry"])
    ch = sample(B, 20, tag="B")
    B.loc[ch, "LossDate"] = [inc[i] - pd.Timedelta(days=int(rng.integers(20, 300))) for i in ch]
    key["loss_before_inception"] = list(B.loc[ch, "ClaimID"])
    ok = ((VAL_DATE - exp).dt.days > 250).values
    ch = sample(B, 15, ok, "B")
    B.loc[ch, "LossDate"] = [exp[i] + pd.Timedelta(days=int(rng.integers(10, 200))) for i in ch]
    key["loss_after_expiry"] = list(B.loc[ch, "ClaimID"])
    ch = sample(B, 30, tag="B")
    B.loc[ch, "Incurred"] = (B.loc[ch, "Incurred"] * rng.uniform(1.1, 1.4, len(ch))).round(2)
    key["incurred_not_paid_plus_reserve"] = list(B.loc[ch, "ClaimID"])
    small = B.TreatyRef.map(lambda r: tmap[r]["limit_usd"] < 4e6) & ~B.TreatyRef.isin(key["unmapped_lob_treaties"])
    ch = sample(B, 12, ((B.Status == "O") & small).values, "B")
    for i in ch:
        lim_local = tmap[B.at[i, "TreatyRef"]]["limit_usd"] / FX[B.at[i, "Currency"]]
        tot = round(lim_local * rng.uniform(1.05, 1.5), 2)
        B.at[i, "Paid"] = round(tot * .2, 2); B.at[i, "Reserve"] = round(tot - B.at[i, "Paid"], 2)
        B.at[i, "Incurred"] = round(B.at[i, "Paid"] + B.at[i, "Reserve"], 2)
    key["claims_exceeding_limit"] = list(B.loc[ch, "ClaimID"])
    ch = sample(B, 10, tag="B"); B.loc[ch, "Status"] = "X"; key["unmapped_status_claims"] = list(B.loc[ch, "ClaimID"])
    orph = B.sample(25, random_state=3).copy()
    orph["TreatyRef"] = [f"T9{i:03d}" for i in range(25)]
    orph["ClaimID"] = [f"CL9{i:05d}" for i in range(25)]
    key["orphan_claims"] = list(orph.ClaimID)
    dupc = B.sample(15, random_state=4).copy()
    key["duplicate_claim_ids"] = list(dupc.ClaimID)
    B = pd.concat([B, orph, dupc], ignore_index=True)
    return A, B, C, X, key


def main():
    rng = np.random.default_rng(SEED)
    cedants, treaties = build_clean(rng)
    A, B, C, X = build_tables(rng, cedants, treaties)
    clean = dict(treaties=len(A), claims=len(B), premium_txns=len(C))
    A, B, C, X, key = plant_errors(rng, A, B, C, X, treaties)
    key["clean_counts"] = clean
    A = A.sample(frac=1, random_state=5).reset_index(drop=True)
    B = B.sample(frac=1, random_state=6).reset_index(drop=True)
    C = C.sample(frac=1, random_state=7).reset_index(drop=True)
    out = ROOT / "data" / "source"; out.mkdir(parents=True, exist_ok=True)
    A["Inception"] = A.Inception.dt.strftime("%Y-%m-%d"); A["Expiry"] = A.Expiry.dt.strftime("%Y-%m-%d")
    A.to_csv(out / "sysA_treaties.csv", index=False)
    for c in ("LossDate", "ReportDate"): B[c] = B[c].dt.strftime("%d-%b-%Y")
    B.to_csv(out / "sysB_claims.csv", index=False)
    C["TxnDate"] = C.TxnDate.dt.strftime("%d/%m/%Y"); C.to_csv(out / "sysC_premium.csv", index=False)
    X["AsOf"] = X.AsOf.dt.strftime("%d/%m/%Y"); X.to_csv(out / "sysC_exposure.csv", index=False)
    (ROOT / "data" / "answer_key.json").write_text(json.dumps(key, indent=1, default=str))
    print(f"System A treaties={len(A)}  System B claims={len(B)}  System C premium={len(C)}  exposure={len(X)}")


if __name__ == "__main__":
    main()
