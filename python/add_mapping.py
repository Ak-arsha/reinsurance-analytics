#!/usr/bin/env python3
"""Add a mapping row (the 'mapping change procedure').  Example:
   python python/add_mapping.py --table lob --source FIN --target "Financial Lines" --by "A. Analyst"
Then re-run:  python python/run_all.py   (the unmapped-values check should drop to zero)."""
import argparse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {"region": "map_region", "lob": "map_lob", "claim_status": "map_claim_status", "currency": "map_currency"}
SYSTEM = {"region": "A", "lob": "A", "claim_status": "B", "currency": "ALL"}


def add(table, source, target, by, rate=None, root=ROOT):
    f = Path(root) / "mappings" / f"{FILES[table]}.csv"
    lines = f.read_text().splitlines()
    if any(l.split(",")[0].strip().upper() == source.strip().upper() for l in lines[1:]):
        raise SystemExit(f"'{source}' is already mapped in {f.name}")
    today = date.today().isoformat()
    row = f"{source},{target},{rate}," if table == "currency" else f"{source},{target},"
    row += f"{SYSTEM[table]},{today},{by},{today}"
    f.write_text("\n".join(lines) + "\n" + row + "\n")
    return f


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--table", choices=FILES, required=True); a.add_argument("--source", required=True)
    a.add_argument("--target", required=True); a.add_argument("--by", default="Analytics"); a.add_argument("--rate", type=float)
    x = a.parse_args()
    if x.table == "currency" and x.rate is None: raise SystemExit("--rate is required for currency mappings")
    print("Added to", add(x.table, x.source, x.target, x.by, x.rate))
