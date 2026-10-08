# User guide: Reinsurance Portfolio MI

For underwriters, actuaries and management. Figures are USD, valuation date 30 Sep 2026.

## Which output should I use?
| Need | Use |
|---|---|
| Quick interactive look, filters, drill by region or line | `dashboard/reinsurance_dashboard.html` |
| Numbers to paste into a paper or send on | `reports/Monthly_MI_Pack.xlsx` (regional versions in `reports/regional/`) |
| Your own analysis | `data/core_csv/` (load into Power BI, Qlik Sense or Excel) |
| A one-off question | Ask Portfolio Analytics; see "Asking for data" below |

## Dashboard pages
- **Overview**: headline premium, losses, loss and combined ratio, executive insights. Click a bar to filter by that region or line.
- **Portfolio risk**: treaties by share of limit consumed, exposure by region, the watchlist (80% of limit or more), largest cedants.
- **Line of business**: compare the five lines side by side; click a row to select one and the other panels update.
- **Claims**: trend, claim types, settled vs open, largest claims.
- **Data quality**: what was checked, what failed, how many records were excluded.

## Reading the numbers
- **Loss ratio** = incurred / earned premium. **Combined ratio** adds commission and a 5% admin assumption; above 100% means an underwriting loss.
- **Incurred** = paid + case reserve. There is no IBNR, so recent underwriting years look better than they will end up. A high *open share* means the year is still developing.
- **Underwriting year** is when the treaty incepted; **loss date** is when the loss happened. The trend charts use loss date for claims and booking date for premium.
- Amounts are converted at one valuation-date FX rate.
- Records that failed data checks are excluded (Data quality page). If a number looks wrong, check there first.

## Asking for data
Tell us: (1) the question, (2) the cut (region, line, underwriting year), (3) the basis (written or earned, paid or incurred), (4) the deadline.
Definitions and sources for every field are in `docs/Data_Dictionary.xlsx`.

## Report pack routine (for the analyst)
Run `python python/run_all.py`, check `docs/UAT_Results.csv` shows all PASS, open `distribution/Monthly_MI_Email.eml` and send.
