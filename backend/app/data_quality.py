from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def profile_csv(path: Path) -> dict[str, Any]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        return {"records": 0, "missing_cells": 0, "duplicate_rows": 0, "warnings": ["empty dataset"]}

    missing = sum(1 for row in rows for value in row.values() if value in {"", None})
    fingerprints = [tuple(sorted(row.items())) for row in rows]
    duplicate_rows = len(fingerprints) - len(set(fingerprints))
    warnings = []
    if missing / max(1, len(rows) * len(rows[0])) > 0.1:
        warnings.append("high missingness")
    if duplicate_rows:
        warnings.append("duplicate records present by design; deduplicate before training")
    return {
        "records": len(rows),
        "missing_cells": missing,
        "duplicate_rows": duplicate_rows,
        "warnings": warnings,
    }


def dataset_quality_summary(data_dir: Path) -> dict[str, Any]:
    csv_paths = sorted(data_dir.glob("*.csv"))
    profiles = {path.stem: profile_csv(path) for path in csv_paths}
    total_records = sum(profile["records"] for profile in profiles.values())
    return {
        "dataset_count": len(profiles),
        "total_records": total_records,
        "profiles": profiles,
        "training_gate": "blocked_if_unreviewed_synthetic_data",
    }

