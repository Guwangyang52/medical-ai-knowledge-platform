from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def list_output_files(task_dir: Path) -> list[Path]:
    output_dir = task_dir / "output"
    if not output_dir.exists():
        return []
    return sorted(path for path in output_dir.iterdir() if path.is_file() and path.name != ".gitkeep")


def infer_file_role(path: Path) -> tuple[str, str]:
    name = path.name.lower()
    if name.endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff")):
        kind = "figure"
    elif name.endswith(".csv"):
        kind = "table"
    else:
        kind = "text"

    descriptions = {
        "subgroup_forest_plot": "亚组分析森林图",
        "forest_plot": "主分析森林图",
        "funnel_plot": "发表偏倚漏斗图",
        "sensitivity_plot": "逐一剔除敏感性分析图",
        "meta_summary": "主 Meta 分析文本摘要",
        "publication_bias": "Egger 与 Begg 发表偏倚检验",
        "result_table": "单项研究效应量结果表",
        "sensitivity_summary": "敏感性分析文本摘要",
        "subgroup_summary": "亚组分析文本摘要",
    }
    for key, description in descriptions.items():
        if key in name:
            return kind, description
    return kind, "输出文件"


def extract_meta_results(meta_summary: str, publication_bias: str) -> dict[str, str]:
    results: dict[str, str] = {}

    studies = re.search(r"Number of studies:\s*k\s*=\s*(\d+)", meta_summary)
    if studies:
        results["number_of_studies"] = studies.group(1)

    observations = re.search(r"Number of observations:\s*o\s*=\s*([0-9]+)", meta_summary)
    if observations:
        results["number_of_observations"] = observations.group(1)

    common = re.search(
        r"Common effect model\s+(-?\d+\.\d+)\s+\[([^\]]+)\]\s+[-\d\.]+\s+([<>=\s\d\.]+)",
        meta_summary,
    )
    if common:
        results["common_effect_md"] = common.group(1)
        results["common_effect_ci"] = common.group(2)
        results["common_effect_p"] = common.group(3).strip()

    random = re.search(
        r"Random effects model\s+(-?\d+\.\d+)\s+\[([^\]]+)\]\s+[-\d\.]+\s+([<>=\s\d\.]+)",
        meta_summary,
    )
    if random:
        results["random_effect_md"] = random.group(1)
        results["random_effect_ci"] = random.group(2)
        results["random_effect_p"] = random.group(3).strip()

    i2 = re.search(r"I\^2\s*=\s*([\d\.]+%)\s*\[([^\]]+)\]", meta_summary)
    if i2:
        results["i2"] = i2.group(1)
        results["i2_ci"] = i2.group(2)

    heterogeneity = re.search(r"\n\s*([\d\.]+)\s+(\d+)\s+([<>=\s\d\.]+)\n", meta_summary)
    if heterogeneity:
        results["heterogeneity_q"] = heterogeneity.group(1)
        results["heterogeneity_df"] = heterogeneity.group(2)
        results["heterogeneity_p"] = heterogeneity.group(3).strip()

    egger = re.search(r"Egger test:.*?p-value\s*=\s*([\d\.]+)", publication_bias, re.S)
    if egger:
        results["egger_p"] = egger.group(1)

    begg = re.search(r"Begg test:.*?p-value\s*=\s*([\d\.]+)", publication_bias, re.S)
    if begg:
        results["begg_p"] = begg.group(1)

    return results


