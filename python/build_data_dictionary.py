#!/usr/bin/env python3
"""Build docs/Data_Dictionary.xlsx (field, definition, source system, transformation, example)."""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parents[1]
ROWS = """
dim_treaty|treaty_id|Unique reinsurance treaty / placement identifier|System A TreatyID|Duplicates removed (first row kept)|T0042
dim_treaty|cedant_id|Key of the ceding company that buys the cover|System A CedantCode|Surrogate key via dim_cedant|12
dim_treaty|lob_id|Line of business of the treaty|System A LobCode|Mapped through map_lob; unknown codes load as 'Unmapped'|Property
dim_treaty|region_id|Reporting region of the treaty|System A Region (free text)|Mapped through map_region; blank loads as 'Unassigned'|North America
dim_treaty|underwriter_id|Underwriter responsible for the treaty|System A Underwriter|Blank loads as 'Unassigned'|Priya Nair
dim_treaty|treaty_type|Proportional, Excess of Loss or Facultative|System A TreatyType|None|Excess of Loss
dim_treaty|underwriting_year|Calendar year in which the treaty incepted (not accident year)|System A UWYear|None|2024
dim_treaty|inception_date / expiry_date|First and last day of cover|System A|Parsed to ISO date|2024-03-01 / 2025-02-28
dim_treaty|currency|Original currency of the treaty|System A Currency|Validated against map_currency|EUR
dim_treaty|share_pct|Reinsurer's share of the risk (100 for non-proportional)|System A SharePct|None|25
dim_treaty|limit_usd|Maximum amount payable under the treaty (100% basis) in USD|System A Limit|x rate_to_usd (valuation-date FX)|12,500,000
dim_treaty|retention_usd|Attachment point: losses below this stay with the cedant|System A Retention|x rate_to_usd|1,000,000
dim_treaty|est_annual_premium_usd|Expected annual premium used for reconciliation (check K02)|System A EstAnnualPremium|x rate_to_usd|1,800,000
dim_treaty|dq_flag|Why the record carries a data-quality flag (blank if clean)|Derived|unmapped_lob / unassigned_region / unassigned_underwriter|unmapped_lob
dim_cedant|cedant_name / country / rating|Ceding company name, domicile and financial-strength rating|System A|First occurrence per CedantCode|Atlas Mutual / UK / A
fact_premium|premium_id|Premium transaction identifier (monthly bordereau instalment)|System C TxnID|None|PT000904
fact_premium|txn_date|Booking date of the instalment|System C TxnDate (dd/mm/yyyy)|Parsed to ISO date|2025-04-25
fact_premium|gross_written_premium|Premium booked from the cedant for the instalment, USD|System C Gross|x rate_to_usd|160,606.71
fact_premium|ceded_premium|Part of GWP passed on to retrocessionaires, USD|System C Ceded|x rate_to_usd|8,481.10
fact_premium|commission|Ceding commission paid on the instalment (written basis), USD|System C Commission|x rate_to_usd|12,265.76
fact_premium|earned_premium|Part of the instalment whose risk period has elapsed at the valuation date, USD|System C Earned|x rate_to_usd|160,606.71
fact_premium|earned_commission|Commission matching earned premium = commission x earned / gross|Derived|Calculated in 03_core_load.sql|12,265.76
fact_claims|claim_id|Claim identifier|System B ClaimID|Duplicates removed (first kept)|CL003403
fact_claims|treaty_id|Treaty the claim is recovered under|System B TreatyRef|Orphans quarantined|T0500
fact_claims|loss_date|Date of loss (accident date)|System B LossDate (dd-Mon-yyyy)|Parsed; must fall inside treaty period else quarantined|2024-12-06
fact_claims|report_date|Date the loss was notified to the reinsurer|System B ReportDate|Parsed to ISO date|2024-12-12
fact_claims|claim_type|Cause / class of loss|System B ClaimType|None|Natural Catastrophe
fact_claims|paid_amount|Cumulative amount already paid, USD|System B Paid|x rate_to_usd|150,818.03
fact_claims|case_reserve|Outstanding estimate for the claim, USD (no IBNR)|System B Reserve|x rate_to_usd|0
fact_claims|incurred_amount|Paid + case reserve, USD|Derived (source Incurred ignored)|Recomputed; mismatches logged by K01|150,818.03
fact_claims|status|Settled, Open or Reopened|System B Status (S/O/R)|Mapped through map_claim_status; unknown loads as 'Unmapped'|Settled
fact_claims|exceeds_limit|1 if incurred is above the treaty limit (needs review)|Derived|incurred_usd > limit_usd|0
fact_exposure|limit_exposure_usd|Reinsurer's share of the limit at the valuation date, USD|System C LimitExposure|x rate_to_usd|3,125,000
fact_exposure|sum_insured_usd|Total insured value behind the treaty, USD|System C SumInsured|x rate_to_usd|45,000,000
fact_exposure|peak_zone|Peril zone driving accumulation|System C PeakZone|None|Florida
Measures|Gross written premium (GWP)|Premium booked, before retrocession and before earning|fact_premium|SUM(gross_written_premium)|
Measures|Earned premium|Premium for risk exposure elapsed at valuation date (pro-rata by month)|fact_premium|SUM(earned_premium)|
Measures|Incurred losses|Paid + case reserve (excludes IBNR, so immature years look better than ultimate)|fact_claims|SUM(incurred_amount)|
Measures|Loss ratio|Incurred losses / earned premium|views|incurred / earned|68.8%
Measures|Commission ratio|Earned commission / earned premium|views|earned_commission / earned|
Measures|Combined ratio|Loss ratio + commission ratio + admin expense assumption (5%)|views|ref_assumptions.admin_expense_ratio|
Measures|Limit utilisation|Incurred / treaty limit; >= 80% puts the treaty on the watchlist|views|incurred / limit_usd|
Measures|Claim frequency|Claims per treaty|views|claim_count / treaties|
Measures|Claim severity|Average incurred per claim|views|incurred / claim_count|
Governance|map_* tables|Owned mapping tables: source value -> reporting value, with owner and date|mappings/*.csv|Edited via python/add_mapping.py|
Governance|dq_check_log|One row per data-quality check per run: tested, failed, status, action|pipeline|Written by python/pipeline.py|
Governance|dq_failed_records|Every failing record with its check and disposition (Quarantined, Corrected, Flagged...)|pipeline|Quarantined rows never reach the core|
Governance|FX basis|Single valuation-date rate per currency; no historic FX|map_currency|Limitation: restates old premium at today's FX|
"""


def main(root=ROOT):
    wb = Workbook(); ws = wb.active; ws.title = "Data dictionary"
    heads = ["Table", "Field", "Definition", "Source", "Transformation", "Example"]
    ws.append(heads)
    for line in ROWS.strip().splitlines(): ws.append(line.split("|"))
    for c in ws[1]: c.font = Font(name="Arial", bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3A4D")
    for row in ws.iter_rows(min_row=2):
        for c in row: c.font = Font(name="Arial", size=10); c.alignment = Alignment(wrap_text=True, vertical="top")
    for col, w in zip("ABCDEF", [14, 26, 62, 28, 42, 22]): ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
    wb.save(Path(root) / "docs" / "Data_Dictionary.xlsx"); print("Data dictionary:", ws.max_row - 1, "entries")


if __name__ == "__main__":
    main()
