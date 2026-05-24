# Claudian 整理工作流

本文说明如何用 Obsidian + Claudian + LLM，把 `raw/` 中的原始资料整理成 `wiki/` 中可供 Codex、Claude Code 和 MCP 工具检索复用的结构化知识。

## 1. 工作流目标

本项目的知识库不是单纯存文件，而是把原始资料编译成 LLM 可读、可检索、可复用的知识单元。

核心路径：

```text
my-vault/raw/
→ Claudian / Claude / Codex 阅读与整理
→ my-vault/wiki/
→ execution-platform 调用
→ 成功任务再沉淀回 wiki 或 my-skills
```

## 2. raw 与 wiki 的分工

### raw

`raw/` 保存原始资料。

可以包含：

- 原始 R/Python 脚本。
- 原始数据或可公开示例数据。
- 学习笔记。
- 输出图表。
- 论文笔记或公开资源说明。
- 尚未整理的分析项目。

`raw/` 中的内容不要求一开始就整洁，但必须可追溯。

### wiki

`wiki/` 保存整理后的结构化知识。

其中最重要的是：

```text
wiki/analyses/<项目名>/
```

每个分析知识单元应能回答：

- 这个模板解决什么问题？
- 输入数据需要什么列？
- 代码如何运行？
- 输出结果如何解释？
- 新数据如何适配？
- 原始资料来自哪里？
- AI 下次应如何复用？

## 3. 新资料导入流程

用户把新资料放入：

```text
my-vault/raw/
```

raw 不需要预整理。用户可以直接上传或复制原生资料，系统的任务就是盘点、筛选、清理、抽象，并生成 wiki 版知识。

推荐分析项目结构：

```text
raw/analyses/<项目名>/
├── README.md
├── SOURCE.md
├── data/
├── code/
├── output/
└── notes/
```

最低要求：

- 如果用户已经知道项目内容，建议写 `README.md`。
- 如果准备公开或长期复用，建议写 `SOURCE.md`。
- 如果用户只是临时导入，可以先直接放原始文件，再由 LLM 补齐 README/SOURCE。

常见 raw 输入形态：

```text
raw/analyses/<项目名>/          R/Python/统计分析项目
raw/papers/<论文或主题>/        PDF、文献笔记、图表
raw/sources/<资料主题>/         教程、网页导出、公开数据说明
```

## 4. LLM 整理步骤

当要求 Claudian、Claude 或 Codex 整理某个 raw 项目时，按以下顺序执行。

### Step 1：读取规则

先读：

```text
CLAUDE.md
AGENTS.md
wiki/index.md
```

确认当前知识库已有的分析模板和概念，避免重复创建。

### Step 2：盘点 raw 项目

读取：

```text
raw/analyses/<项目名>/README.md
raw/analyses/<项目名>/SOURCE.md
raw/analyses/<项目名>/data/
raw/analyses/<项目名>/code/
raw/analyses/<项目名>/output/
raw/analyses/<项目名>/notes/
```

输出一个简短判断：

- 分析类型是什么？
- 使用什么语言和包？
- 数据格式是什么？
- 是否可公开？
- 是否已经有对应 wiki？
- 是否需要替换敏感或未授权文件？

### Step 2.1：判断资料类型

按资料类型进入不同整理路径：

