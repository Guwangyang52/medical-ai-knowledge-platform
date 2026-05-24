# 先打开我：医学科研 AI 知识库工作台

这是已经初始化好的用户版工作台，不是开发者源码仓库。

## 第一次使用

1. 双击打开 `workspace.code-workspace`。
2. 在 VS Code 里确认左侧能看到三个目录：
   - `my-vault`：你的 Obsidian / AI 知识库。
   - `execution-platform`：运行分析任务、保存日志和输出。
   - `my-skills`：沉淀你自己的可复用技能。
3. 如果使用 Obsidian，请打开 `my-vault` 这个目录作为 vault。
4. 让 Codex、Claude Code 或其他 AI 助手先阅读：
   - `my-vault/AGENTS.md`
   - `my-vault/CLAUDE.md`
   - `my-vault/wiki/index.md`

## 快速验证

在 VS Code 终端中进入 `execution-platform` 后运行：

```powershell
python .\platform-core\scripts\search_kb.py "连续变量 Meta 分析" --json
```

## 日常使用边界

- 原始资料放入 `my-vault/raw/`。
- 整理后的长期知识放入 `my-vault/wiki/`。
- 临时分析任务放入 `execution-platform/projects/`。
- 任务输出、日志和报告不要直接写进 `my-vault/wiki/`。
- 只有确认某次任务结果可以复用后，再把它沉淀进 `my-vault/wiki/` 或 `my-skills/`。

## 这个工作台和 GitHub 仓库的区别

GitHub 仓库是开发者维护框架、模板、脚本和文档的地方。

这个目录是普通用户真正工作的地方：可以放心放自己的资料、笔记、任务和输出。不要把含有私人资料的工作台直接上传到公开 GitHub。
