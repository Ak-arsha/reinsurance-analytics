# Power BI build guide

The .pbix itself is not included (it must be authored in Power BI Desktop). Everything it needs is: clean data, a tested model design and the measures.

## 1. Get the data
Use `data/core_csv/*.csv` (Get Data > Text/CSV), or connect to PostgreSQL after loading with `sql/postgres_schema.sql` (untested DDL).
In Power Query, set `dim_date[date_key]`, `fact_premium[txn_date]`, `fact_claims[loss_date]` and the treaty inception/expiry dates to **Date**; rename `date_key` to `date`.

## 2. Star schema
```
dim_cedant ─┐                 ┌─ dim_lob
dim_region ─┼─ dim_treaty ────┤
dim_underwriter ┘     │       └─ (treaty is the shared conformed dimension)
                      ├── fact_premium ── dim_date[date] (txn_date)
                      ├── fact_claims  ── dim_date[date] (loss_date)
                      └── fact_exposure
```
Relationships (all many-to-one, single direction, from the dimension to the fact):
`dim_treaty[treaty_id]` to each fact's `treaty_id`; `dim_cedant`, `dim_lob`, `dim_region`, `dim_underwriter` to `dim_treaty` by their id; `dim_date[date]` to `fact_premium[txn_date]` and `fact_claims[loss_date]`.
Why: both facts share treaty, line, region and date, so one slicer filters premium and claims consistently; measures divide claims by premium without fan-out.
Hide foreign keys. Mark `dim_date` as the date table.

## 3. Measures
Paste `powerbi/dax_measures.dax`. Check: Loss Ratio card (no filters) = 68.8%; GWP = $1,289M; Treaty Count = 700.

## 4. Pages (mirror the HTML dashboard)
1. Executive Overview: KPI cards, premium by region, loss ratio by line, monthly premium vs incurred, Insight Text measure.
2. Portfolio Risk: `risk_band` from `v_treaty_summary.csv`, exposure by region, watchlist table filtered on `Limit Utilisation >= 0.8`.
3. Line of Business: slicer on `dim_lob[lob_name]`; cards for premium, incurred, loss ratio, combined ratio, exposure.
4. Claims: trend, type, region, status, top-N claims.
5. Data Quality: `dq_check_log.csv`, `v_dq_health.csv`, `v_unmapped_values.csv`.

Conditional formatting: loss ratio red above 80%, combined ratio red above 100%.
