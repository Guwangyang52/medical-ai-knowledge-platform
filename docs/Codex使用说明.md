# Codex 使用说明

本文说明如何让 Codex 在本项目中调用知识库和执行平台。

## 1. 打开工作区

运行 bootstrap 后，用 VS Code 或 Codex 打开：

```text
workspace.code-workspace
```

确保工作区包含：

- `my-vault`
- `execution-platform`
- `my-skills`

## 2. 先读规则

让 Codex 先读取：

```text
my-vault/AGENTS.md
my-vault/CLAUDE.md
execution-platform/CLAUDE.md
my-vault/wiki/index.md
```

这些文件定义了：

- raw 与 wiki 的边界。
- 如何检索分析模板。
- 临时任务写到哪里。
- 结果如何归档。
- 何时允许沉淀回 wiki 或 skill。

## 3. 检索知识库

在 `execution-platform` 中运行：

```powershell
python .\platform-core\scripts\search_kb.py "连续变量 Meta 分析" --json
python .\platform-core\scripts\search_kb.py "网状 Meta 分析 BUGSnet SUCRA" --json
```

Codex 应优先复用检索命中的模板，而不是从零生成代码。

## 4. 校验知识库

```powershell
python .\platform-core\scripts\validate_kb.py --json
```

如果模板缺少 `README.md`、`manifest.yaml`、`code.R/code.py`、`data/` 或 `output/`，应先补齐结构。

## 5. 创建执行任务

```powershell
python .\platform-core\scripts\create_analysis_project.py "my analysis task" --template-dir "..\my-vault\wiki\analyses\连续数据的Meta分析" --copy-template-code
```

任务目录会生成在：

```text
execution-platform/projects/
```

## 6. 运行与归档

R 任务：

```powershell
python .\platform-core\scripts\run_r_task.py ".\projects\<task>" --script "src/analysis.R"
```

归档：

```powershell
python .\platform-core\scripts\archive_result.py ".\projects\<task>"
```

## 7. 整理 raw 到 wiki

如果用户新增了 raw 项目，例如：

```text
my-vault/raw/analyses/my-python-project/
```

可以让 Codex 执行：

```text
请按照 docs/Claudian整理工作流.md 和 my-vault/AGENTS.md，
整理 my-vault/raw/analyses/my-python-project/，
生成或更新 my-vault/wiki/analyses/my-python-project/。
```

如果用户新增 PDF：

```text
my-vault/raw/papers/paper.pdf
```

可以让 Codex 执行：

```text
请按照 docs/Claudian整理工作流.md 整理这篇 PDF，
生成 my-vault/wiki/sources/<文献名>.md，
必要时补充 concepts 和 synthesis。
```

## 8. 注意事项

- 不要把临时任务输出直接写入 `my-vault/wiki/`。
- 不要覆盖 raw 原始资料。
- 不要提交 `execution-platform/projects/`。
- 不要提交 `config/paths.yaml`。
- 用户确认后才沉淀 `knowledge_candidate.md`。

