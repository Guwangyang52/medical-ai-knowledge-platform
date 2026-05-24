from __future__ import annotations

import csv
import json
from pathlib import Path


def main() -> int:
    root = Path.cwd()
    input_path = root / "data" / "sample_table.csv"
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    numeric_columns: dict[str, list[float]] = {}
    for row in rows:
        for key, value in row.items():
            try:
                numeric_columns.setdefault(key, []).append(float(value))
            except (TypeError, ValueError):
                continue

    summary = {
        "n_rows": len(rows),
        "columns": list(rows[0].keys()) if rows else [],
        "numeric_columns": {
            key: {
                "n": len(values),
                "mean": sum(values) / len(values) if values else None,
                "min": min(values) if values else None,
                "max": max(values) if values else None,
            }
            for key, values in numeric_columns.items()
        },
    }

    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated summary for {len(rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
