# MCP 接入说明

MCP 原型位于：

```text
platform-core/mcp/medical_research_platform/
```

本地 smoke test：

```powershell
python .\platform-core\mcp\medical_research_platform\medical_research_platform_server.py --call knowledge.search --arguments '{"query":"连续变量 Meta 分析","best":true}'
```

正式接入前，先运行 `bootstrap.ps1`，并让客户端使用生成后的本地路径。

