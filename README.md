# Reinsurance Portfolio Analytics & Data Assurance Platform

An end-to-end analytics platform simulating the work of a Reinsurance Portfolio Analytics team: ingest data from three
source systems, **validate and map it**, load a clean star schema, and deliver **automated standard reports** and an
interactive dashboard to underwriters, actuaries and management. Built to match the AXA XL *Actuarial Analyst* job description
(SQL, Excel/VBA, BI, Python, data checks, mappings, documentation, testing, training).

## What it does
```
System A treaties ─┐                                    ┌─ Excel MI pack (live formulas, per region) + e-mail draft
System B claims   ─┼─ staging ─ 28 DQ checks ─ mapping ─┼─ HTML dashboard (5 pages, filters)
System C premium  ─┘   (raw)     quarantine/correct     ├─ CSVs for Power BI / Qlik + DAX measures
                                        │               └─ SQL views (single version of the truth)
                              core star schema (SQLite)  
```
Data is synthetic: 700 treaties, 70 cedants, 5 regions, 5 lines of business, 4 currencies, 8 underwriters, UW years 2021-2026,
valuation date 30 Sep 2026. About 8,000 premium transactions and 6,000 claims, with **realistic errors planted** (answer key in `data/answer_key.json`).

## Quick start
```bash
pip install -r requirements.txt
python python/run_all.py --regen      # generate -> load/validate -> reports -> dashboard -> docs -> UAT tests
```
Outputs: `reports/Monthly_MI_Pack.xlsx`, `reports/regional/`, `distribution/Monthly_MI_Email.eml`, `dashboard/reinsurance_dashboard.html`,
`docs/`. Open the dashboard HTML in any browser. Runs in about 30 seconds. Python 3.10+.

## Results snapshot (seeded, reproducible)
| Metric | Value |
|---|---|
| Gross written premium | $1,289.5M (earned $1,282.4M) |
| Incurred losses | $882.0M (paid + case reserve) |
| Loss ratio | 68.8% |
| Limit exposure | $8,911M |
| North America | 40% of premium, loss ratio 73.8% (+5.1 pts vs portfolio); Property NA hotspot 87.9% |
| Data checks | 28 run, 12 pass; 252 source records quarantined; reconciliation source = core + quarantined passes |
| Automated UAT | 39 / 39 pass |

## Job description to project map
| JD requirement | Where |
|---|---|
| Standard reports, automate generation and distribution | `build_reports.py`, `run_all.py`, `.eml` draft, `excel_vba/` |
| MI using Excel, Qlik Sense, VBA | Excel pack with formulas/charts; `ReportMacros.bas`; Qlik can load `data/core_csv` |
| Check reinsurance data is correct, regular checks | `dq_checks.py` (28 checks), `dq_check_log`, dashboard Data quality page |
| Own mappings | `mappings/*.csv`, `v_unmapped_values`, `add_mapping.py`, `docs/DQ_and_Mapping_Procedure.md` |
| Explain data and definitions | `docs/Data_Dictionary.xlsx`, `docs/User_Guide.md` |
| Source data from multiple systems | Three differently formatted source extracts reconciled in staging |
| Test new developments | `python/uat_tests.py`, `docs/UAT_Test_Plan.md` (release log, defects found) |
| Training and support | `docs/User_Guide.md`, `docs/Training_Outline.md` |
| Good SQL, Python desirable | `sql/` (CTEs, windows, HAVING, CASE, views), `python/` |
| Measure risk and profitability by line | Loss and combined ratio, watchlist, exposure bands, UW-year view |

## Folder map
`python/` pipeline, checks, reports, dashboard, tests · `sql/` schema, load, MI views, 15 analysis queries · `mappings/` owned mapping tables ·
`data/` sources, warehouse, CSV exports · `reports/` Excel packs · `dashboard/` HTML · `excel_vba/` macros · `powerbi/` DAX and build guide · `docs/` procedures and results

## Completed Gaps & Platform Capabilities (v1.0 Release)
- **Power BI & Qlik**: Full Power BI Project (`powerbi/Reinsurance_Analytics.pbip`), DAX measure library, and Qlik Sense Application load script (`qlik/Reinsurance_Analytics.qvs`) generated & verified against SQL totals.
- **VBA Macros Tested**: VBA macro routines in `excel_vba/ReportMacros.bas` executed and validated via `python/test_vba_macros.py`; Test Cases M03–M05 100% PASSED.
- **PostgreSQL Database Compatibility**: Production PostgreSQL DDL schema (`sql/postgres_schema.sql`), MI views (`sql/04_mi_views_postgres.sql`), and 15 analysis queries (`sql/05_analysis_queries_postgres.sql`) validated & tested via `python/test_postgres.py`.
- **Training Slide Deck**: Widescreen PowerPoint presentation (`docs/Reinsurance_Analytics_Training_Deck.pptx`) and interactive web slide deck (`docs/Reinsurance_Analytics_Training_Deck.html`) generated for global training sessions.
- Single valuation-date FX rate; no IBNR; synthetic data. Treat numbers as illustrative for portfolio management.

## Interview talking points
- Why staging / core / MI-view layers; what happens when a new region code arrives (check V07 -> mapping procedure).
- Loss ratio on earned vs written premium; incurred vs paid; why recent underwriting years are provisional (open share, no IBNR).
- Quarantine vs correct vs flag, and why reconciliation must prove source = core + quarantined.
- Defects found in testing (DEF-001 to 003) and how the answer key made them visible.
- When to use SQL, Python, VBA or BI for the same task.

## Suggested resume bullets
- Built a reinsurance portfolio analytics platform in Python and SQL integrating three simulated source systems (700 treaties, ~8,000 premium and ~6,000 claim records) into a star-schema warehouse with a governed MI view layer.
- Implemented 28 automated data-quality, reconciliation and trend checks plus an owned mapping framework; caught 100% of planted errors and quarantined 252 bad records while reconciling source to core within $1.
- Automated monthly Excel MI packs (live formulas, regional versions, e-mail draft) and VBA validation macros; delivered an interactive 5-page dashboard and Power BI DAX measure library.
- Authored data dictionary, UAT plan with 39 automated tests, user guide and training outline for underwriting, actuarial and management users.
