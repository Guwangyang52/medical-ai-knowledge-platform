from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from platform_config import default_python_path

DEFAULT_PYTHON = default_python_path()


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


def read_task_name(task_dir: Path) -> str:
    task_md = task_dir / "task.md"
    if task_md.exists():
        for line in task_md.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return task_dir.name


def selected_template_block(task_dir: Path) -> str:
    prior = task_dir / "run_manifest.yaml"
    if prior.exists():
        text = prior.read_text(encoding="utf-8", errors="replace")
        marker = "knowledge:\n"
        runtime_marker = "\nruntime:\n"
        if marker in text and runtime_marker in text:
            block = text.split(marker, 1)[1].split(runtime_marker, 1)[0].rstrip()
            if block:
                return block
    return '  selected_template:\n    id: ""\n    title: ""\n    path: ""\n    manifest: ""\n    main_code: ""'


def resolve_executable(executable: Path) -> Path:
    if executable.exists():
        return executable
    if executable == DEFAULT_PYTHON and str(executable).lower() in {"python", "python.exe"}:
        return Path(sys.executable)
    if len(executable.parts) == 1:
        found = shutil.which(str(executable))
        if found:
            return Path(found)
    raise SystemExit(f"Python executable does not exist: {executable}")


def validate_script_path(task_dir: Path, script: str) -> Path:
    script_path = (task_dir / script).resolve()
    task_root = task_dir.resolve()
    try:
        script_path.relative_to(task_root)
    except ValueError as exc:
        raise SystemExit(f"Python script must stay inside the task directory: {script}") from exc
    if not script_path.exists():
        raise SystemExit(f"Python script does not exist: {script_path}")
    if script_path.suffix.lower() != ".py":
        raise SystemExit(f"Python runner expects a .py script: {script_path}")
    return script_path


