---
title: 网状Meta分析（NMA）
problem_type: Meta分析
method: Bayesian network meta-analysis, BUGSnet
tool: R
package: BUGSnet, dplyr, tidyr, ggplot2, gridExtra
date: 2026-05-23
tags:
  - meta分析
  - NMA
  - Bayesian
  - BUGSnet
  - SUCRA
data_source: public_or_teaching_example
status: complete
---

# 网状 Meta 分析（NMA）

## 问题背景

传统成对 Meta 分析一次只能比较两种干预。网状 Meta 分析（network meta-analysis, NMA）可以同时比较三种或更多干预，并结合直接证据与间接证据估计相对效果。

本模板演示如何使用 R 包 `BUGSnet` 进行贝叶斯网状 Meta 分析。

对应 raw 原始项目：

```text
raw/analyses/网状Meta分析/
```

## 适用场景

- 至少有 3 种可比较干预。
- 多个研究之间形成连通的证据网络。
- 干预、结局、研究对象具有临床可交换性。
- 需要比较治疗排序、SUCRA、league table 或相对效果。

不适合：

- 网络不连通。
- 干预定义不一致。
- 研究对象差异过大，不满足间接比较假设。

## 数据格式要求

示例数据：

```text
data/nma_sample_data.csv
```

每行代表一个研究中的一个干预组（arm-based format）。

必需列：

| 列名 | 说明 |
|---|---|
| `Study` | 研究名称 |
| `Treatment` | 干预名称 |
| `Number.of.patients` | 样本量 |
| `Number.of.remissions` | 缓解人数 |
| `Number.of.relapses` | 复发人数 |
| `Number.of.adverse.event.related.withdrawals` | 不良事件退出人数 |
| `Cumulative.dose.of.steroid_Mean` | 连续结局均值 |
| `Cumulative.dose.of.steroid_SD` | 连续结局标准差 |

关键检查：

- `Study` + `Treatment` 组合应唯一。
- `Treatment` 命名必须一致。
- 证据网络必须连通。
- 连续结局 SD 必须大于 0。

## 环境准备

BUGSnet 依赖 JAGS。首次运行前需要：

1. 安装 JAGS。
2. 安装 R 编译工具链。
3. 安装 R 包：

```r
install.packages(c("remotes", "knitr", "dplyr", "tidyr", "ggplot2", "gridExtra"))
remotes::install_github("audrey-b/BUGSnet@v1.1.0")
```

## 代码逻辑

`code.R` 的主要流程：

```text
读取 data/nma_sample_data.csv
→ 拆分不同结局
→ data.prep() 转换为 BUGSnet 数据对象
→ net.plot() 绘制证据网络
→ nma.model() 设置固定/随机效应模型
→ nma.run() 运行 MCMC
→ nma.fit() 比较模型拟合
→ nma.rank() 计算 SUCRA / rankogram
→ nma.league() 生成 league table
→ nma.forest() 生成相对参照组森林图
```

## 输出解释

重点解释：

- Evidence network：网络是否连通，哪些干预有直接比较。
- DIC：固定效应与随机效应模型拟合比较。
- SUCRA：治疗排序概率，但必须报告不确定性。
- League table：任意两种干预之间的相对效果。
- Forest plot：各干预相对参照组的效果与可信区间。

简化判断：

```text
网络不连通 → 不应强行做排序
MCMC 未收敛 → 不解释排序
SUCRA 高但可信区间宽 → 结论需谨慎
直接证据少 → 强调间接证据不确定性
```

## 新数据适配指南

1. 将用户数据整理为 arm-based format。
2. 保持 `Study`、`Treatment`、样本量、结局列命名清晰。
3. 修改 `reference` 为实际参照干预。
4. 根据结局类型选择：
   - 二分类：`family = "binomial"`，`link = "logit"` 或 `"log"`。
   - 连续：`family = "normal"`，`link = "identity"`。
5. 检查网络连通性后再运行模型。
6. 如模型不稳定，增加 `n.adapt`、`n.burnin`、`n.iter`。

## AI 使用提示

当用户提出“网状 Meta 分析”“NMA”“BUGSnet”“SUCRA”“多干预比较”等需求时，应优先检索并阅读本模板。

执行新任务时：

1. 读取本 `README.md` 与 `manifest.yaml`。
2. 在 `execution-platform/projects/` 下创建任务。
3. 将 `code.R` 复制到任务目录的 `src/analysis.R`。
4. 将用户数据放入任务目录的 `data/`。
5. 运行前检查 JAGS 与 BUGSnet。
6. 输出写入任务目录的 `output/`，不要覆盖 wiki 模板目录。
7. 归档并生成 `knowledge_candidate.md`。

## 关联

- raw 原始项目：`raw/analyses/网状Meta分析/`
- 相关概念：`wiki/concepts/Meta分析.md`
- 相关模板：`wiki/analyses/连续数据的Meta分析/`

