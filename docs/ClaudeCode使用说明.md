# Claude Code 使用说明

本文说明如何让 Claude Code 使用本项目的知识库与执行平台。

## 1. 推荐工作区

先运行 bootstrap，然后打开：

```text
workspace.code-workspace
```

工作区应同时包含：

- `my-vault`
- `execution-platform`
- `my-skills`

## 2. 项目规则

Claude Code 进入工作区后，先阅读：

```text
my-vault/CLAUDE.md
execution-platform/CLAUDE.md
my-vault/wiki/index.md
```

核心原则：

```text
知识库优先
复用模板优先
临时任务写 execution-platform/projects
成功后生成 knowledge_candidate
用户确认后再沉淀回 wiki 或 skill
```

## 3. 直接脚本调用

在 `execution-platform` 中：

```powershell
python .\platform-core\scripts\search_kb.py "连续变量 Meta 分析" --json
python .\platform-core\scripts\validate_kb.py --json
```

创建任务：

```powershell
python .\platform-core\scripts\create_analysis_project.py "demo task" --template-dir "..\my-vault\wiki\analyses\连续数据的Meta分析" --copy-template-code
```

运行 R：

```powershell
python .\platform-core\scripts\run_r_task.py ".\projects\<task>" --script "src/analysis.R"
```

归档：

```powershell
python .\platform-core\scripts\archive_result.py ".\projects\<task>"
```

## 4. MCP 原型

MCP 原型位于：

```text
execution-platform/platform-core/mcp/medical_research_platform/
```

工具：

- `knowledge.search`
- `knowledge.validate`
- `analysis.create_task`
- `analysis.run_r`
- `archive.result`

配置示例：

```text
execution-platform/platform-core/mcp/medical_research_platform/mcp_config.example.json
```

需要把示例中的安装目录替换为用户自己的本地平台路径，并设置：

```text
MAKP_PATHS_CONFIG=<install-root>\execution-platform\config\paths.yaml
```

## 5. 整理 raw 资料

Claude Code 可用于整理：

- R 分析项目。
- Python 分析项目。
- PDF 文献。
- 混合资料包。

推荐指令：

```text
请先阅读 my-vault/CLAUDE.md 和 docs/Claudian整理工作流.md，
然后整理 my-vault/raw/<路径>，
生成对应的 wiki 知识单元，并更新 wiki/index.md 与 wiki/log.md。
```

## 6. 安全边界

Claude Code 不应：

- 上传真实隐私数据。
- 提交未授权 PDF/PPT/Docx。
- 删除 raw 原始资料。
- 把任务输出直接堆进 wiki。
- 在用户未确认时沉淀候选知识。

