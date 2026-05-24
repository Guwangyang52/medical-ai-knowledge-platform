# 执行平台

这个目录由 `bootstrap.ps1` 或 `bootstrap.py` 生成。

它是项目的“可运行侧”。配套知识库位于：

```text
../my-vault/
```

这个目录用于：

- 检索 wiki 知识模板
- 创建分析任务
- 执行 R / Python 脚本
- 保存日志和输出
- 接入 MCP 工具
- 生成结果归档报告

临时任务应放在 `projects/`，不要直接在 Obsidian vault 的 `wiki/` 里运行。

## Python 示例

```powershell
python .\platform-core\scripts\search_kb.py "Python 表格数据摘要" --json
python .\platform-core\scripts\create_analysis_project.py "python demo" --template-dir "..\my-vault\wiki\analyses\Python表格数据摘要" --copy-template-code --task-id python-demo
Copy-Item "..\my-vault\wiki\analyses\Python表格数据摘要\data\sample_table.csv" ".\projects\python-demo\data\sample_table.csv"
python .\platform-core\scripts\run_python_task.py ".\projects\python-demo" --script "src/analysis.py"
```