def parse_env(values: list[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"--env must use KEY=VALUE format: {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"--env key cannot be empty: {item}")
        env[key] = value
    return env


def read_requirements(task_dir: Path, requirements: str) -> list[str]:
    req_path = task_dir / requirements
    if not req_path.exists():
        return []
    packages: list[str] = []
    for raw_line in req_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        packages.append(line)
    return packages


def write_run_manifest(
    task_dir: Path,
    script: str,
    script_args: list[str],
    python_path: Path,
    status: str,
    returncode: int,
    started: str,
    finished: str,
    stdout_path: str,
    stderr_path: str,
    packages: list[str],
) -> None:
    outputs = list_relative_files(task_dir, "output")
    inputs = list_relative_files(task_dir, "data")
    output_lines = "\n".join(f"  - {item}" for item in outputs) if outputs else "  []"
    input_lines = "\n".join(f"  - {item}" for item in inputs) if inputs else "  []"
    package_lines = "\n".join(f"    - {yaml_quote(item)}" for item in packages) if packages else "    []"
    args_lines = "\n".join(f"    - {yaml_quote(item)}" for item in script_args) if script_args else "    []"

    manifest = f"""task_id: {yaml_quote(task_dir.name)}
task_name: {yaml_quote(read_task_name(task_dir))}
status: {status}
returncode: {returncode}
started: {started}
finished: {finished}

knowledge:
{selected_template_block(task_dir)}

runtime:
  language: Python
  script: {yaml_quote(script)}
  script_args:
{args_lines}
  working_directory: {yaml_quote(str(task_dir))}
  python: {yaml_quote(str(python_path))}
  packages:
{package_lines}

inputs:
{input_lines}

outputs:
{output_lines}

logs:
  stdout: {yaml_quote(stdout_path)}
  stderr: {yaml_quote(stderr_path)}

notes:
  - Python runner executed task.
"""
    (task_dir / "run_manifest.yaml").write_text(manifest, encoding="utf-8")


def describe_output(path: Path) -> str:
    name = path.name.lower()
    if name.endswith((".png", ".jpg", ".jpeg", ".svg", ".pdf")):
        return "figure_or_document"
    if name.endswith((".csv", ".tsv", ".xlsx")):
        return "table"
    if name.endswith((".json", ".yaml", ".yml")):
        return "structured_data"
    if name.endswith((".txt", ".md", ".log")):
        return "text"
    return "file"


def write_output_manifest(task_dir: Path) -> None:
    outputs = [task_dir / item for item in list_relative_files(task_dir, "output")]
    files = []
    for path in outputs:
        files.append(
            {
                "file": str(path.relative_to(task_dir)).replace("\\", "/"),
                "type": describe_output(path),
                "size_bytes": path.stat().st_size,
            }
        )
    report_dir = task_dir / "report"
    report_dir.mkdir(exist_ok=True)
    payload = {
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "task_dir": str(task_dir),
        "files": files,
    }
    (report_dir / "output_manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def update_result_summary(task_dir: Path, status: str, started: str, finished: str) -> None:
    outputs = list_relative_files(task_dir, "output")
    output_lines = "\n".join(f"- `{item}`" for item in outputs) if outputs else "- 暂无输出文件。"
    content = f"""# {task_dir.name} 结果摘要

## 运行状态

{status}

## 运行时间

- started: {started}
- finished: {finished}

## 输出文件

{output_lines}

## 结果解释

本文件由 Python runner 自动生成。请结合 `output/` 中的表格、图像、JSON 或文本结果补充医学/统计学解释。
"""
    report_dir = task_dir / "report"
    report_dir.mkdir(exist_ok=True)
    (report_dir / "result_summary.md").write_text(content, encoding="utf-8")


def run_task(
    task_dir: Path,
    script: str,
    python_path: Path,
    script_args: list[str],
    timeout: int,
    env_values: list[str],
    requirements: str,
) -> int:
    validate_script_path(task_dir, script)
    resolved_python = resolve_executable(python_path)

    (task_dir / "logs").mkdir(exist_ok=True)
    (task_dir / "output").mkdir(exist_ok=True)
    (task_dir / "report").mkdir(exist_ok=True)

    stdout_rel = "logs/stdout.log"
    stderr_rel = "logs/stderr.log"
    stdout_path = task_dir / stdout_rel
    stderr_path = task_dir / stderr_rel

    env = os.environ.copy()
    env.update(parse_env(env_values))
    env["PYTHONUNBUFFERED"] = "1"

    command = [str(resolved_python), script, *script_args]
    started = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    timed_out = False
    try:
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(
                command,
                cwd=task_dir,
                stdout=stdout,
                stderr=stderr,
                text=True,
                env=env,
                timeout=timeout if timeout > 0 else None,
            )
        returncode = completed.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        returncode = 124
        with stderr_path.open("a", encoding="utf-8") as stderr:
            stderr.write(f"\nPython runner timed out after {timeout} seconds.\n")

    finished = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    status = "timeout" if timed_out else ("success" if returncode == 0 else "failed")
    packages = read_requirements(task_dir, requirements)
    write_run_manifest(
        task_dir,
        script,
        script_args,
        resolved_python,
        status,
        returncode,
        started,
        finished,
        stdout_rel,
        stderr_rel,
        packages,
    )
    write_output_manifest(task_dir)
    update_result_summary(task_dir, status, started, finished)
    return returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Python analysis task directory.")
    parser.add_argument("task_dir", help="Analysis task directory")
    parser.add_argument("--script", default="src/analysis.py", help="Python script path relative to task dir")
    parser.add_argument("--python", default=str(DEFAULT_PYTHON), help="Path to python executable")
    parser.add_argument("--timeout", type=int, default=0, help="Timeout in seconds, 0 means no timeout")
    parser.add_argument("--env", action="append", default=[], help="Extra environment variable in KEY=VALUE format")
    parser.add_argument("--requirements", default="requirements.txt", help="Requirements file relative to task dir")
    args, script_args = parser.parse_known_args()

    task_dir = Path(args.task_dir)
    if not task_dir.exists():
        raise SystemExit(f"Task directory does not exist: {task_dir}")

    if script_args and script_args[0] == "--":
        script_args = script_args[1:]

    return run_task(
        task_dir,
        args.script,
        Path(args.python),
        script_args,
        args.timeout,
        args.env,
        args.requirements,
    )


if __name__ == "__main__":
    raise SystemExit(main())
