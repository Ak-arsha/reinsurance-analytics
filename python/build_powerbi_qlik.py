#!/usr/bin/env python3
"""
build_powerbi_qlik.py
Generates ready-to-use Power BI Project (.pbip) files, Qlik Sense load script (.qvs),
and Qlik documentation based on the core warehouse CSVs and DAX measures.
"""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POWERBI_DIR = ROOT / "powerbi"
QLIK_DIR = ROOT / "qlik"

def create_powerbi_project():
    """Builds a complete Power BI Project (.pbip) folder structure."""
    pbip_dir = POWERBI_DIR / "Reinsurance_Analytics.pbip"
    dataset_dir = POWERBI_DIR / "Reinsurance_Analytics.Dataset"
    report_dir = POWERBI_DIR / "Reinsurance_Analytics.Report"

    dataset_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    # 1. Main .pbip file
    pbip_content = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "Reinsurance_Analytics.Report"
                }
            }
        ]
    }
    (POWERBI_DIR / "Reinsurance_Analytics.pbip").write_text(json.dumps(pbip_content, indent=2), encoding="utf-8")

    # 2. Report definition.pbir
    report_pbir = {
        "version": "1.0",
        "datasetReference": {
            "byPath": {
                "path": "../Reinsurance_Analytics.Dataset"
            },
            "byConnection": None
        }
    }
    (report_dir / "definition.pbir").write_text(json.dumps(report_pbir, indent=2), encoding="utf-8")

    # 3. Report definition.json (Visual pages structure)
    report_def = {
        "name": "Reinsurance Analytics Dashboard",
        "pages": [
            {
                "name": "Executive Overview",
                "displayName": "Executive Overview",
                "displayOption": "FitToPage",
                "visuals": [
                    {"title": "GWP Card", "type": "card", "measure": "[Gross Written Premium]"},
                    {"title": "Loss Ratio Card", "type": "card", "measure": "[Loss Ratio]"},
                    {"title": "Combined Ratio Card", "type": "card", "measure": "[Combined Ratio]"},
                    {"title": "Premium by Region", "type": "barChart", "category": "dim_region[region_name]", "value": "[Gross Written Premium]"},
                    {"title": "Loss Ratio by Line of Business", "type": "columnChart", "category": "dim_lob[lob_name]", "value": "[Loss Ratio]"},
                    {"title": "Monthly Premium vs Incurred Losses", "type": "lineChart", "category": "dim_date[year_month]", "values": ["[Gross Written Premium]", "[Incurred Losses]"]},
                    {"title": "Executive Insight Text", "type": "textbox", "measure": "[Insight Text]"}
                ]
            },
            {
                "name": "Portfolio Risk",
                "displayName": "Portfolio Risk",
                "visuals": [
                    {"title": "Total Exposure", "type": "card", "measure": "[Total Exposure]"},
                    {"title": "Watchlist Count", "type": "card", "measure": "[Watchlist Treaties]"},
                    {"title": "Risk Band Breakdown", "type": "pieChart", "category": "v_treaty_summary[risk_band]", "value": "[Treaty Count]"},
                    {"title": "Watchlist Treaties Table", "type": "table", "columns": ["treaty_id", "cedant_name", "lob_name", "limit_usd", "incurred", "limit_utilisation"]}
                ]
            },
            {
                "name": "Line of Business",
                "displayName": "Line of Business",
                "visuals": [
                    {"title": "LOB Slicer", "type": "slicer", "field": "dim_lob[lob_name]"},
                    {"title": "LOB Summary Table", "type": "matrix", "rows": ["dim_lob[lob_name]"], "values": ["[Gross Written Premium]", "[Earned Premium]", "[Incurred Losses]", "[Loss Ratio]", "[Combined Ratio]"]}
                ]
            },
            {
                "name": "Claims Analysis",
                "displayName": "Claims Analysis",
                "visuals": [
                    {"title": "Claim Count", "type": "card", "measure": "[Claim Count]"},
                    {"title": "Incurred Losses", "type": "card", "measure": "[Incurred Losses]"},
                    {"title": "Claims by Type", "type": "donutChart", "category": "fact_claims[claim_type]", "value": "[Incurred Losses]"},
                    {"title": "Top 10 Loss-Making Treaties", "type": "table", "columns": ["treaty_id", "cedant_name", "incurred", "loss_ratio"]}
                ]
            },
            {
                "name": "Data Quality",
                "displayName": "Data Quality & Governance",
                "visuals": [
                    {"title": "DQ Checks Passed", "type": "card", "measure": "[DQ Checks Passed]"},
                    {"title": "Quarantined Records", "type": "card", "measure": "[Quarantined Records]"},
                    {"title": "Data Quality Check Log", "type": "table", "columns": ["check_id", "check_name", "category", "severity", "status"]}
                ]
            }
        ]
    }
    (report_dir / "definition.json").write_text(json.dumps(report_def, indent=2), encoding="utf-8")

    # 4. Tabular Model BIM file for Power BI Dataset
    model_bim = {
        "name": "Reinsurance_Analytics_Model",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True
            },
            "tables": [
                {
                    "name": "dim_region",
                    "columns": [
                        {"name": "region_id", "dataType": "int64", "sourceColumn": "region_id"},
                        {"name": "region_name", "dataType": "string", "sourceColumn": "region_name"}
                    ]
                },
                {
                    "name": "dim_lob",
                    "columns": [
                        {"name": "lob_id", "dataType": "int64", "sourceColumn": "lob_id"},
                        {"name": "lob_name", "dataType": "string", "sourceColumn": "lob_name"}
                    ]
                },
                {
                    "name": "dim_underwriter",
                    "columns": [
                        {"name": "underwriter_id", "dataType": "int64", "sourceColumn": "underwriter_id"},
                        {"name": "underwriter_name", "dataType": "string", "sourceColumn": "underwriter_name"}
                    ]
                },
                {
                    "name": "dim_cedant",
                    "columns": [
                        {"name": "cedant_id", "dataType": "int64", "sourceColumn": "cedant_id"},
                        {"name": "cedant_code", "dataType": "string", "sourceColumn": "cedant_code"},
                        {"name": "cedant_name", "dataType": "string", "sourceColumn": "cedant_name"},
                        {"name": "country", "dataType": "string", "sourceColumn": "country"},
                        {"name": "cedant_type", "dataType": "string", "sourceColumn": "cedant_type"},
                        {"name": "rating", "dataType": "string", "sourceColumn": "rating"}
                    ]
                },
                {
                    "name": "dim_treaty",
                    "columns": [
                        {"name": "treaty_id", "dataType": "string", "sourceColumn": "treaty_id"},
                        {"name": "cedant_id", "dataType": "int64", "sourceColumn": "cedant_id"},
                        {"name": "lob_id", "dataType": "int64", "sourceColumn": "lob_id"},
                        {"name": "region_id", "dataType": "int64", "sourceColumn": "region_id"},
                        {"name": "underwriter_id", "dataType": "int64", "sourceColumn": "underwriter_id"},
                        {"name": "treaty_type", "dataType": "string", "sourceColumn": "treaty_type"},
                        {"name": "underwriting_year", "dataType": "int64", "sourceColumn": "underwriting_year"},
                        {"name": "inception_date", "dataType": "dateTime", "sourceColumn": "inception_date"},
                        {"name": "expiry_date", "dataType": "dateTime", "sourceColumn": "expiry_date"},
                        {"name": "currency", "dataType": "string", "sourceColumn": "currency"},
                        {"name": "share_pct", "dataType": "double", "sourceColumn": "share_pct"},
                        {"name": "limit_usd", "dataType": "double", "sourceColumn": "limit_usd"},
                        {"name": "retention_usd", "dataType": "double", "sourceColumn": "retention_usd"},
                        {"name": "est_annual_premium_usd", "dataType": "double", "sourceColumn": "est_annual_premium_usd"},
                        {"name": "dq_flag", "dataType": "string", "sourceColumn": "dq_flag"}
                    ]
                },
                {
                    "name": "dim_date",
                    "dataCategory": "Time",
                    "columns": [
                        {"name": "date", "dataType": "dateTime", "sourceColumn": "date_key", "isKey": True},
                        {"name": "year", "dataType": "int64", "sourceColumn": "year"},
                        {"name": "quarter", "dataType": "int64", "sourceColumn": "quarter"},
                        {"name": "month", "dataType": "int64", "sourceColumn": "month"},
                        {"name": "year_month", "dataType": "string", "sourceColumn": "year_month"},
                        {"name": "year_quarter", "dataType": "string", "sourceColumn": "year_quarter"}
                    ]
                },
                {
                    "name": "fact_premium",
                    "columns": [
                        {"name": "premium_id", "dataType": "string", "sourceColumn": "premium_id"},
                        {"name": "treaty_id", "dataType": "string", "sourceColumn": "treaty_id"},
                        {"name": "txn_date", "dataType": "dateTime", "sourceColumn": "txn_date"},
                        {"name": "original_currency", "dataType": "string", "sourceColumn": "original_currency"},
                        {"name": "gross_written_premium", "dataType": "double", "sourceColumn": "gross_written_premium"},
                        {"name": "ceded_premium", "dataType": "double", "sourceColumn": "ceded_premium"},
                        {"name": "commission", "dataType": "double", "sourceColumn": "commission"},
                        {"name": "earned_premium", "dataType": "double", "sourceColumn": "earned_premium"},
                        {"name": "earned_commission", "dataType": "double", "sourceColumn": "earned_commission"}
                    ]
                },
                {
                    "name": "fact_claims",
                    "columns": [
                        {"name": "claim_id", "dataType": "string", "sourceColumn": "claim_id"},
                        {"name": "treaty_id", "dataType": "string", "sourceColumn": "treaty_id"},
                        {"name": "loss_date", "dataType": "dateTime", "sourceColumn": "loss_date"},
                        {"name": "report_date", "dataType": "dateTime", "sourceColumn": "report_date"},
                        {"name": "claim_type", "dataType": "string", "sourceColumn": "claim_type"},
                        {"name": "paid_amount", "dataType": "double", "sourceColumn": "paid_amount"},
                        {"name": "case_reserve", "dataType": "double", "sourceColumn": "case_reserve"},
                        {"name": "incurred_amount", "dataType": "double", "sourceColumn": "incurred_amount"},
                        {"name": "status", "dataType": "string", "sourceColumn": "status"},
                        {"name": "exceeds_limit", "dataType": "int64", "sourceColumn": "exceeds_limit"},
                        {"name": "dq_flag", "dataType": "string", "sourceColumn": "dq_flag"}
                    ]
                },
                {
                    "name": "fact_exposure",
                    "columns": [
                        {"name": "treaty_id", "dataType": "string", "sourceColumn": "treaty_id"},
                        {"name": "as_of_date", "dataType": "dateTime", "sourceColumn": "as_of_date"},
                        {"name": "sum_insured_usd", "dataType": "double", "sourceColumn": "sum_insured_usd"},
                        {"name": "limit_exposure_usd", "dataType": "double", "sourceColumn": "limit_exposure_usd"},
                        {"name": "peak_zone", "dataType": "string", "sourceColumn": "peak_zone"}
                    ]
                },
                {
                    "name": "_Measures",
                    "measures": [
                        {"name": "Gross Written Premium", "expression": "SUM ( fact_premium[gross_written_premium] )", "formatString": "$#,##0"},
                        {"name": "Ceded Premium", "expression": "SUM ( fact_premium[ceded_premium] )", "formatString": "$#,##0"},
                        {"name": "Net Premium", "expression": "[Gross Written Premium] - [Ceded Premium]", "formatString": "$#,##0"},
                        {"name": "Earned Premium", "expression": "SUM ( fact_premium[earned_premium] )", "formatString": "$#,##0"},
                        {"name": "Earned Commission", "expression": "SUM ( fact_premium[earned_commission] )", "formatString": "$#,##0"},
                        {"name": "Paid Losses", "expression": "SUM ( fact_claims[paid_amount] )", "formatString": "$#,##0"},
                        {"name": "Case Reserves", "expression": "SUM ( fact_claims[case_reserve] )", "formatString": "$#,##0"},
                        {"name": "Incurred Losses", "expression": "SUM ( fact_claims[incurred_amount] )", "formatString": "$#,##0"},
                        {"name": "Claim Count", "expression": "COUNTROWS ( fact_claims )", "formatString": "#,##0"},
                        {"name": "Treaty Count", "expression": "DISTINCTCOUNT ( dim_treaty[treaty_id] )", "formatString": "#,##0"},
                        {"name": "Total Exposure", "expression": "SUM ( fact_exposure[limit_exposure_usd] )", "formatString": "$#,##0"},
                        {"name": "Average Premium", "expression": "DIVIDE ( [Gross Written Premium], [Treaty Count] )", "formatString": "$#,##0"},
                        {"name": "Average Claim", "expression": "DIVIDE ( [Incurred Losses], [Claim Count] )", "formatString": "$#,##0"},
                        {"name": "Loss Ratio", "expression": "DIVIDE ( [Incurred Losses], [Earned Premium] )", "formatString": "0.0%"},
                        {"name": "Commission Ratio", "expression": "DIVIDE ( [Earned Commission], [Earned Premium] )", "formatString": "0.0%"},
                        {"name": "Admin Expense Ratio", "expression": "0.05", "formatString": "0.0%"},
                        {"name": "Combined Ratio", "expression": "[Loss Ratio] + [Commission Ratio] + [Admin Expense Ratio]", "formatString": "0.0%"},
                        {"name": "Limit Utilisation", "expression": "DIVIDE ( [Incurred Losses], SUM ( dim_treaty[limit_usd] ) )", "formatString": "0.0%"},
                        {"name": "Watchlist Treaties", "expression": "COUNTROWS ( FILTER ( VALUES ( dim_treaty[treaty_id] ), [Limit Utilisation] >= 0.8 ) )", "formatString": "#,##0"},
                        {"name": "Insight Text", "expression": "SELECTEDVALUE ( dim_region[region_name], \"Portfolio\" ) & \" writes \" & FORMAT ( DIVIDE ( [Gross Written Premium], CALCULATE ( [Gross Written Premium], ALL ( dim_region ), ALL ( dim_lob ) ) ), \"0%\" ) & \" of premium with a loss ratio of \" & FORMAT ( [Loss Ratio], \"0.0%\" ) & \".\""}
                    ]
                }
            ],
            "relationships": [
                {"fromTable": "dim_treaty", "fromColumn": "cedant_id", "toTable": "dim_cedant", "toColumn": "cedant_id"},
                {"fromTable": "dim_treaty", "fromColumn": "lob_id", "toTable": "dim_lob", "toColumn": "lob_id"},
                {"fromTable": "dim_treaty", "fromColumn": "region_id", "toTable": "dim_region", "toColumn": "region_id"},
                {"fromTable": "dim_treaty", "fromColumn": "underwriter_id", "toTable": "dim_underwriter", "toColumn": "underwriter_id"},
                {"fromTable": "fact_premium", "fromColumn": "treaty_id", "toTable": "dim_treaty", "toColumn": "treaty_id"},
                {"fromTable": "fact_claims", "fromColumn": "treaty_id", "toTable": "dim_treaty", "toColumn": "treaty_id"},
                {"fromTable": "fact_exposure", "fromColumn": "treaty_id", "toTable": "dim_treaty", "toColumn": "treaty_id"},
                {"fromTable": "fact_premium", "fromColumn": "txn_date", "toTable": "dim_date", "toColumn": "date"},
                {"fromTable": "fact_claims", "fromColumn": "loss_date", "toTable": "dim_date", "toColumn": "date"}
            ]
        }
    }
    (dataset_dir / "model.bim").write_text(json.dumps(model_bim, indent=2), encoding="utf-8")
    print(f"Power BI Project created successfully at {pbip_dir}")


