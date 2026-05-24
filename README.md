# Medical AI Knowledge Platform

这是开发者仓库。普通用户请下载 Releases 中的 `MedicalAIKnowledgeWorkspace-v0.1.0.zip` 工作台包。

一个本地优先的医学科研 AI 知识库与执行平台框架。

它的目标不是公开某个人的完整知识库，而是开源一套可复制的系统，让用户下载后能逐步搭建自己的：

```text
raw 原始资料
-> Obsidian / Claudian / LLM 整理
-> wiki 结构化知识
-> Codex / Claude Code 检索调用
-> R / Python 分析任务执行
-> 结果归档
-> 可复用知识或 skill 沉淀
```

当前版本定位：`v0.1.0-alpha`。

## 这是什么

本项目是生成医学科研 AI 知识库工作台的开发者仓库，包含：

- `starter-vault/`：用户工作台的初始 Obsidian 知识库模板。
- `starter-skills/`：用户可继续扩展的 starter skills。
- `execution-platform-template/`：用户工作台的执行平台外壳。
- `platform-core/`：知识检索、任务创建、R/Python runner、归档和 MCP 原型。
- `bootstrap.ps1` / `bootstrap.py`：开发者或高级用户本地初始化脚本。
- `tools/build_user_workspace.ps1`：生成普通用户 Release zip 的打包脚本。

它不是云服务、Web App，也不是某个个人知识库的完整公开备份。

## 普通用户入口

如果你只是想搭建自己的知识库工作台，不建议直接 clone 本开发仓库。

请到 GitHub Releases 下载：

```text
MedicalAIKnowledgeWorkspace-v0.1.0.zip
```

解压后会看到：

```text
MedicalAIKnowledgeWorkspace/
├─ my-vault/
├─ execution-platform/
├─ my-skills/
├─ workspace.code-workspace
├─ start.ps1
└─ README_先打开我.md
```

然后：

1. 双击打开 `workspace.code-workspace`。
2. 用 Obsidian 打开 `my-vault/`。
3. 先阅读 `README_先打开我.md`。
4. 让 Codex 或 Claude Code 先阅读：

```text
my-vault/CLAUDE.md
my-vault/AGENTS.md
my-vault/wiki/index.md
```

## 开发者入口

如果你要修改框架、模板、脚本或参与开发，请 clone 本仓库：

```powershell
git clone git@github.com:Guwangyang52/medical-ai-knowledge-platform.git
cd medical-ai-knowledge-platform
```

开发者可以用 bootstrap 生成本地测试工作台：

```powershell
.\bootstrap.ps1 D:\MyAIKnowledgePlatform
```

也可以生成普通用户 Release 包：

```powershell
.\tools\build_user_workspace.ps1 -Version 0.1.0
```

生成结果：

```text
dist/MedicalAIKnowledgeWorkspace/
dist/MedicalAIKnowledgeWorkspace-v0.1.0.zip
```

推送 `v*` tag 后，GitHub Actions 会自动构建 zip 并附加到对应 GitHub Release。详见 [发布用户工作台](docs/发布用户工作台.md)。

## 当前内置示例

starter vault 当前包含三组 raw/wiki 成对示例：

```text
starter-vault/raw/analyses/连续数据的Meta分析/
starter-vault/wiki/analyses/连续数据的Meta分析/

starter-vault/raw/analyses/网状Meta分析/
starter-vault/wiki/analyses/网状Meta分析/

starter-vault/raw/analyses/Python表格数据摘要/
starter-vault/wiki/analyses/Python表格数据摘要/

starter-vault/raw/analyses/《机器学习及Python应用》陈强-神经网络/
starter-vault/wiki/analyses/Python-神经网络/
```

其中：

- 连续数据 Meta 分析：推荐作为第一个 R 端到端 demo。
- 网状 Meta 分析：展示原始 raw 项目如何整理成 wiki 知识单元，运行前需要额外配置 JAGS / BUGSnet。
- Python 表格数据摘要：展示 Python 项目如何整理成 wiki 模板，并通过 Python runner 执行。
- Python-神经网络：展示机器学习书籍/课程资料如何整理为开源安全的 Python 神经网络模板。

## raw 到 wiki

