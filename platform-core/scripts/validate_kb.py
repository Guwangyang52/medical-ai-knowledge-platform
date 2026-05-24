from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from platform_config import default_analyses_dir

DEFAULT_ANALYSES_DIR = default_analyses_dir()

REQUIRED_MANIFEST_FIELDS = [
    "id",
    "title",
    "type",
    "version",
    "status",
    "reuse_level",
    "problem_type",
    "methods",
    "language",
    "main_code",
    "packages",
    "input_requirements",
    "outputs",
    "ai_usage",
    "tags",
    "updated",
]


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none"}:
        return None
    return value.strip('"').strip("'")


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    pending_key: tuple[int, dict[str, Any], str] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if line.startswith("- "):
            item = parse_scalar(line[2:])
            if not isinstance(parent, list):
                if pending_key is None:
                    continue
                _, pending_parent, key = pending_key
                new_list: list[Any] = []
                pending_parent[key] = new_list
                stack.append((pending_key[0], new_list))
                parent = new_list
            parent.append(item)
            continue

        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value == "":
            new_dict: dict[str, Any] = {}
            if isinstance(parent, dict):
                parent[key] = new_dict
                pending_key = (indent, parent, key)
                stack.append((indent, new_dict))
            continue

        if isinstance(parent, dict):
            parent[key] = parse_scalar(raw_value)
            pending_key = None

    return root


def has_files(path: Path) -> bool:
    return path.exists() and any(item.is_file() for item in path.iterdir())


def validate_project(project_dir: Path) -> dict[str, Any]:
    readme = project_dir / "README.md"
    code_r = project_dir / "code.R"
    code_py = project_dir / "code.py"
    data_dir = project_dir / "data"
    output_dir = project_dir / "output"
    manifest = project_dir / "manifest.yaml"

    missing: list[str] = []
    warnings: list[str] = []

    if not readme.exists():
        missing.append("README.md")
    if not code_r.exists() and not code_py.exists():
        missing.append("code.R or code.py")
    if not data_dir.exists():
        missing.append("data/")
    elif not has_files(data_dir):
        warnings.append("data/ is empty")
    if not output_dir.exists():
        missing.append("output/")
    elif not has_files(output_dir):
        warnings.append("output/ is empty")
    if not manifest.exists():
        missing.append("manifest.yaml")

    manifest_missing_fields: list[str] = []
    manifest_parse_error = ""
    manifest_title = ""
    manifest_id = ""

    if manifest.exists():
        try:
            manifest_data = parse_simple_yaml(manifest)
            manifest_title = str(manifest_data.get("title", ""))
            manifest_id = str(manifest_data.get("id", ""))
            manifest_missing_fields = [
                field for field in REQUIRED_MANIFEST_FIELDS if field not in manifest_data
            ]
            if manifest_missing_fields:
                warnings.append("manifest missing fields: " + ", ".join(manifest_missing_fields))
        except Exception as exc:  # pragma: no cover - defensive CLI behavior
            manifest_parse_error = str(exc)
            warnings.append(f"manifest parse error: {manifest_parse_error}")

    status = "ok"
    if missing:
        status = "missing_required"
    elif warnings:
        status = "warning"

    return {
        "name": project_dir.name,
        "path": str(project_dir),
        "status": status,
        "has_readme": readme.exists(),
        "has_code_r": code_r.exists(),
        "has_code_py": code_py.exists(),
        "has_data": data_dir.exists(),
        "data_has_files": has_files(data_dir) if data_dir.exists() else False,
        "has_output": output_dir.exists(),
        "output_has_files": has_files(output_dir) if output_dir.exists() else False,
        "has_manifest": manifest.exists(),
        "manifest_id": manifest_id,
        "manifest_title": manifest_title,
        "manifest_missing_fields": manifest_missing_fields,
        "missing": missing,
        "warnings": warnings,
    }


def validate(analyses_dir: Path) -> list[dict[str, Any]]:
    return [
        validate_project(project_dir)
        for project_dir in sorted(analyses_dir.iterdir())
        if project_dir.is_dir()
    ]


def summarize(results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total": len(results),
        "ok": sum(1 for item in results if item["status"] == "ok"),
        "warning": sum(1 for item in results if item["status"] == "warning"),
        "missing_required": sum(1 for item in results if item["status"] == "missing_required"),
        "with_manifest": sum(1 for item in results if item["has_manifest"]),
        "without_manifest": sum(1 for item in results if not item["has_manifest"]),
    }


def print_text(results: list[dict[str, Any]]) -> None:
    summary = summarize(results)
    print("Knowledge base validation summary")
    print(f"  total projects: {summary['total']}")
    print(f"  ok: {summary['ok']}")
    print(f"  warning: {summary['warning']}")
    print(f"  missing required: {summary['missing_required']}")
    print(f"  with manifest: {summary['with_manifest']}")
    print(f"  without manifest: {summary['without_manifest']}")
    print()

    for item in results:
        print(f"- {item['name']}: {item['status']}")
        if item["missing"]:
            print(f"  missing: {', '.join(item['missing'])}")
        if item["warnings"]:
            print(f"  warnings: {'; '.join(item['warnings'])}")
        if item["has_manifest"]:
            print(f"  manifest: {item['manifest_id'] or '(id missing)'}")


def write_csv(results: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "name",
        "status",
        "has_readme",
        "has_code_r",
        "has_code_py",
        "has_data",
        "data_has_files",
        "has_output",
        "output_has_files",
        "has_manifest",
        "manifest_id",
        "missing",
        "warnings",
        "path",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in results:
            row = {field: item.get(field, "") for field in fields}
            row["missing"] = "; ".join(item["missing"])
            row["warnings"] = "; ".join(item["warnings"])
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate analysis template structure in the knowledge base.")
    parser.add_argument("--analyses-dir", default=str(DEFAULT_ANALYSES_DIR), help="Path to wiki/analyses")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--csv", help="Write CSV report to this path")
    parser.add_argument("--fail-on-missing", action="store_true", help="Exit with code 1 when required items are missing")
    args = parser.parse_args()

    analyses_dir = Path(args.analyses_dir)
    if not analyses_dir.exists():
        raise SystemExit(f"Analyses directory does not exist: {analyses_dir}")

    results = validate(analyses_dir)
    if args.csv:
        write_csv(results, Path(args.csv))

    if args.json:
        print(json.dumps({"summary": summarize(results), "projects": results}, ensure_ascii=False, indent=2))
    else:
        print_text(results)

    if args.fail_on_missing and any(item["status"] == "missing_required" for item in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