| raw 类型 | 目标 wiki |
|---|---|
| R 分析项目 | `wiki/analyses/<项目名>/` |
| Python 分析项目 | `wiki/analyses/<项目名>/` |
| PDF 文献 | `wiki/sources/<文献名>.md` |
| 多篇文献主题 | `wiki/synthesis/<主题>.md`，必要时拆到 `wiki/sources/` |
| 方法学概念 | `wiki/concepts/<概念名>.md` |
| 混合项目 | 先建 `wiki/analyses/`，再补 sources/concepts/synthesis |
```

### Step 3：确定 wiki 目标目录

一般写入：

```text
wiki/analyses/<项目名>/
```

机器学习大项目可拆成多个 wiki 单元，例如：

```text
raw/analyses/机器学习及R应用/
→ wiki/analyses/机器学习-线性模型/
→ wiki/analyses/机器学习-树与集成/
→ wiki/analyses/机器学习-SVM与KNN/
```

### Step 4：创建 wiki 标准结构

```text
wiki/analyses/<项目名>/
├── README.md
├── manifest.yaml
├── code.R 或 code.py
├── data/
└── output/
```

`output/` 可以只放 `README.md`，实际运行输出应放到执行平台任务目录。

### Step 5：编写 README.md

README 必须面向人和 LLM 同时可读。

推荐章节：

```text
问题背景
适用场景
数据格式要求
环境准备
代码逻辑
输出解释
新数据适配指南
AI 使用提示
关联
```

其中“数据格式要求”和“新数据适配指南”尤其重要，因为 Codex/Claude Code 需要据此判断用户新数据是否能复用模板。

### Step 6：编写 manifest.yaml

`manifest.yaml` 用于程序检索。

基本字段：

```yaml
id:
title:
type: analysis_template
version:
status:
reuse_level:
problem_type:
methods:
language:
main_code:
packages:
source:
input_requirements:
outputs:
ai_usage:
links:
tags:
updated:
```

`ai_usage.retrieval_keywords` 要覆盖用户可能说出的自然语言。

例如网状 Meta：

```yaml
ai_usage:
  retrieval_keywords:
    - 网状Meta分析
    - NMA
    - 贝叶斯Meta分析
    - BUGSnet
    - SUCRA
```

### Step 7：整理代码

代码要求：

- 能从 wiki 项目目录相对路径运行。
- 输入默认读 `data/`。
- 输出默认写 `output/`。
- 不写死用户本地绝对路径。
- 不覆盖 raw 原始资料。
- 必要时保留依赖安装说明。

R 项目建议：

- 主脚本命名为 `code.R`。
- 任务执行版复制为 `src/analysis.R`。
- 输出写入 `output/`。

Python 项目建议：

- 主脚本命名为 `code.py`。
- 任务执行版复制为 `src/analysis.py`。
- 依赖写入 README，后续可扩展 `requirements.txt`。
- 输入默认读取 `data/`。
- 输出默认写入 `output/`。

对实际任务，AI 应把模板代码复制到：

```text
execution-platform/projects/<task>/src/
```

不要直接在 wiki 模板目录里运行临时任务。

### Step 8：整理数据和输出

GitHub starter 中优先放：

- 合成 CSV。
- 可公开 CSV。
- 小体积示例数据。
- `output/README.md`。

谨慎放：

- Excel。
- 图片输出。
- 外部教学数据。

不放：

- 未授权 PDF/PPT/Docx。
- 真实患者或课题私有数据。
- 大体积运行输出。
- `.Rhistory`。
- `.Rproj.user/`。

### Step 9：更新索引和日志

更新：

```text
wiki/index.md
wiki/log.md
```

`index.md` 中至少加入：

- wiki 知识单元链接。
- raw 原始项目链接。

`log.md` 中记录：

- 日期。
- 新增或更新了哪个项目。
- 数据是否为合成/公开示例。

### Step 10：补充 concepts

如果 README 中出现重要概念，例如：

```text
[[Meta分析]]
[[贝叶斯分析]]
[[SUCRA]]
```

应检查：

```text
wiki/concepts/
```

若不存在，创建简短概念笔记。不要留下空白概念节点。

## 5. 执行平台衔接

整理完成后，执行平台应能调用 wiki：

```powershell
python .\execution-platform\platform-core\scripts\search_kb.py "网状 Meta 分析" --json
```

命中模板后，AI 创建任务：

```powershell
python .\execution-platform\platform-core\scripts\create_analysis_project.py "NMA demo"
```

任务目录中运行和归档：

```text
execution-platform/projects/<task>/
├── data/
├── src/
├── output/
├── logs/
└── report/
```

如果任务成功并有复用价值，再生成：

```text
report/knowledge_candidate.md
```

用户确认后才写回 `wiki/` 或 `my-skills/`。

## 6. Python 分析项目整理规则

如果用户上传 Python 项目，例如：

```text
raw/analyses/python-survival-demo/
├── main.py
├── data.csv
├── notebook.ipynb
├── figures/
└── notes.md
```

整理为：

```text
wiki/analyses/python-survival-demo/
├── README.md
├── manifest.yaml
├── code.py
├── data/
└── output/
```

README 需说明：

- Python 版本。
- 主要依赖包。
- 输入数据列。
- 运行命令。
- 输出文件。
- notebook 与脚本的关系。
- 如何适配新数据。

manifest 示例：

```yaml
language: Python
main_code: code.py
packages:
  - pandas
  - numpy
  - scikit-learn
