from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from platform_config import default_projects_dir

DEFAULT_PROJECTS_DIR = default_projects_dir()


def slugify(value: str) -> str:
    value = value.strip()
    value = re.sub(r'[<>:"/\\|?*\r\n\t]+', "-", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "analysis-task"


def repair_windows_mojibake(value: str) -> str:
    """Repair UTF-8 text that arrived as cp1252/latin1 mojibake.

    Some Windows PowerShell-to-Python paths can pass Chinese arguments as text
    like "è¿žç»­..." instead of "连续...". Keep this narrow and best-effort so
    normal input is left untouched.
    """
    if not value:
        return value
    mojibake_markers = ("Ã", "Â", "ä", "å", "æ", "ç", "è", "é", "Ò", "Ñ", "Ê", "Ð")
    if not any(marker in value for marker in mojibake_markers):
        return value
    for encoding in ("latin1", "cp1252"):
        try:
            repaired = value.encode(encoding).decode("utf-8")
        except UnicodeError:
            continue
        if repaired != value:
            return repaired
    return value


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


def template_info(template_dir: str) -> dict[str, str]:
    if not template_dir:
        return {"id": "", "title": "", "path": "", "manifest": "", "main_code": ""}

    template_path = Path(template_dir)
    manifest_path = template_path / "manifest.yaml"
    info = {
        "id": "",
        "title": template_path.name,
        "path": str(template_path),
        "manifest": str(manifest_path) if manifest_path.exists() else "",
        "main_code": "",
    }
    if manifest_path.exists():
        manifest = parse_simple_yaml(manifest_path)
        info["id"] = str(manifest.get("id", ""))
        info["title"] = str(manifest.get("title", info["title"]))
        info["main_code"] = str(manifest.get("main_code", ""))
    return info


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def yaml_quote(value: str) -> str:
    if value == "":
        return '""'
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_task_md(
    task_id: str,
    task_name: str,
    description: str,
    info: dict[str, str],
    created: str,
) -> str:
    matched_template = yaml_quote(info["title"]) if info["path"] else '""'
    return f"""---
task_id: {task_id}
type: analysis_task
status: draft
created: {created}
knowledge_hit: {"true" if info["path"] else "false"}
matched_template: {matched_template}
---

# {task_name}

## 用户原始需求

{description or "待补充。"}

## 分析目标

待补充。

## 数据位置

```text
data/
```

## 命中的知识库模板

```text
{info["path"] or "未指定。"}
```

## 执行计划

1. 检查输入数据。
2. 参考命中的知识库模板。
3. 在 `src/` 中编写或改写分析代码。
4. 将结果输出到 `output/`。
5. 将运行日志写入 `logs/`。
6. 在 `report/` 中整理结果解释和沉淀建议。

## 用户确认事项

- 输入数据是否已经放入 `data/`。
- 是否复用上述知识库模板。
- 是否需要将成功流程沉淀回知识库。
"""


def build_run_manifest(
    task_id: str,
    task_name: str,
    info: dict[str, str],
    created: str,
) -> str:
    return f"""task_id: {yaml_quote(task_id)}
task_name: {yaml_quote(task_name)}
status: draft
created: {created}
started:
finished:

knowledge:
  selected_template:
    id: {yaml_quote(info["id"])}
    title: {yaml_quote(info["title"])}
    path: {yaml_quote(info["path"])}
    manifest: {yaml_quote(info["manifest"])}
    main_code: {yaml_quote(info["main_code"])}

runtime:
  language:
  script:
  working_directory: .
  packages: []

inputs: []
outputs: []

logs:
  stdout: logs/stdout.log
  stderr: logs/stderr.log

notes:
  - P4 created task scaffold.
"""


def build_result_summary(task_name: str) -> str:
    return f"""# {task_name} 结果摘要

## 运行状态

尚未运行。

## 主要结果

待补充。

## 输出文件

待补充。

## 结果解释

待补充。
"""


def build_knowledge_candidate(task_name: str) -> str:
    return f"""---
type: knowledge_candidate
status: not_evaluated
target_location:
reuse_value:
---

# {task_name} 知识沉淀候选

## 是否值得沉淀

待评估。

## 可沉淀内容

待补充。

## 建议写入位置

待补充。

## 与现有知识的关系

待补充。

## 需要用户确认的问题

待补充。
"""


def create_project(args: argparse.Namespace) -> Path:
    args.name = repair_windows_mojibake(args.name)
    args.description = repair_windows_mojibake(args.description)
    args.template_dir = repair_windows_mojibake(args.template_dir)
    args.task_id = repair_windows_mojibake(args.task_id)
    args.date = repair_windows_mojibake(args.date)

    created = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    date_prefix = args.date or datetime.now().strftime("%Y-%m-%d")
    task_slug = slugify(args.name)
    task_id = args.task_id or f"{date_prefix}_{task_slug}"

    projects_dir = Path(args.projects_dir)
    project_dir = projects_dir / task_id
    if project_dir.exists() and not args.force:
        raise SystemExit(f"Project already exists: {project_dir}. Use --force to reuse it.")

    for subdir in ["data", "src", "output", "report", "logs"]:
        (project_dir / subdir).mkdir(parents=True, exist_ok=True)

    info = template_info(args.template_dir)

    write_text(project_dir / "task.md", build_task_md(task_id, args.name, args.description, info, created))
    write_text(project_dir / "run_manifest.yaml", build_run_manifest(task_id, args.name, info, created))
    write_text(project_dir / "report" / "result_summary.md", build_result_summary(args.name))
    write_text(project_dir / "report" / "knowledge_candidate.md", build_knowledge_candidate(args.name))
    write_text(project_dir / "logs" / ".gitkeep", "")
    write_text(project_dir / "data" / ".gitkeep", "")
    write_text(project_dir / "src" / ".gitkeep", "")
    write_text(project_dir / "output" / ".gitkeep", "")

    if args.copy_template_code and info["path"] and info["main_code"]:
        source_code = Path(info["path"]) / info["main_code"]
        if source_code.exists():
            target_name = "analysis" + source_code.suffix
            (project_dir / "src" / target_name).write_text(source_code.read_text(encoding="utf-8"), encoding="utf-8")

    return project_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a standard analysis task directory.")
    parser.add_argument("name", help="Task name")
    parser.add_argument("--description", default="", help="Original user request or task description")
    parser.add_argument("--projects-dir", default=str(DEFAULT_PROJECTS_DIR), help="Target projects directory")
    parser.add_argument("--template-dir", default="", help="Matched knowledge template directory")
    parser.add_argument("--task-id", default="", help="Custom task id / directory name")
    parser.add_argument("--date", default="", help="Date prefix, default today, format YYYY-MM-DD")
    parser.add_argument("--copy-template-code", action="store_true", help="Copy template main_code into src/analysis.*")
    parser.add_argument("--force", action="store_true", help="Allow writing into an existing task directory")
    args = parser.parse_args()

    project_dir = create_project(args)
    print(f"Created analysis project: {project_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
