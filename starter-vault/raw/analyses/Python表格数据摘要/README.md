# Python 表格数据摘要 raw 示例

这个目录模拟用户直接放入 `raw/` 的一个原生 Python 小项目。

它的作用不是提供复杂统计模型，而是展示系统如何把一个 Python 脚本项目整理成可被 LLM 检索和执行的平台模板。

## 原始材料

- `code/analysis.py`：原始 Python 分析脚本
- `data/sample_table.csv`：示例表格数据
- `notes/README.md`：用户备注
- `output/README.md`：原项目输出说明

## 整理目标

Claudian / Codex / Claude Code 可以把这个 raw 项目整理为：

```text
wiki/analyses/Python表格数据摘要/
```

整理后应包含：

- `README.md`
- `manifest.yaml`
- `code.py`
- `data/sample_table.csv`
- `output/README.md`

## 用户替换方式

用户可以把自己的 Python 项目直接放到 `raw/analyses/<项目名>/`，保留原始目录结构。

整理时不要直接改 raw 原始材料，而是在 wiki 中生成结构化版本。
