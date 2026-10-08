# UAT test plan and release log

## A. Automated regression tests: `python/uat_tests.py` (39 cases, results in `docs/UAT_Results.csv`)
| Area | What it proves |
|---|---|
| Detection (A01-A17) | Every error planted by `generate_data.py` (see `data/answer_key.json`) is caught by the intended check |
| Reconciliation (B-Z01/Z02) | Source premium and claims = core + quarantined |
| Integrity (B01-B08) | No orphans, duplicates, bad dates or negative premium in the core; staged rows = loaded + quarantined |
| SQL (C01-C03) | All 15 analysis queries run; view-based and fact-based loss ratio agree |
| Reports (D01-D05) | Excel pack and dashboard totals tie to SQL; no formula errors |
| Mapping (E01-E02) | The mapping change procedure clears unmapped values on a scratch copy |

## B. Manual & Automated test cases (executed before each release)
| ID | Component | Steps | Expected | Result |
|---|---|---|---|---|
| M01 | Excel pack | Open `Monthly_MI_Pack.xlsx`, change Summary!B4 (admin ratio) to 8% | Combined ratios rise by 3 points, loss ratios unchanged | PASS |
| M02 | Excel pack | Filter Treaty_Data to one region | Summary does not change (it is whole-file); regional pack totals match region row | PASS |
| M03 | VBA | Import `ReportMacros.bas`, run `ValidatePack` | Passes and reports the count of failing DQ checks (16 failing checks) | PASS |
| M04 | VBA | Change one Treaty_Data GWP value, run `ValidatePack` | Reports mismatch, 'Do NOT send' | PASS |
| M05 | VBA | Run `SplitByRegion` | Six regional workbooks created, row counts add up to 700 in Treaty_Data | PASS |
| M06 | Dashboard | Overview: click 'North America' bar | KPI strip shows ~$513M GWP, filter box shows region | PASS |
| M07 | Dashboard | Line of business tab: click 'Casualty' row | Selection KPI shows Casualty, UW-year chart updates | PASS |
| M08 | Dashboard | Resize to phone width | Nav becomes a scrolling tab strip, no sideways page scroll | PASS |
| M09 | Power BI | Build model per `powerbi/README_powerbi.md`; compare Loss Ratio card to SQL Q3 | Matches to 0.1 pt (68.8%) | PASS |

## C. Release log
| Version | Change | Tested by | Defects found during testing |
|---|---|---|---|
| 0.1 | Initial warehouse, 28 data checks, 15 queries | Author | DEF-001 to DEF-003 below |
| 0.2 | Excel pack, e-mail draft, dashboard, VBA module | Author | none open |
| 1.0 | Power BI PBIP project, Qlik Sense QVS app, VBA execution, PostgreSQL testing, Training Slide Deck | Author | 44 / 44 tests PASS |

### Defects found and fixed during build
- **DEF-001**: Check K02 flagged 26 treaties instead of the 10 planted. Cause: negative and zero premium rows distorted the booked total. Fix: K02 now compares only valid, de-duplicated instalments.
- **DEF-002**: V02 (loss after expiry) found 16 claims versus 15 planted. Cause: the generator could place a loss on day 365, one day after expiry. Fix: generator limited to day 364.
- **DEF-003**: Property loss ratio was about 92% (portfolio ~85%). Cause: planted over-limit claims were attached to treaties with very large limits. Fix: planted over-limit claims restricted to treaties with limits under $4M. Portfolio loss ratio now 68.8%.

### Status of Gaps / Open Items
- **Power BI & Qlik**: Power BI Project (`Reinsurance_Analytics.pbip`), DAX measures, and Qlik Sense Application load script (`Reinsurance_Analytics.qvs`) fully created, verified & documented.
- **VBA macros**: Executed & verified via automated test suite (`python/test_vba_macros.py`). Test cases M03-M05 fully PASSED.
- **PostgreSQL**: PostgreSQL DDL schema (`postgres_schema.sql`), MI views (`04_mi_views_postgres.sql`), and 15 analysis queries (`05_analysis_queries_postgres.sql`) fully validated & verified via `python/test_postgres.py`.
- **Training Deck**: Full 16-slide PowerPoint presentation (`Reinsurance_Analytics_Training_Deck.pptx`) and interactive web presentation (`Reinsurance_Analytics_Training_Deck.html`) generated and aligned with AXA XL training outline.
