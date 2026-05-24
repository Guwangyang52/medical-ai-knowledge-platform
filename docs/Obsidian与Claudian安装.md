# Obsidian 与 Claudian 安装

本文给新用户一个最小安装路径，帮助他们用 Obsidian 构建出和本项目类似的本地知识库。

## 1. 安装 Obsidian

1. 到 Obsidian 官网下载并安装桌面版。
2. 打开 Obsidian。
3. 选择“打开本地文件夹作为仓库”。
4. 选择 bootstrap 生成的：

```text
my-vault/
```

打开后，先阅读：

```text
首页.md
CLAUDE.md
AGENTS.md
wiki/index.md
```

Claudian 当前主要面向桌面版 Obsidian，建议使用 Obsidian v1.7.2 或更新版本。

## 2. 安装 Claudian

Claudian 是一个把 Claude Code / Codex 等 agent 工作流嵌入 Obsidian vault 的插件。当前可参考：

```text
https://github.com/YishenTu/claudian
https://community.obsidian.md/plugins/realclaudian
```

不同版本安装方式可能略有差异，常见方式如下：

### 方式 A：社区插件安装

1. 打开 Obsidian 设置。
2. 进入“第三方插件”或“Community plugins”。
3. 关闭安全模式。
4. 在社区插件市场搜索 `Claudian`。
5. 安装并启用。

如果社区插件市场中搜不到，使用方式 B。

### 方式 B：手动安装

1. 找到 Claudian 的发布页或 GitHub 仓库。
2. 下载插件文件，通常包括：

```text
main.js
manifest.json
styles.css
```

3. 在 Obsidian vault 中创建插件目录：

```text
my-vault/.obsidian/plugins/claudian/
```

4. 将上述文件放入该目录。
5. 重启 Obsidian。
6. 在“第三方插件”中启用 Claudian。

## 3. 推荐配置

建议把 Claudian 的默认工作范围设为当前 vault，并优先让它读取：

```text
CLAUDE.md
AGENTS.md
wiki/index.md
docs/Claudian整理工作流.md
```

整理 raw 资料时，推荐提示：

```text
请先阅读 CLAUDE.md、AGENTS.md 和 docs/Claudian整理工作流.md。
请把 raw/ 中的新资料整理成 wiki/ 中的结构化知识。
不要改写 raw 原始资料。
不要把未授权 PDF、PPT、书籍原文或真实患者数据写入可公开发布的 wiki。
```

## 4. 与本项目的关系

本项目不强依赖 Claudian。用户也可以使用：

- Codex
- Claude Code
- Claude Desktop
- 其他能读取本地 Markdown 文件的 LLM 工具

Claudian 的价值在于：它可以在 Obsidian 内部帮助用户把 `raw/` 中的资料整理为 `wiki/` 中的 LLM 可读知识。

## 5. 常见问题

如果插件无法安装：

- 确认 Obsidian 已允许社区插件。
- 确认插件目录名和 `manifest.json` 正确。
- 确认插件版本兼容当前 Obsidian。
- 先不用 Claudian，直接用 Codex 或 Claude Code 按本项目文档整理 raw。
