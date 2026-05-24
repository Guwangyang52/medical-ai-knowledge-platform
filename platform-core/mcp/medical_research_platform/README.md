# Medical Research Platform MCP

This is the v0.1 stdio MCP prototype for the local knowledge-driven execution platform.

## Tools

- `knowledge.search`
- `knowledge.validate`
- `analysis.create_task`
- `analysis.run_r`
- `analysis.run_python`
- `archive.result`

## Smoke Test

After running `bootstrap.ps1`, call:

```powershell
$env:MAKP_PATHS_CONFIG = "<YOUR_INSTALL_DIR>\execution-platform\config\paths.yaml"
python "<YOUR_INSTALL_DIR>\execution-platform\platform-core\mcp\medical_research_platform\medical_research_platform_server.py" --call knowledge.search --arguments '{"query":"连续变量 Meta 分析","best":true}'
```

## Client Config

Use `mcp_config.example.json` as a template and replace `<YOUR_INSTALL_DIR>` with your local installation directory.
