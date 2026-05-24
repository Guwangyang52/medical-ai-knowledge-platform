---
title: 连续数据的Meta分析
problem_type: Meta分析
method: MD/SMD，固定/随机效应模型，metacont
tool: R
package: meta
date: 2026-05-23
tags:
  - meta分析
  - 连续变量
  - MD
  - SMD
  - 发表偏倚
  - 亚组分析
data_source: synthetic_demo
status: complete
---

# 连续数据的 Meta 分析

## 问题背景

连续结局变量（如愈合时间、血压、评分量表等）常用于医学研究。这个模板演示如何用 R 对实验组和对照组的均数、标准差、样本量进行 Meta 分析。

本模板是 GitHub starter 的合成 demo，对应 raw 原始项目：

```text
raw/analyses/连续数据的Meta分析/
```

## 数据格式要求

示例数据：

```text
data/sample_continuous_meta.csv
```

必需列：

| 列名 | 类型 | 说明 |
|---|---|---|
| `First_author` | 字符 | 研究标签或第一作者 |
| `Year` | 数值 | 年份 |
| `n.e` | 整数 | 实验组样本量 |
| `mean.e` | 数值 | 实验组均数 |
| `sd.e` | 数值 | 实验组标准差，必须大于 0 |
| `n.c` | 整数 | 对照组样本量 |
| `mean.c` | 数值 | 对照组均数 |
| `sd.c` | 数值 | 对照组标准差，必须大于 0 |

可选列：

| 列名 | 类型 | 说明 |
|---|---|---|
| `Subgroups` | 字符 | 亚组变量 |

常见转换：

- 只有标准误：`SD = SE * sqrt(n)`。
- 只有 95% CI：`SD = (upper - lower) * sqrt(n) / 3.92`。
- 单位一致时使用 MD，单位不一致时使用 SMD。

## 方法

核心 R 包：

```r
meta
```

核心流程：

```text
读取 data/sample_continuous_meta.csv
→ 检查必需列
→ metacont() 合并连续结局效应量
→ 输出 summary/table/forest/funnel/sensitivity/subgroup
```

主要输出：

- `output/meta_summary.txt`
- `output/result_table.csv`
- `output/forest_plot.png`
- `output/funnel_plot.png`
- `output/publication_bias.txt`
- `output/sensitivity_summary.txt`
- `output/sensitivity_plot.png`
- `output/subgroup_summary.txt`
- `output/subgroup_forest_plot.png`

## 代码运行

在模板目录中可直接运行：

```powershell
Rscript code.R
```

在执行平台中，推荐先创建任务目录，再把模板代码复制到任务目录运行：

```powershell
python ..\..\..\execution-platform\platform-core\scripts\create_analysis_project.py "continuous meta demo"
```

实际路径由 bootstrap 生成的 `config/paths.yaml` 决定。

## 结果解读规则

LLM/Codex/Claude Code 解读结果时应优先关注：

- 合并效应量 MD 或 SMD。
- 95% CI 是否跨 0。
- p 值是否显著。
- I² 异质性大小。
- 敏感性分析方向是否稳定。
- 发表偏倚检验在研究数量较少时要谨慎解释。

I² 简化判断：

```text
I² < 25%      低异质性
I² 25%-75%   中等或较高异质性
I² > 75%     高异质性，优先解释随机效应模型，并考虑亚组或敏感性分析
```

## 新数据适配指南

1. 将用户数据放入任务目录的 `data/`。
2. 保持必需列名一致，或在 `src/analysis.R` 中做列名映射。
3. 单位一致时保留 `sm = "MD"`。
4. 单位不一致时改为 `sm = "SMD"`。
5. 如果没有 `Subgroups` 列，代码会跳过亚组分析。
6. 输出只写入任务目录的 `output/`，不要直接覆盖 wiki 模板输出。

## AI 使用提示

当用户提出“连续变量 Meta 分析”“均数标准差 Meta 分析”“metacont”等需求时，应优先检索并复用本模板。

执行新任务时：

1. 读取本 `README.md` 与 `manifest.yaml`。
2. 在 `execution-platform/projects/` 下创建任务。
3. 复制 `code.R` 到任务的 `src/analysis.R`。
4. 把用户数据放入任务的 `data/`。
5. 运行 R 脚本。
6. 用 `archive_result.py` 归档。
7. 生成 `knowledge_candidate.md`，经用户确认后再沉淀。

## 关联

- raw 原始项目：`raw/analyses/连续数据的Meta分析/`
- 相关概念：`wiki/concepts/Meta分析.md`
- 后续可扩展模板：二分类数据 Meta、单个率 Meta、网状 Meta、剂量反应 Meta。

