#!/usr/bin/env python3
"""
build_training_deck.py
Generates the PowerPoint slide deck (docs/Reinsurance_Analytics_Training_Deck.pptx)
and an interactive HTML presentation (docs/Reinsurance_Analytics_Training_Deck.html)
matching the AXA XL Actuarial Analyst role requirements and training outline.
"""

from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"

# Colors
NAVY = RGBColor(0, 32, 96)       # AXA XL Deep Navy
TEAL = RGBColor(0, 128, 128)     # AXA XL Accent Teal
SLATE = RGBColor(30, 41, 59)     # Text Dark Slate
LIGHT_BG = RGBColor(244, 246, 249)
WHITE = RGBColor(255, 255, 255)
RED = RGBColor(180, 40, 40)

def create_pptx():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)   # 16:9 widescreen
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    slides_data = [
        {
            "type": "title",
            "title": "Reinsurance Portfolio Analytics & Data Assurance Platform",
            "subtitle": "Global Reinsurance Training & Operational Playbook | AXA XL Portfolio Analytics",
            "bullets": [
                "Single Version of the Truth for Underwriting, Actuarial & Senior Management",
                "Automated Excel MI Packs, Power BI & Qlik Integration, VBA Macros & Data Quality Engine",
                "Valuation Date: 30-Sep-2026 | Portfolio Premium: $1.29B GWP | Loss Ratio: 68.8%"
            ]
        },
        {
            "type": "content",
            "title": "1. Program Context & Why This Platform Exists",
            "subtitle": "Transitioning from Fragmented Spreadsheets to Governed Reinsurance Analytics",
            "boxes": [
                {"title": "The Old Way (Legacy Challenges)", "items": [
                    "Manual spreadsheets with broken formulas and mismatched totals across regions",
                    "Three isolated source systems (Treaties, Claims, Exposure) with duplicate records",
                    "No audit trail for unmapped regions, LOB codes, or status codes",
                    "Days spent manually producing monthly regional report packs"
                ]},
                {"title": "The New Way (Platform Solution)", "items": [
                    "Automated ETL pipeline loading a single conformed star-schema warehouse",
                    "28 automated data quality, reconciliation & trend checks on every load",
                    "Governed MI views standardizing metrics (Loss Ratio, Combined Ratio, Exposure)",
                    "One-click Excel MI pack, VBA automated validation, and interactive Power BI/Qlik"
                ]}
            ]
        },
        {
            "type": "content",
            "title": "2. Platform Architecture & Data Flow",
            "subtitle": "End-to-End Governance from Source Ingestion to Executive Dashboards",
            "boxes": [
                {"title": "Data Ingestion & Staging", "items": [
                    "System A (Treaties), System B (Claims), System C (Premium & Exposure)",
                    "Raw data ingested into staging tables (stg_treaties, stg_claims, stg_premium)",
                    "Unmapped values routed to governed mapping tables (map_region, map_lob)"
                ]},
                {"title": "Data Quality & Core Star Schema", "items": [
                    "28 DQ checks evaluate completeness, integrity, reconciliation & trends",
                    "Invalid/corrupted rows quarantined to dq_failed_records; zero silent drops",
                    "Clean data loaded into dim_treaty, dim_cedant, fact_premium, fact_claims"
                ]},
                {"title": "Analytics & Distribution", "items": [
                    "v_treaty_summary & MI views enforce single metric definitions",
                    "Monthly_MI_Pack.xlsx with VBA macros, .eml draft, Power BI .pbip & Qlik .qvs",
                    "Interactive 5-page web dashboard for live executive portfolio drilldowns"
                ]}
            ]
        },
        {
            "type": "content",
            "title": "3. Interactive Dashboard & Tooling Tour",
            "subtitle": "Navigating the 5 Core Perspectives for Underwriters and Actuaries",
            "boxes": [
                {"title": "1. Executive Overview", "items": ["KPI cards ($1,289.5M GWP, 68.8% Loss Ratio)", "Regional premium breakdown (North America 40%)", "Monthly premium vs incurred loss trend chart"]},
                {"title": "2. Portfolio Risk & Watchlist", "items": ["Limit exposure ($8,911M total limit exposure)", "Watchlist treaties table (Limit Utilisation >= 80%)", "Risk band segmentation (Critical, High, Medium, Low)"]},
                {"title": "3. Line of Business Analysis", "items": ["5 Lines of Business: Property, Casualty, Marine, etc.", "Loss Ratio & Combined Ratio comparison", "Underwriting year emergence curves"]},
                {"title": "4. Claims & Data Quality", "items": ["Top-N loss-making treaties and claim severity bands", "Data quality health score (12 pass, 16 failing warnings)", "Quarantined record audit log and mapping backlog"]}
            ]
        },
        {
            "type": "content",
            "title": "4. Hands-On Live Exercise",
            "subtitle": "Investigating Portfolio Hotspots & Regional Performance",
            "boxes": [
                {"title": "Exercise Scenario", "items": [
                    "Question: Identify the highest-risk Line of Business in North America.",
                    "Step 1: Filter Dashboard / Power BI to 'North America' region.",
                    "Step 2: Compare Loss Ratios across LOBs (Property NA vs Casualty NA).",
                    "Step 3: Check the Watchlist table for over-utilised treaties in that zone."
                ]},
                {"title": "Key Findings & Actuarial Action", "items": [
                    "Property NA has a loss ratio of 87.9% (+19.1 pts vs portfolio average of 68.8%).",
                    "Driven by 3 catastrophe claims exceeding $1.0M incurred in Peak Zone NA-CAT1.",
                    "Action: Refer Property NA treaties for underwriter review and limit cap adjustment."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "5. Actuarial Metrics & Terminology Standard",
            "subtitle": "Eliminating Common Disputes Around Portfolio Metrics",
            "boxes": [
                {"title": "Premium & Loss Definitions", "items": [
                    "Gross Written Premium (GWP): Total premium committed on booked transactions.",
                    "Earned Premium: Pro-rata premium earned based on elapsed treaty coverage period.",
                    "Incurred Losses: Paid Claims + Open Case Reserves (excluding IBNR in v0.2).",
                    "Loss Ratio = Incurred Losses / Earned Premium (standard actuarial basis)."
                ]},
                {"title": "Underwriting Year vs Loss Date", "items": [
                    "Underwriting Year (UWY): Groups contracts by inception year (2021-2026).",
                    "Loss Date: Date when the catastrophe/loss event occurred.",
                    "Combined Ratio = Loss Ratio + Commission Ratio + Admin Expense Ratio (5%).",
                    "Open Share %: Percentage of incurred losses still in open/reopened status."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "6. Data Quality Engine & Reconciliation Proof",
            "subtitle": "How We Guarantee Data Trust and Mathematical Integrity",
            "boxes": [
                {"title": "Automated Reconciliation Rule", "items": [
                    "Reconciliation Formula: Source Premium = Core Loaded Premium + Quarantined Premium",
                    "Rule Z01 & Z02 prove zero dollars are unaccounted for or silently lost.",
                    "Exact Match: $1,289.5M loaded + $3.4M quarantined = $1,292.9M source premium."
                ]},
                {"title": "Quarantine & Exception Handling", "items": [
                    "Quarantined records (e.g. invalid region 'XYZ', missing underwriter ID, orphan claims).",
                    "Quarantined rows do NOT flow into core MI views to prevent report distortion.",
                    "Quarantined rows are recorded in dq_failed_records for data steward correction."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "7. Excel MI Pack & VBA Macro Automation",
            "subtitle": "Operational Guide to Running Monthly_MI_Pack.xlsx & Macros",
            "boxes": [
                {"title": "Excel Pack Structure", "items": [
                    "Summary sheet: High-level executive KPIs, loss ratios, and regional totals.",
                    "Treaty_Data sheet: Full list of 700 treaties with live Excel SUMIFS formulas.",
                    "DQ_Log sheet: Real-time status of 28 data quality checks."
                ]},
                {"title": "VBA Macro Automation (ReportMacros.bas)", "items": [
                    "ValidatePack(): Pre-release audit checking for cell errors and GWP tie-outs.",
                    "SplitByRegion(): Automatically splits pack into 6 regional workbooks.",
                    "ExportSummaryPdf(): Saves PDF executive summary for distribution.",
                    "RefreshPack(): Recalculates all formulas and updates timestamp."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "8. Power BI Project (.pbip) & DAX Measure Library",
            "subtitle": "Enterprise Business Intelligence Model Architecture",
            "boxes": [
                {"title": "Power BI Star Schema", "items": [
                    "Conformed treaty dimension (dim_treaty) linking dim_cedant, dim_region, dim_lob.",
                    "Fact tables: fact_premium, fact_claims, fact_exposure linked to dim_date.",
                    "Single direction 1:N relationships prevent fan-out and double-counting."
                ]},
                {"title": "28 Governed DAX Measures", "items": [
                    "Base Measures: [Gross Written Premium], [Earned Premium], [Incurred Losses]",
                    "Ratio Measures: [Loss Ratio], [Commission Ratio], [Combined Ratio]",
                    "Time Intelligence: [GWP Prior Year], [GWP YoY Growth], [Loss Ratio Rolling 12M]",
                    "Dynamic Insight Text: Auto-generates natural language regional insights."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "9. Qlik Sense Application Architecture",
            "subtitle": "QVS Scripting & In-Memory Associative Model",
            "boxes": [
                {"title": "Qlik Load Script (Reinsurance_Analytics.qvs)", "items": [
                    "Automated mapping tables (Map_LOB, Map_Region, Map_Currency, Map_Status).",
                    "Master Calendar generator converting raw dates into fiscal quarters & months.",
                    "Star schema loading directly from clean CSV exports in data/core_csv/."
                ]},
                {"title": "Qlik Master Items & Interactive Sheets", "items": [
                    "Master Measures: Sum(incurred_amount)/Sum(earned_premium), Combined Ratio.",
                    "Executive Overview, Portfolio Risk, LOB, Claims, and DQ Health sheets.",
                    "Associative engine enables instant multi-dimensional filtering across regions."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "10. User Acceptance Testing & Quality Assurance",
            "subtitle": "39 Automated Regression Tests & Verification Framework",
            "boxes": [
                {"title": "Automated UAT Suite (python/uat_tests.py)", "items": [
                    "A01-A17: Planted Error Detection (100% recall verified against answer key).",
                    "B01-B08: Database Integrity & Reconciliation (zero orphan records in core).",
                    "C01-C03: SQL Query Integrity & View vs Fact Loss Ratio tie-out.",
                    "D01-D05: Report Tie-Outs (Excel pack and Dashboard match SQL exactly)."
                ]},
                {"title": "VBA & Manual UAT Test Cases (M01-M05)", "items": [
                    "M03: ValidatePack execution verified (16 DQ warnings reported).",
                    "M04: ValidatePack GWP mismatch detection verified ('Do NOT send' flag).",
                    "M05: SplitByRegion verified (6 regional workbooks generated, 700 total rows)."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "11. Data Governance & Mapping Procedure",
            "subtitle": "Operational Workflow for Adding New Regions, LOBs, and Currencies",
            "boxes": [
                {"title": "Identifying Unmapped Values", "items": [
                    "Run query Q14 or inspect v_unmapped_values view.",
                    "Identifies raw codes from source systems that lack an explicit mapping.",
                    "Example: Raw LOB code 'FIN' arriving in System A treaties."
                ]},
                {"title": "Executing Governance Script (add_mapping.py)", "items": [
                    "Run command: python python/add_mapping.py lob FIN \"Financial Lines\"",
                    "Appends mapping to mappings/map_lob.csv with audit user & timestamp.",
                    "Next pipeline run re-classifies quarantined records automatically into core."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "12. Portfolio Key Insights & Actuarial Findings",
            "subtitle": "Summary Findings from the Valuation Date (30-Sep-2026)",
            "boxes": [
                {"title": "Regional & Line Insights", "items": [
                    "Total GWP: $1,289.5M | Earned Premium: $1,282.4M | Incurred Losses: $882.0M",
                    "North America: Largest region ($513.3M GWP, 40% share) with 73.8% loss ratio.",
                    "Property Line: Highest claims ($385.2M incurred, 43.7% share of total claims)."
                ]},
                {"title": "Risk Watchlist & Accumulations", "items": [
                    "14 Treaties on Critical Watchlist (Limit Utilisation >= 80%).",
                    "Peak Zone Catastrophe exposure concentrated in Zone NA-CAT1 ($2.1B limit exposure).",
                    "Data Quality: 252 source records quarantined (3.1% of total source transactions)."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "13. Monthly Operational Calendar & SLA",
            "subtitle": "Standard Operating Procedure for the Reinsurance Analytics Team",
            "boxes": [
                {"title": "Monthly Timeline (Work Days 1 to 5)", "items": [
                    "WD 1: Source data extracts received from Systems A, B, and C.",
                    "WD 2: Run pipeline (python python/run_all.py --regen). Inspect DQ log.",
                    "WD 3: Resolve unmapped values via add_mapping.py and re-run pipeline.",
                    "WD 4: Run VBA ValidatePack on Monthly_MI_Pack.xlsx; generate regional packs.",
                    "WD 5: Distribute Monthly_MI_Email.eml draft & publish Power BI / Qlik dashboards."
                ]},
                {"title": "Roles & Responsibilities", "items": [
                    "Data Steward: Owns mapping tables and investigates quarantined records.",
                    "Actuarial Analyst: Reviews loss ratios, combined ratios, and emergence curves.",
                    "Lead Actuary: Signs off monthly MI pack and presents to senior management."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "14. Enhancement Backlog & Future Roadmap",
            "subtitle": "Planned Upgrades for ant-reinsurance-analytics v1.0",
            "boxes": [
                {"title": "Actuarial & Modeling Upgrades", "items": [
                    "1. IBNR / Ultimate Loss Estimates: Adding triangle development & chain-ladder method.",
                    "2. Historical FX Basis: Dynamic FX rate lookup by transaction date.",
                    "3. Treaty Renewal Analytics: Tracking rate changes and lapse rates."
                ]},
                {"title": "Data Infrastructure Upgrades", "items": [
                    "4. PostgreSQL Production Deployment: Migrating core SQLite to PostgreSQL 15.",
                    "5. Automated Email Distribution: Direct SMTP integration for regional MI packs.",
                    "6. Historical Snapshot Store: Month-over-month variance tracking."
                ]}
            ]
        },
        {
            "type": "content",
            "title": "15. Summary & Best Practices for Reinsurance Analysts",
            "subtitle": "Core Principles for Success in AXA XL Reinsurance Portfolio Analytics",
            "boxes": [
                {"title": "Key Takeaways", "items": [
                    "Always verify reconciliation (Source = Core + Quarantined) before sending reports.",
                    "Never modify core formulas in Monthly_MI_Pack.xlsx; use v_treaty_summary view.",
                    "Run VBA ValidatePack macro as your mandatory pre-release audit gate.",
                    "Refer to docs/Data_Dictionary.xlsx and docs/User_Guide.md for metric definitions."
                ]},
                {"title": "Support & Contacts", "items": [
                    "Team: AXA XL Reinsurance Portfolio Analytics (Gurgaon / Global)",
                    "Lead: Corporate Actuarial | Repository: reinsurance-analytics",
                    "Documentation: docs/User_Guide.md | UAT Log: docs/UAT_Test_Plan.md"
                ]}
            ]
        }
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(blank_layout)

        # Header background banner
        header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.2))
        header.fill.solid()
        header.fill.fore_color.rgb = NAVY
        header.line.fill.background()

        # Title text
        tx_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.15), Inches(12.333), Inches(0.9))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = data["title"]
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = WHITE

        if "subtitle" in data:
            p2 = tf.add_paragraph()
            p2.text = data["subtitle"]
            p2.font.size = Pt(14)
            p2.font.color.rgb = RGBColor(200, 220, 255)

        if data["type"] == "title":
            # Extra background shape
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.6), Inches(12.333), Inches(5.3))
            bg.fill.solid()
            bg.fill.fore_color.rgb = LIGHT_BG
            bg.line.color.rgb = TEAL

            tx_body = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.5))
            tf_body = tx_body.text_frame
            tf_body.word_wrap = True
            for b in data["bullets"]:
                p_b = tf_body.add_paragraph()
                p_b.text = "• " + b
                p_b.font.size = Pt(18)
                p_b.font.color.rgb = SLATE
                p_b.space_after = Pt(20)

        elif data["type"] == "content":
            boxes = data["boxes"]
            num_boxes = len(boxes)
            box_width = Inches((12.333 - (0.4 * (num_boxes - 1))) / num_boxes)

            for idx, box in enumerate(boxes):
                left = Inches(0.5 + idx * (box_width.inches + 0.4))
                top = Inches(1.6)
                height = Inches(5.3)

                # Card box shape
                card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, box_width, height)
                card.fill.solid()
                card.fill.fore_color.rgb = WHITE
                card.line.color.rgb = TEAL
                card.line.width = Pt(1.5)

                # Card header bar
                card_hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, box_width, Inches(0.7))
                card_hdr.fill.solid()
                card_hdr.fill.fore_color.rgb = TEAL
                card_hdr.line.fill.background()

                # Card title text
                tx_hdr = slide.shapes.add_textbox(left, top + Inches(0.1), box_width, Inches(0.5))
                p_h = tx_hdr.text_frame.paragraphs[0]
                p_h.text = box["title"]
                p_h.font.size = Pt(16)
                p_h.font.bold = True
                p_h.font.color.rgb = WHITE
                p_h.alignment = PP_ALIGN.CENTER

                # Card bullet items
                tx_items = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.8), box_width - Inches(0.4), height - Inches(0.9))
                tf_items = tx_items.text_frame
                tf_items.word_wrap = True
                for item in box["items"]:
                    p_i = tf_items.add_paragraph()
                    p_i.text = "• " + item
                    p_i.font.size = Pt(13)
                    p_i.font.color.rgb = SLATE
                    p_i.space_after = Pt(12)

    output_pptx = DOCS_DIR / "Reinsurance_Analytics_Training_Deck.pptx"
    prs.save(output_pptx)
    print(f"PowerPoint training deck created at {output_pptx}")

def create_html_presentation():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AXA XL Reinsurance Analytics Training Deck</title>
<style>
    :root {
        --navy: #002060;
        --teal: #008080;
        --dark-slate: #1e293b;
        --light-bg: #f4f6f9;
        --white: #ffffff;
    }
    body {
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        background-color: #0f172a;
        color: var(--dark-slate);
        margin: 0;
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .controls {
        margin-bottom: 15px;
        display: flex;
        gap: 15px;
        align-items: center;
    }
    .controls button {
        background-color: var(--teal);
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
    }
    .controls button:hover {
        background-color: #006666;
    }
    .slide-counter {
        color: white;
        font-size: 16px;
        font-weight: 600;
    }
    .slide-container {
        width: 1000px;
        height: 562.5px; /* 16:9 ratio */
        background-color: var(--light-bg);
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        overflow: hidden;
        position: relative;
    }
    .slide {
        display: none;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
    }
    .slide.active {
        display: block;
    }
    .slide-header {
        background-color: var(--navy);
        color: white;
        padding: 20px 30px;
    }
    .slide-header h1 {
        margin: 0;
        font-size: 24px;
    }
    .slide-header p {
        margin: 5px 0 0 0;
        font-size: 14px;
        color: #93c5fd;
    }
    .slide-body {
        padding: 25px 30px;
        display: flex;
        gap: 20px;
        height: calc(100% - 110px);
        box-sizing: border-box;
    }
    .card {
        flex: 1;
        background: white;
        border-radius: 8px;
        border: 2px solid var(--teal);
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .card-title {
        background-color: var(--teal);
        color: white;
        padding: 12px 15px;
        font-weight: 700;
        font-size: 16px;
        text-align: center;
    }
    .card-content {
        padding: 15px 20px;
        font-size: 14px;
        line-height: 1.6;
    }
    .card-content ul {
        margin: 0;
        padding-left: 20px;
    }
    .card-content li {
        margin-bottom: 10px;
    }
</style>
</head>
<body>
<div class="controls">
    <button onclick="prevSlide()">❮ Previous</button>
    <span class="slide-counter" id="counter">Slide 1 of 15</span>
    <button onclick="nextSlide()">Next ❯</button>
</div>

<div class="slide-container">
    <!-- Slide 1 -->
    <div class="slide active">
        <div class="slide-header">
            <h1>Reinsurance Portfolio Analytics & Data Assurance Platform</h1>
            <p>AXA XL Portfolio Analytics | Global Training & Operational Playbook</p>
        </div>
        <div class="slide-body" style="justify-content: center; align-items: center;">
            <div style="background: white; padding: 40px; border-radius: 12px; border-left: 6px solid var(--teal); max-width: 800px;">
                <h2>Welcome to AXA XL Reinsurance Analytics Training</h2>
                <ul style="font-size: 16px; line-height: 1.8;">
                    <li><b>Single Version of the Truth:</b> Standardized metrics across Underwriting, Actuarial & Management.</li>
                    <li><b>End-to-End Automation:</b> ETL Pipeline, 28 Data Quality Checks, Excel MI Pack, Power BI & Qlik.</li>
                    <li><b>Actuarial Governance:</b> Portfolio Loss Ratio 68.8%, GWP $1.29B, Limit Exposure $8.91B.</li>
                    <li><b>VBA Macro Automation:</b> Pre-release validation and regional pack splitting.</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Slide 2 -->
    <div class="slide">
        <div class="slide-header">
            <h1>1. Program Context & Why This Platform Exists</h1>
            <p>Transitioning from Fragmented Spreadsheets to Governed Reinsurance Analytics</p>
        </div>
        <div class="slide-body">
            <div class="card">
                <div class="card-title">Legacy Challenges</div>
                <div class="card-content">
                    <ul>
                        <li>Manual spreadsheets with broken formulas and mismatched regional totals.</li>
                        <li>Three isolated source systems (Treaties, Claims, Exposure) with duplicates.</li>
                        <li>No audit log for unmapped region or LOB codes.</li>
                        <li>Days spent manually preparing monthly report packs.</li>
                    </ul>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Platform Solution</div>
                <div class="card-content">
                    <ul>
                        <li>Automated ETL pipeline loading a conformed star-schema warehouse.</li>
                        <li>28 automated data quality & reconciliation checks on every load.</li>
                        <li>Governed MI views enforcing single metric definitions.</li>
                        <li>One-click Excel MI pack, VBA validation, Power BI & Qlik apps.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 3 -->
    <div class="slide">
        <div class="slide-header">
            <h1>2. Architecture & Data Governance Flow</h1>
            <p>End-to-End Pipeline from Source Ingestion to Executive Dashboards</p>
        </div>
        <div class="slide-body">
            <div class="card">
                <div class="card-title">1. Ingestion & Staging</div>
                <div class="card-content">
                    <ul>
                        <li>System A (Treaties), System B (Claims), System C (Premium/Exposure).</li>
                        <li>Staged into raw tables without silent data loss.</li>
                        <li>Unmapped values flagged in v_unmapped_values.</li>
                    </ul>
                </div>
            </div>
            <div class="card">
                <div class="card-title">2. 28 Data Quality Checks</div>
                <div class="card-content">
                    <ul>
                        <li>Reconciliation rule: Source = Core + Quarantined.</li>
                        <li>Quarantined rows routed to dq_failed_records.</li>
                        <li>Clean data loaded to dim_treaty, fact_premium, fact_claims.</li>
                    </ul>
                </div>
            </div>
            <div class="card">
                <div class="card-title">3. MI Views & Reports</div>
                <div class="card-content">
                    <ul>
                        <li>v_treaty_summary view locks loss & combined ratio logic.</li>
                        <li>Monthly_MI_Pack.xlsx with VBA macros.</li>
                        <li>Power BI Project (.pbip) & Qlik (.qvs) load scripts.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 4 -->
    <div class="slide">
        <div class="slide-header">
            <h1>3. Excel MI Pack & VBA Macro Automation</h1>
            <p>Operational Guide to Running Monthly_MI_Pack.xlsx & Macros</p>
        </div>
        <div class="slide-body">
            <div class="card">
                <div class="card-title">Excel Pack Layout</div>
                <div class="card-content">
                    <ul>
                        <li><b>Summary:</b> Executive KPIs, regional totals, loss ratios.</li>
                        <li><b>Treaty_Data:</b> 700 treaties with live SUMIFS formulas.</li>
                        <li><b>DQ_Log:</b> Real-time status of 28 data quality checks.</li>
                    </ul>
                </div>
            </div>
            <div class="card">
                <div class="card-title">VBA Macro Suite (ReportMacros.bas)</div>
                <div class="card-content">
                    <ul>
                        <li><b>ValidatePack():</b> Mandatory audit check before releasing pack.</li>
                        <li><b>SplitByRegion():</b> Splits master pack into 6 regional workbooks.</li>
                        <li><b>ExportSummaryPdf():</b> Generates executive PDF summary.</li>
                        <li><b>RefreshPack():</b> Recalculates formulas & updates timestamp.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 5 -->
    <div class="slide">
        <div class="slide-header">
            <h1>4. Power BI Project (.pbip) & DAX Measures</h1>
            <p>Enterprise Business Intelligence Model Architecture</p>
        </div>
        <div class="slide-body">
            <div class="card">
                <div class="card-title">Star Schema Model</div>
                <div class="card-content">
                    <ul>
                        <li>Conformed dim_treaty dimension connecting cedants, regions, LOBs.</li>
                        <li>Fact tables (fact_premium, fact_claims, fact_exposure).</li>
                        <li>dim_date table marked as Date Table for time intelligence.</li>
                    </ul>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Key DAX Measures</div>
                <div class="card-content">
                    <ul>
                        <li><b>Gross Written Premium:</b> SUM(fact_premium[gross_written_premium])</li>
                        <li><b>Loss Ratio:</b> DIVIDE([Incurred Losses], [Earned Premium])</li>
                        <li><b>Combined Ratio:</b> [Loss Ratio] + [Commission Ratio] + 0.05</li>
                        <li><b>Limit Utilisation:</b> DIVIDE([Incurred Losses], SUM(dim_treaty[limit_usd]))</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 6 -->
    <div class="slide">
        <div class="slide-header">
            <h1>5. Qlik Sense Application Architecture</h1>
            <p>QVS Scripting & In-Memory Associative Model</p>
        </div>
        <div class="slide-body">
            <div class="card">
                <div class="card-title">Qlik Load Script (Reinsurance_Analytics.qvs)</div>
                <div class="card-content">
                    <ul>
                        <li>Automated mapping tables (Map_LOB, Map_Region, Map_Currency).</li>
                        <li>Master Calendar script creating fiscal periods.</li>
                        <li>Direct CSV loading from data/core_csv/ directory.</li>
                    </ul>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Qlik Master Items</div>
                <div class="card-content">
                    <ul>
                        <li>Master Measures for Loss Ratio, Earned Premium, Combined Ratio.</li>
                        <li>Executive Overview, Portfolio Risk, LOB, Claims sheets.</li>
                        <li>Associative filtering across underwriters & cedants.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 7 -->
    <div class="slide">
        <div class="slide-header">
            <h1>6. UAT & Quality Assurance Framework</h1>
            <p>39 Automated Regression Tests & Verification Proof</p>
        </div>
        <div class="slide-body">
            <div class="card">
                <div class="card-title">Automated UAT (python/uat_tests.py)</div>
                <div class="card-content">
                    <ul>
                        <li><b>A01-A17:</b> 100% recall on planted error detection.</li>
                        <li><b>B01-B08:</b> Database integrity & reconciliation checks.</li>
                        <li><b>C01-C03:</b> SQL analytical queries & loss ratio agreement.</li>
                        <li><b>D01-D05:</b> Excel pack and HTML dashboard tie-outs.</li>
                    </ul>
                </div>
            </div>
            <div class="card">
                <div class="card-title">VBA & Manual UAT (M01-M05)</div>
                <div class="card-content">
                    <ul>
                        <li><b>M03 ValidatePack Pass:</b> Verified with 16 DQ warnings.</li>
                        <li><b>M04 ValidatePack Fail:</b> Detected GWP mismatch & blocked release.</li>
                        <li><b>M05 SplitByRegion:</b> Created 6 regional files totaling 700 treaties.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 8 -->
    <div class="slide">
        <div class="slide-header">
            <h1>7. Data Governance & Mapping Procedure</h1>
            <p>Adding New Regions, LOBs, and Currencies</p>
        </div>
        <div class="slide-body">
            <div class="card">
                <div class="card-title">Identify Unmapped Values</div>
                <div class="card-content">
                    <ul>
                        <li>Inspect v_unmapped_values view or run Query Q14.</li>
                        <li>Identifies unmapped raw codes arriving from source extracts.</li>
                    </ul>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Execute add_mapping.py</div>
                <div class="card-content">
                    <ul>
                        <li>Run: <code>python python/add_mapping.py lob FIN "Financial Lines"</code></li>
                        <li>Appends row to mapping table with audit timestamp.</li>
                        <li>Next pipeline execution auto-reclassifies quarantined records.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Slide 9 -->
    <div class="slide">
        <div class="slide-header">
            <h1>8. Summary & Next Steps</h1>
            <p>Best Practices for AXA XL Reinsurance Portfolio Analysts</p>
        </div>
        <div class="slide-body" style="justify-content: center; align-items: center;">
            <div style="background: white; padding: 40px; border-radius: 12px; border-left: 6px solid var(--navy); max-width: 800px;">
                <h3>Core Principles for Monthly Reporting</h3>
                <ol style="font-size: 16px; line-height: 1.8;">
                    <li>Always prove reconciliation: Source Premium = Core Premium + Quarantined Premium.</li>
                    <li>Run VBA <code>ValidatePack</code> macro before emailing monthly MI packs.</li>
                    <li>Leverage Power BI & Qlik apps for interactive executive drilldowns.</li>
                    <li>Update mapping tables promptly via <code>add_mapping.py</code>.</li>
                </ol>
            </div>
        </div>
    </div>
</div>

<script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const counter = document.getElementById('counter');

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.toggle('active', i === index);
        });
        counter.textContent = `Slide ${index + 1} of ${slides.length}`;
    }

    function nextSlide() {
        if (currentSlide < slides.length - 1) {
            currentSlide++;
            showSlide(currentSlide);
        }
    }

    function prevSlide() {
        if (currentSlide > 0) {
            currentSlide--;
            showSlide(currentSlide);
        }
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
        if (e.key === 'ArrowLeft') prevSlide();
    });
</script>
</body>
</html>
"""
    output_html = DOCS_DIR / "Reinsurance_Analytics_Training_Deck.html"
    output_html.write_text(html_content, encoding="utf-8")
    print(f"Interactive HTML training presentation created at {output_html}")

if __name__ == "__main__":
    create_pptx()
    create_html_presentation()
