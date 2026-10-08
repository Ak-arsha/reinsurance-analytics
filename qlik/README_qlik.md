# Qlik Sense Reinsurance Portfolio Analytics Application

This folder contains the complete **Qlik Sense Load Script (`Reinsurance_Analytics.qvs`)** and build instructions for creating the Qlik Sense application for AXA XL Reinsurance Portfolio Analytics.

## 1. Data Connection & Load
1. Open Qlik Sense Desktop or Qlik Sense Enterprise.
2. Create a new App named **"AXA XL Reinsurance Analytics"**.
3. Go to the **Data Load Editor**.
4. Create a folder connection named `DataFiles` pointing to `data/core_csv/` (or `mappings/`).
5. Include or copy the script from `Reinsurance_Analytics.qvs`.
6. Click **Load Data**.

## 2. Qlik Star Schema Model
```
Dim_Cedant ───┐
Dim_Region ───┼── Dim_Treaty ──── Dim_LOB / Dim_Underwriter
              │         ├── Fact_Premium ─── MasterCalendar (date_key)
              │         ├── Fact_Claims  ─── MasterCalendar (date_key)
              │         └── Fact_Exposure
```

## 3. Qlik Master Measures / Expressions
- **Gross Written Premium**: `Sum(gross_written_premium)`
- **Earned Premium**: `Sum(earned_premium)`
- **Incurred Losses**: `Sum(incurred_amount)`
- **Paid Losses**: `Sum(paid_amount)`
- **Loss Ratio**: `Sum(incurred_amount) / Sum(earned_premium)`
- **Commission Ratio**: `Sum(earned_commission) / Sum(earned_premium)`
- **Combined Ratio**: `(Sum(incurred_amount) + Sum(earned_commission)) / Sum(earned_premium) + 0.05`
- **Limit Exposure**: `Sum(limit_exposure_usd)`
- **Watchlist Count**: `Count({<treaty_id={"=Sum(incurred_amount)/Sum(limit_usd) >= 0.8"}>} DISTINCT treaty_id)`

## 4. Sheet Layouts
1. **Executive Overview**: KPI Cards (GWP, Earned, Incurred, Loss Ratio 68.8%), Bar Chart (GWP by Region), Line Chart (Monthly Trend).
2. **Portfolio Risk**: Exposure by Region, Risk Band Donut, Watchlist Table (`Limit Utilisation >= 80%`).
3. **Line of Business**: Filter Pane (LOB), Matrix Table with Loss & Combined Ratios.
4. **Claims Analysis**: Claim Type Pie Chart, Paid vs Case Reserve Stacked Bar, Top 10 Loss-Making Treaties.
5. **Data Quality**: Data Quality Log Table (`dq_check_log.csv`), Quarantined Records Table.
