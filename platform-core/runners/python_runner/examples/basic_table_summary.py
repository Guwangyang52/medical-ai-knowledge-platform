from __future__ import annotations

import csv
import json
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def numeric_values(rows: list[dict[str, str]], column: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        raw = row.get(column, "").strip()
        if raw == "":
            continue
        try:
            values.append(float(raw))
        except ValueError:
            continue
    return values


def summarize(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "mean": None, "min": None, "max": None}
    return {
        "n": len(values),
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
    }


def main() -> int:
    task_dir = Path.cwd()
    input_path = task_dir / "data" / "sample_table.csv"
    output_dir = task_dir / "output"
    output_dir.mkdir(exist_ok=True)

    rows = read_rows(input_path)
    columns = list(rows[0].keys()) if rows else []
    numeric_summary = {column: summarize(numeric_values(rows, column)) for column in columns}

    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump({"rows": len(rows), "columns": columns, "numeric_summary": numeric_summary}, handle, ensure_ascii=False, indent=2)

    with (output_dir / "summary.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["column", "n", "mean", "min", "max"])
        for column, stats in numeric_summary.items():
            writer.writerow([column, stats["n"], stats["mean"], stats["min"], stats["max"]])

    print(f"Rows: {len(rows)}")
    print(f"Columns: {', '.join(columns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
