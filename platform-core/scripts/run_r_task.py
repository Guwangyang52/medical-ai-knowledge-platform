from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from platform_config import default_rscript_path

DEFAULT_RSCRIPT = default_rscript_path()


def yaml_quote(value: str) -> str:
    if value == "":
        return '""'
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def list_relative_files(base: Path, folder: str) -> list[str]:
    target = base / folder
    if not target.exists():
        return []
    return [
        str(path.relative_to(base)).replace("\\", "/")
        for path in sorted(target.rglob("*"))
        if path.is_file() and path.name != ".gitkeep"
    ]


def write_run_manifest(
    task_dir: Path,
    script: str,
    rscript: Path,
    status: str,
    returncode: int,
    started: str,
    finished: str,
    stdout_path: str,
    stderr_path: str,
) -> None:
    outputs = list_relative_files(task_dir, "output")
    inputs = list_relative_files(task_dir, "data")
    output_lines = "\n".join(f"  - {item}" for item in outputs) if outputs else "  []"
    input_lines = "\n".join(f"  - {item}" for item in inputs) if inputs else "  []"

    prior = task_dir / "run_manifest.yaml"
    selected_template_block = ""
    task_name = task_dir.name
    task_md = task_dir / "task.md"
    if task_md.exists():
        for line in task_md.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                task_name = line[2:].strip()
                break
    if prior.exists():
        text = prior.read_text(encoding="utf-8")
        if task_name == task_dir.name:
            for line in text.splitlines():
                if line.startswith("task_name:"):
                    raw_value = line.split(":", 1)[1].strip()
                    task_name = raw_value.strip('"').replace("\\\\", "\\")
                    break
        marker = "knowledge:\n"
        runtime_marker = "\nruntime:\n"
        if marker in text and runtime_marker in text:
            selected_template_block = text.split(marker, 1)[1].split(runtime_marker, 1)[0].rstrip()

    if not selected_template_block:
        selected_template_block = "  selected_template:\n    id: \"\"\n    title: \"\"\n    path: \"\"\n    manifest: \"\"\n    main_code: \"\""

    manifest = f"""task_id: {yaml_quote(task_dir.name)}
task_name: {yaml_quote(task_name)}
status: {status}
returncode: {returncode}
started: {started}
finished: {finished}

knowledge:
{selected_template_block}

runtime:
  language: R
  script: {yaml_quote(script)}
  working_directory: {yaml_quote(str(task_dir))}
  rscript: {yaml_quote(str(rscript))}
  packages:
    - meta
    - readxl

inputs:
{input_lines}

outputs:
{output_lines}

logs:
  stdout: {yaml_quote(stdout_path)}
  stderr: {yaml_quote(stderr_path)}

notes:
  - P5 R runner executed task.
"""
    prior.write_text(manifest, encoding="utf-8")


def update_result_summary(task_dir: Path, status: str, started: str, finished: str) -> None:
    outputs = list_relative_files(task_dir, "output")
    output_lines = "\n".join(f"- `{item}`" for item in outputs) if outputs else "- 尚无输出文件。"
    content = f"""# {task_dir.name} 结果摘要

## 运行状态

{status}

## 运行时间

- started: {started}
- finished: {finished}

## 输出文件

{output_lines}

## 结果解释

本文件由 P5 runner 自动生成初版摘要。具体统计解释需结合 `output/meta_summary.txt`、森林图、漏斗图和敏感性分析结果进一步撰写。
"""
    (task_dir / "report" / "result_summary.md").write_text(content, encoding="utf-8")


def run_task(task_dir: Path, script: str, rscript: Path) -> int:
    script_path = task_dir / script
    if not script_path.exists():
        raise SystemExit(f"R script does not exist: {script_path}")
    resolved_rscript = rscript
    if not resolved_rscript.exists() and len(resolved_rscript.parts) == 1:
        found = shutil.which(str(resolved_rscript))
        if found:
            resolved_rscript = Path(found)
    if not resolved_rscript.exists():
        raise SystemExit(f"Rscript does not exist: {rscript}")

    (task_dir / "logs").mkdir(exist_ok=True)
    (task_dir / "output").mkdir(exist_ok=True)

    stdout_rel = "logs/stdout.log"
    stderr_rel = "logs/stderr.log"
    stdout_path = task_dir / stdout_rel
    stderr_path = task_dir / stderr_rel

    started = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        completed = subprocess.run(
            [str(resolved_rscript), script],
            cwd=task_dir,
            stdout=stdout,
            stderr=stderr,
            text=True,
        )
    finished = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    status = "success" if completed.returncode == 0 else "failed"
    write_run_manifest(task_dir, script, resolved_rscript, status, completed.returncode, started, finished, stdout_rel, stderr_rel)
    update_result_summary(task_dir, status, started, finished)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an R analysis task directory.")
    parser.add_argument("task_dir", help="Analysis task directory")
    parser.add_argument("--script", default="src/analysis.R", help="R script path relative to task dir")
    parser.add_argument("--rscript", default=str(DEFAULT_RSCRIPT), help="Path to Rscript.exe")
    args = parser.parse_args()

    task_dir = Path(args.task_dir)
    if not task_dir.exists():
        raise SystemExit(f"Task directory does not exist: {task_dir}")

    return run_task(task_dir, args.script, Path(args.rscript))


if __name__ == "__main__":
    raise SystemExit(main())