def create_qlik_sense_app():
    """Builds Qlik Sense Script (.qvs) and Qlik Documentation."""
    QLIK_DIR.mkdir(parents=True, exist_ok=True)

    qvs_content = """///$tab Main
SET DateFormat='YYYY-MM-DD';
SET TimestampFormat='YYYY-MM-DD hh:mm:ss';
SET MoneyThousandSep=',';
SET MoneyDecimalSep='.';
SET MoneyFormat='$#,##0.00;($#,##0.00)';

///$tab Mapping Tables
Map_LOB:
MAPPING LOAD source_value, mapped_value FROM [lib://DataFiles/map_lob.csv] (txt, utf8, embedded labels, delimiter is ',');

Map_Region:
MAPPING LOAD source_value, mapped_value FROM [lib://DataFiles/map_region.csv] (txt, utf8, embedded labels, delimiter is ',');

Map_Currency:
MAPPING LOAD source_value, mapped_value FROM [lib://DataFiles/map_currency.csv] (txt, utf8, embedded labels, delimiter is ',');

Map_Claim_Status:
MAPPING LOAD source_value, mapped_value FROM [lib://DataFiles/map_claim_status.csv] (txt, utf8, embedded labels, delimiter is ',');

///$tab Dimensions
Dim_Region:
LOAD
    region_id,
    region_name
FROM [lib://DataFiles/dim_region.csv] (txt, utf8, embedded labels, delimiter is ',');

Dim_LOB:
LOAD
    lob_id,
    lob_name
FROM [lib://DataFiles/dim_lob.csv] (txt, utf8, embedded labels, delimiter is ',');

Dim_Underwriter:
LOAD
    underwriter_id,
    underwriter_name
FROM [lib://DataFiles/dim_underwriter.csv] (txt, utf8, embedded labels, delimiter is ',');

Dim_Cedant:
LOAD
    cedant_id,
    cedant_code,
    cedant_name,
    country AS cedant_country,
    cedant_type,
    rating
FROM [lib://DataFiles/dim_cedant.csv] (txt, utf8, embedded labels, delimiter is ',');

Dim_Treaty:
LOAD
    treaty_id,
    cedant_id,
    lob_id,
    region_id,
    underwriter_id,
    treaty_type,
    underwriting_year,
    Date(Date#(inception_date, 'YYYY-MM-DD')) AS inception_date,
    Date(Date#(expiry_date, 'YYYY-MM-DD')) AS expiry_date,
    currency,
    share_pct,
    limit_usd,
    retention_usd,
    est_annual_premium_usd,
    dq_flag AS treaty_dq_flag
FROM [lib://DataFiles/dim_treaty.csv] (txt, utf8, embedded labels, delimiter is ',');

///$tab Facts
Fact_Premium:
LOAD
    premium_id,
    treaty_id,
    Date(Date#(txn_date, 'YYYY-MM-DD')) AS date_key,
    original_currency,
    gross_written_premium,
    ceded_premium,
    gross_written_premium - ceded_premium AS net_premium,
    commission,
    earned_premium,
    earned_commission
FROM [lib://DataFiles/fact_premium.csv] (txt, utf8, embedded labels, delimiter is ',');

Fact_Claims:
LOAD
    claim_id,
    treaty_id,
    Date(Date#(loss_date, 'YYYY-MM-DD')) AS date_key,
    Date(Date#(report_date, 'YYYY-MM-DD')) AS report_date,
    claim_type,
    paid_amount,
    case_reserve,
    incurred_amount,
    status AS claim_status,
    exceeds_limit,
    dq_flag AS claim_dq_flag
FROM [lib://DataFiles/fact_claims.csv] (txt, utf8, embedded labels, delimiter is ',');

Fact_Exposure:
LOAD
    treaty_id,
    Date(Date#(as_of_date, 'YYYY-MM-DD')) AS exposure_as_of_date,
    sum_insured_usd,
    limit_exposure_usd,
    peak_zone
FROM [lib://DataFiles/fact_exposure.csv] (txt, utf8, embedded labels, delimiter is ',');

///$tab Master Calendar
MasterCalendar:
LOAD
    date_key,
    Year(date_key) AS Year,
    Month(date_key) AS Month,
    Dual(Month(date_key) & '-' & Year(date_key), Year(date_key)*12 + Month(date_key)) AS YearMonth,
    'Q' & Ceil(Month(date_key)/3) AS Quarter,
    Year(date_key) & '-Q' & Ceil(Month(date_key)/3) AS YearQuarter
FROM [lib://DataFiles/dim_date.csv] (txt, utf8, embedded labels, delimiter is ',');
"""

    (POWERBI_DIR / "Reinsurance_Analytics.qvs").write_text(qvs_content, encoding="utf-8")
    (QLIK_DIR / "Reinsurance_Analytics.qvs").write_text(qvs_content, encoding="utf-8")

    qlik_readme = """# Qlik Sense Reinsurance Portfolio Analytics Application

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
"""
    (QLIK_DIR / "README_qlik.md").write_text(qlik_readme, encoding="utf-8")
    print(f"Qlik Sense script and documentation created at {QLIK_DIR}")

if __name__ == "__main__":
    create_powerbi_project()
    create_qlik_sense_app()
