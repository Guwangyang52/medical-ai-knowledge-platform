# FAQ

## 这是一个完整医学知识库吗？

不是。它是一个框架和 starter 系统，包含少量公开/合成示例，方便用户搭建自己的本地知识库。

## 我可以把私有数据放进 raw 吗？

可以，但只限你的本地私有 vault。不要把私有数据上传到公开 GitHub 仓库。

## raw 需要先整理干净吗？

不需要。`raw/` 可以放原生材料。Claudian、Claude 或 Codex 的任务就是帮助你检查、整理，并编译成 `wiki/`。

## raw 和 wiki 有什么区别？

`raw/` 是原始资料层。`wiki/` 是整理后的结构化知识层，方便人和 LLM 查阅、检索、复用。

## execution-platform 是干什么的？

它负责运行真实任务，让临时输出、日志和报告不要污染 Obsidian 知识库。

## 支持 Python 项目吗？

文档已经支持 Python raw 项目，并建议整理为 `wiki/analyses/<project>/code.py`。完整 Python runner 自动化还在 alpha 后续计划中。

## 支持 PDF 文献吗？

工作流支持把 PDF 文献整理为 `wiki/sources/` 笔记。自动 PDF 解析流水线尚未实现。

## 为什么 starter 示例不直接放 PDF 和 Word？

很多论文、书籍和教程不能随意再分发。公开 starter 应尽量使用合成数据或明确授权的公开材料。

## 网状 Meta 分析能开箱即跑吗？

通常不能。它需要 JAGS 和 BUGSnet。当前网状 Meta 示例主要用于展示 raw/wiki 结构和整理方式。

## 第一步应该运行什么？

先运行：

```powershell
.\bootstrap.ps1
```

然后打开 `workspace.code-workspace`，阅读 `my-vault/CLAUDE.md`，再运行：

```powershell
python .\execution-platform\platform-core\scripts\search_kb.py "连续变量 Meta 分析" --json
```