input_requirements:
  data_format:
    - csv
  required_columns: []
ai_usage:
  retrieval_keywords:
    - Python
    - survival analysis
    - machine learning
```

如果 raw 中只有 notebook，应尽量提取为可运行 `code.py`，并在 README 中说明 notebook 是原始探索记录。

## 7. PDF 文献整理规则

如果用户上传 PDF 文献，例如：

```text
raw/papers/Zhang_2024_method_paper.pdf
```

整理为：

```text
wiki/sources/Zhang_2024_method_paper.md
```

source 笔记建议结构：

```markdown
---
title:
authors:
year:
journal:
doi:
tags:
  - source
---

# 标题

## 这篇文献解决什么问题

## 研究设计 / 方法

## 关键结果

## 可复用知识

## 关联概念

## 关联分析模板

## 原始文件

raw/papers/...
```

如果 PDF 与某个分析模板直接相关，应同时更新：

- `wiki/sources/`
- `wiki/concepts/`
- `wiki/analyses/<相关模板>/README.md` 的来源或背景说明
- `wiki/index.md`
- `wiki/log.md`

如果上传的是多篇文献组成的主题包，应先生成多个 `wiki/sources/*.md`，再生成：

```text
wiki/synthesis/<主题>.md
```

## 8. 混合资料整理规则

有些 raw 项目会同时包含：

- PDF 文献。
- R/Python 代码。
- Excel/CSV 数据。
- 输出图片。
- Word 笔记。

整理顺序：

1. 先识别项目主目标：是分析模板、文献资料、还是主题综述。
2. 分析模板写入 `wiki/analyses/`。
3. 文献写入 `wiki/sources/`。
4. 方法概念写入 `wiki/concepts/`。
5. 跨文献或跨项目总结写入 `wiki/synthesis/`。
6. 在各页面之间建立链接。

## 9. Claudian 提示词模板

可以在 Claudian、Claude Code 或 Codex 中使用：

```text
请按照本知识库的 CLAUDE.md / AGENTS.md 规则，整理 raw/<路径>/。

要求：
1. 先盘点 raw 中所有文件，判断资料类型：R/Python 分析项目、PDF 文献、主题资料或混合项目。
2. 如果是分析项目，生成或更新 wiki/analyses/<项目名>/。
3. 如果是 PDF 文献，生成或更新 wiki/sources/<文献名>.md。
4. 如果是方法概念，生成或更新 wiki/concepts/<概念名>.md。
5. 如果是主题资料，生成或更新 wiki/synthesis/<主题>.md。
6. 对分析项目，写 README.md、manifest.yaml、code.R/code.py、data/、output/README.md。
7. 对文献资料，提取题名、作者、年份、期刊、DOI、问题、方法、结果、可复用知识和关联概念。
8. 更新 wiki/index.md 和 wiki/log.md。
9. 不要复制未授权 PDF/PPT/Docx 到公开 starter，不要上传真实隐私数据。
```

## 10. 质量检查清单

整理完成后检查：

```text
[ ] raw 项目有 README.md
[ ] raw 项目有 SOURCE.md
[ ] wiki 项目有 README.md
[ ] wiki 项目有 manifest.yaml
[ ] wiki 项目有 code.R 或 code.py
[ ] data 说明清楚
[ ] output 说明清楚
[ ] wiki/index.md 已更新
[ ] wiki/log.md 已更新
[ ] concepts 无空白节点
[ ] search_kb.py 能检索到
[ ] validate_kb.py 能通过
[ ] 没有硬编码本地路径
[ ] 没有未授权大文件或隐私数据
```