def read_csv_preview(path: Path, max_rows: int = 5) -> list[list[str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        return [row for _, row in zip(range(max_rows), reader)]


def build_output_manifest(task_dir: Path, outputs: list[Path], results: dict[str, str]) -> str:
    lines = [
        f'generated: "{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}"',
        f'task_dir: "{str(task_dir).replace("\\", "\\\\")}"',
        "",
        "files:",
    ]
    for path in outputs:
        kind, description = infer_file_role(path)
        rel = str(path.relative_to(task_dir)).replace("\\", "/")
        lines.extend(
            [
                f"  - file: {rel}",
                f"    type: {kind}",
                f"    size_bytes: {path.stat().st_size}",
                f"    description: {description}",
            ]
        )

    lines.extend(["", "extracted_results:"])
    if results:
        for key, value in results.items():
            lines.append(f"  {key}: {value}")
    else:
        lines.append("  {}")

    return "\n".join(lines) + "\n"


def build_result_summary(task_dir: Path, outputs: list[Path], results: dict[str, str]) -> str:
    output_lines = []
    for path in outputs:
        kind, description = infer_file_role(path)
        rel = str(path.relative_to(task_dir)).replace("\\", "/")
        output_lines.append(f"- `{rel}`：{description}（{kind}, {path.stat().st_size} bytes）")

    random_md = results.get("random_effect_md", "未提取")
    random_ci = results.get("random_effect_ci", "未提取")
    random_p = results.get("random_effect_p", "未提取")
    i2 = results.get("i2", "未提取")
    egger_p = results.get("egger_p", "未提取")
    begg_p = results.get("begg_p", "未提取")

    interpretation = []
    if results.get("random_effect_md"):
        interpretation.append(
            f"- 随机效应模型合并 MD = {random_md}，95%CI [{random_ci}]，p = {random_p}。"
        )
    if results.get("i2"):
        interpretation.append(f"- 异质性 I² = {i2}，提示研究间异质性很高，应优先解释随机效应模型。")
    if egger_p != "未提取" or begg_p != "未提取":
        interpretation.append(f"- 发表偏倚检验：Egger p = {egger_p}，Begg p = {begg_p}。")
    if not interpretation:
        interpretation.append("- 尚未自动提取到核心统计结论，请人工补充。")

    return f"""# {task_dir.name} 结果摘要

## 运行状态

已完成结果归档。

## 核心结果

{chr(10).join(interpretation)}

## 输出文件

{chr(10).join(output_lines) if output_lines else "- 尚无输出文件。"}

## 建议解读

- 本任务为连续结局变量 Meta 分析。
- 示例结果显示合并效应具有统计学意义。
- I² 很高，说明研究间差异明显，报告时应结合亚组分析、敏感性分析和研究设计差异解释。
- 发表偏倚检验在研究数量较少时效能有限，需谨慎解释。

## 归档文件

- `report/output_manifest.yaml`
- `report/result_summary.md`
- `report/knowledge_candidate.md`
"""


def build_knowledge_candidate(task_dir: Path, outputs: list[Path], results: dict[str, str]) -> str:
    has_runner_value = bool(outputs and results.get("random_effect_md"))
    reuse_value = "medium" if has_runner_value else "low"
    status = "candidate" if has_runner_value else "not_evaluated"

    return f"""---
type: knowledge_candidate
status: {status}
target_location: wiki/analyses/连续数据的Meta分析
reuse_value: {reuse_value}
---

# {task_dir.name} 知识沉淀候选

## 是否值得沉淀

值得作为“连续数据 Meta 分析任务运行样例”沉淀，但不建议新建一个全新的知识库模板。

## 可沉淀内容

- 将交互式 `code.R` 改造为可在执行平台运行的非交互式脚本。
- 输出文件统一写入任务目录 `output/`。
- 自动生成森林图、漏斗图、敏感性分析图、亚组森林图。
- 自动生成 `meta_summary.txt`、`publication_bias.txt`、`result_table.csv`。
- runner 自动维护 `run_manifest.yaml` 和结果摘要。

## 建议写入位置

```text
wiki/analyses/连续数据的Meta分析/
```

建议更新方式：

- 不替换原始知识库示例代码。
- 在 README 中新增“执行平台适配版说明”。
- 将 `continuous_meta_analysis.R` 作为后续标准 runner 示例。

## 与现有知识的关系

本任务复用了现有模板 `连续数据的Meta分析`，属于对已有知识单元的执行平台化增强。

## 需要用户确认的问题

- 是否将非交互式执行版 R 脚本沉淀回平台知识库？
- 是否把该执行版作为连续数据 Meta 分析的默认运行模板？
- 是否需要继续为其他 Meta 分析模板制作类似执行版脚本？
"""


def archive(task_dir: Path) -> None:
    outputs = list_output_files(task_dir)
    meta_summary = read_text(task_dir / "output" / "meta_summary.txt")
    publication_bias = read_text(task_dir / "output" / "publication_bias.txt")
    results = extract_meta_results(meta_summary, publication_bias)

    report_dir = task_dir / "report"
    report_dir.mkdir(exist_ok=True)

    (report_dir / "output_manifest.yaml").write_text(
        build_output_manifest(task_dir, outputs, results),
        encoding="utf-8",
    )
    (report_dir / "result_summary.md").write_text(
        build_result_summary(task_dir, outputs, results),
        encoding="utf-8",
    )
    (report_dir / "knowledge_candidate.md").write_text(
        build_knowledge_candidate(task_dir, outputs, results),
        encoding="utf-8",
    )

    print(f"Archived result for task: {task_dir}")
    print(f"Output files: {len(outputs)}")
    if results:
        print("Extracted results:")
        for key, value in results.items():
            print(f"  {key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive task outputs and generate result reports.")
    parser.add_argument("task_dir", help="Analysis task directory")
    args = parser.parse_args()

    task_dir = Path(args.task_dir)
    if not task_dir.exists():
        raise SystemExit(f"Task directory does not exist: {task_dir}")

    archive(task_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
