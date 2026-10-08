# Data quality and mapping procedure

Owner: Portfolio Analytics. Applies to every load of Systems A (treaties), B (claims) and C (premium, exposure).

## 1. What happens on every load (`python/pipeline.py`)
1. Source CSVs are loaded untouched into `stg_*` tables (dates parsed to ISO, numbers typed).
2. 28 checks run (`python/dq_checks.py`): completeness, validity, consistency, uniqueness, referential integrity, trend, reconciliation.
3. Every failing record is written to `dq_failed_records` with a **disposition**; every check writes one row to `dq_check_log`.
4. The core load applies dispositions: **Quarantined** rows are not loaded; **Corrected** rows are fixed by rule (incurred = paid + reserve);
   **Loaded as Unmapped / Mapped to Unassigned** rows load under an explicit placeholder so totals still tie; **Flagged** rows load and are reported.
5. Reconciliation checks Z01/Z02 prove `source = core + quarantined` for premium and claims.

## 2. Disposition rules
| Disposition | Used for | Why |
|---|---|---|
| Quarantined | Duplicates, orphans, loss dates outside treaty period, zero/negative premium | Counting them would overstate or misattribute figures |
| Corrected | Incurred not equal to paid + reserve | One unambiguous rule; the correction is logged |
| Loaded as Unmapped / Unassigned | New LOB or status code, blank region or underwriter | Keeps money in the totals but visible as a gap |
| Flagged | Claim above limit, premium differs from estimate, trend breaks | Needs a human decision; may be legitimate |

## 3. Daily/monthly routine for the analyst
1. Run `python python/run_all.py`. Open the **Data quality** dashboard page or `DQ_Log` in the Excel pack.
2. Any **High** severity FAIL: investigate before publishing. Find rows with
   `SELECT * FROM dq_failed_records WHERE check_id = 'V01';`
3. Raise quarantined items with the owning system team (A: underwriting, B: claims, C: finance) and record the answer in the ticket.
4. Check `SELECT * FROM v_unmapped_values;` and follow the mapping change steps below.
5. Do not send the pack if reconciliation (Z01/Z02) fails.

## 4. Mapping change procedure
1. **Detect**: a new source value appears in `v_unmapped_values` (also check V04, V05, V06, V07 in the log).
2. **Confirm** the meaning with the business owner of the source system. Never guess.
3. **Add** the mapping: `python python/add_mapping.py --table lob --source FIN --target "Financial Lines" --by "<your name>"`
   (writes owner and date to `mappings/map_lob.csv`, which is version controlled).
4. **Re-run** the pipeline and **verify**: `v_unmapped_values` is empty and the 'Unmapped' line has no treaties.
5. **Log** the change (ticket reference, who confirmed, date). Automated test E01/E02 in `python/uat_tests.py` replays this procedure.

Worked example in this dataset: eight treaties arrive with LOB code `FIN`. V05 flags them and they load as 'Unmapped' (about $23M premium, visible on the dashboard).
After mapping `FIN` to Financial Lines and re-running, they join Financial Lines.

## 5. Known limitations
- Single valuation-date FX rate for all periods.
- No IBNR: recent underwriting years are understated until claims develop.
- Trend check T01 ignores 2021 (ramp-up of a new portfolio) and uses a 35% month-on-month threshold, set in `pipeline.py`.