用户可以直接把原始资料放到：

```text
my-vault/raw/
```

例如：

```text
my-vault/raw/analyses/我的R分析项目/
my-vault/raw/analyses/我的Python分析项目/
my-vault/raw/papers/某篇论文.pdf
```

然后让 Claudian、Claude、Codex 或其他 LLM 按规则整理到：

```text
my-vault/wiki/analyses/
my-vault/wiki/sources/
my-vault/wiki/concepts/
my-vault/wiki/synthesis/
```

参考文档：

- [Claudian整理工作流](docs/Claudian整理工作流.md)
- [用户快速上手](docs/用户快速上手.md)

## 执行平台

执行平台负责临时任务和运行，不负责长期保存知识。

标准流程：

```text
检索模板
-> 创建任务
-> 复制或改写代码
-> 运行 R / Python
-> 归档输出
-> 生成 knowledge_candidate
-> 用户决定是否沉淀
```

核心脚本：

```text
platform-core/scripts/search_kb.py
platform-core/scripts/validate_kb.py
platform-core/scripts/create_analysis_project.py
platform-core/scripts/run_r_task.py
platform-core/scripts/run_python_task.py
platform-core/scripts/archive_result.py
```

Python 任务示例：

```powershell
python .\platform-core\scripts\search_kb.py "Python 表格数据摘要" --json
python .\platform-core\scripts\create_analysis_project.py "python demo" --template-dir "..\my-vault\wiki\analyses\Python表格数据摘要" --copy-template-code --task-id python-demo
Copy-Item "..\my-vault\wiki\analyses\Python表格数据摘要\data\sample_table.csv" ".\projects\python-demo\data\sample_table.csv"
python .\platform-core\scripts\run_python_task.py ".\projects\python-demo" --script "src/analysis.py"
```

任务目录结构：

```text
execution-platform/projects/<task>/
├─ task.md
├─ run_manifest.yaml
├─ data/
├─ src/
├─ output/
├─ report/
└─ logs/
```

## Codex / Claude Code / MCP

本项目支持三种调用方式：

- 规则文件：`CLAUDE.md` 和 `AGENTS.md`
- 直接脚本：`search_kb.py`、`validate_kb.py`、`create_analysis_project.py`、`run_r_task.py`、`run_python_task.py`
- MCP 原型：`platform-core/mcp/medical_research_platform/`

MCP 原型工具：

- `knowledge.search`
- `knowledge.validate`
- `analysis.create_task`
- `analysis.run_r`
- `analysis.run_python`
- `archive.result`

## 文档入口

- [用户快速上手](docs/用户快速上手.md)
- [Obsidian与Claudian安装](docs/Obsidian与Claudian安装.md)
- [Claudian整理工作流](docs/Claudian整理工作流.md)
- [第一个分析执行任务](docs/第一个分析执行任务.md)
- [Codex使用说明](docs/Codex使用说明.md)
- [ClaudeCode使用说明](docs/ClaudeCode使用说明.md)
- [MCP接入说明](docs/MCP接入说明.md)
- [项目开发指南](docs/项目开发指南_v0.2.md)
- [发布用户工作台](docs/发布用户工作台.md)
- [FAQ](docs/FAQ.md)

## 隐私与开源边界

不要提交：

- 真实患者数据
- 私有课题数据
- 未授权 PDF、Word、PPT
- 本地运行任务、日志和输出
- `config/paths.yaml`
- API key、token、账号信息
- RStudio 状态文件，例如 `.Rproj.user/` 或 `.Rhistory`

公开仓库只应包含框架代码、规则文件、文档、可再分发示例、合成数据和 starter 模板。

## 当前 alpha 状态

已具备：

- bootstrap 初始化本地知识库和执行平台
- starter wiki 模板检索
- starter wiki 模板校验
- R runner
- Python runner
- 连续数据 Meta 分析示例
- 网状 Meta 分析示例
- Python 表格数据摘要示例
- MCP 原型

后续计划：

- 官方 MCP SDK 版实现
- 更多医学统计和机器学习模板
- 自动 PDF 解析流水线
- 更完整的 Release 质量检查

## License

MIT License，见 [LICENSE](LICENSE)。
