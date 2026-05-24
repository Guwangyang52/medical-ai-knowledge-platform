# 网状 Meta 分析原生 raw 材料示例

这个目录模拟用户直接丢进 `raw/analyses/` 的原始分析项目。

raw 不要求一开始就是标准结构。真实使用时，用户可以直接放入：

- R 脚本。
- Python 脚本。
- Excel/CSV 数据。
- Word 笔记。
- PDF 文献。
- 输出图片。
- RStudio/Python 项目文件。
- 临时说明文档。

GitHub starter 不能包含未授权 PDF、Word 文档、大体积输出图或本地缓存文件，所以本示例是“开源安全的原生 raw 模拟版”。

## 本示例包含

- `code/analysis.R`
- `data/nma_sample_data.csv`
- `原始资料清单.md`
- `整理说明.md`
- `output/README.md`
- `notes/README.md`
- `SOURCE.md`

## 用户自己的 raw 可以更乱

你不需要先手动整理成 wiki 格式。可以直接把原始项目放到：

```text
my-vault/raw/analyses/<项目名>/
```

然后让 Claudian / Claude / Codex 执行：

```text
请按照 docs/Claudian整理工作流.md 整理 raw/analyses/<项目名>/，
生成 wiki/analyses/<项目名>/。
```

整理后的标准知识单元应该出现在：

```text
my-vault/wiki/analyses/<项目名>/
```

