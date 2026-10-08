#!/usr/bin/env python3
"""One command to run the whole platform:  python python/run_all.py [--regen]
   --regen   regenerate the three messy source extracts first (otherwise existing CSVs are reused)
Steps: [generate] -> load/validate/map -> insights -> Excel+e-mail reports -> CSV export -> dashboard -> query docs -> UAT.
Schedule with cron (0 7 1 * *  python /path/python/run_all.py) or Windows Task Scheduler."""
import logging, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
ROOT = Path(__file__).resolve().parents[1]
(ROOT / "logs").mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.FileHandler(ROOT / "logs" / "run_all.log"), logging.StreamHandler()])
log = logging.getLogger("run_all")


def step(name, fn):
    t = time.time(); log.info("START %s", name)
    try:
        r = fn(); log.info("DONE  %s (%.1fs)", name, time.time() - t); return r
    except Exception:
        log.exception("FAILED %s", name); raise SystemExit(f"Pipeline stopped at step: {name} (see logs/run_all.log)")


def main():
    import generate_data, pipeline, insights, build_reports, export_core_csv, build_dashboard, run_queries, build_data_dictionary, uat_tests
    if "--regen" in sys.argv or not (ROOT / "data" / "source" / "sysA_treaties.csv").exists():
        step("generate source extracts", generate_data.main)
    step("load, validate, map, build core + views", pipeline.run_pipeline)
    step("executive insights", insights.build)
    step("Excel packs + e-mail draft", build_reports.main)
    step("export CSVs for Power BI/Qlik", export_core_csv.main)
    step("dashboard", build_dashboard.main)
    step("data dictionary", build_data_dictionary.main)
    step("SQL query documentation", lambda: run_queries.run() and None)
    ok = step("UAT regression tests", uat_tests.main)
    log.info("Run complete. UAT %s", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
