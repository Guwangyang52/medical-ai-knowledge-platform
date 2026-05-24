# 网状 Meta 分析 raw 项目

这是一个开源安全的原生 raw 材料示例，用来展示多干预比较项目如何从 raw 层整理成 wiki 知识单元。

真实用户使用时，不需要先把 raw 整理成标准格式。可以直接把原始项目放进 `raw/analyses/<项目名>/`，再让 Claudian / Claude / Codex 整理成 wiki。

## 内容

- `README_RAW.md`：解释 raw 原生材料的用法。
- `原始资料清单.md`：说明本地原始项目中哪些内容保留或排除。
- `整理说明.md`：说明本 raw 项目如何生成 wiki。
- `data/nma_sample_data.csv`：arm-based 示例数据，每行代表一个研究中的一个干预组。
- `code/analysis.R`：基于 BUGSnet 的贝叶斯网状 Meta 分析脚本。
- `output/README.md`：输出类型说明。
- `notes/README.md`：整理笔记入口。

## 对应 wiki

```text
wiki/analyses/网状Meta分析/
```

wiki 层会提炼适用场景、数据结构、BUGSnet 工作流、MCMC 参数、SUCRA 排名、league table 和输出解读规则。

## 开源注意

本 starter 不包含原始 PDF、Word 文档、RStudio 状态文件或大体积 TIFF 输出。发布前必须确认数据与代码来源可公开。
