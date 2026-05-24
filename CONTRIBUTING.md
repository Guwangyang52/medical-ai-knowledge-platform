# 贡献指南

感谢你愿意改进 Medical AI Knowledge Platform。

本项目目前是 alpha 阶段，目标是构建本地 AI 可读科研知识库与执行平台。

## 可以贡献什么

欢迎贡献：

- 新的 starter 模板。
- 更安全的 bootstrap 初始化逻辑。
- 更清晰的用户文档。
- R/Python runner 改进。
- MCP 接入改进。
- 知识库校验脚本。
- 合成 demo 数据。

## 隐私规则

请不要贡献：

- 真实患者数据。
- 私有课题数据。
- 未授权 PDF、Word、PPT。
- API key、token、账号信息或本地绝对路径。
- 大体积运行输出。
- `.Rproj.user/`、`.Rhistory` 等本地状态文件。

如果新增 raw 示例，请加入 `SOURCE.md`，说明来源、授权和是否允许再分发。

## 模板要求

每个 `wiki/analyses/<template>/` 建议包含：

```text
README.md
manifest.yaml
code.R 或 code.py
data/
output/
```

每个可复用 `raw/analyses/<project>/` 建议包含：

```text
README.md 或 README_RAW.md
SOURCE.md
data/
code/
output/
notes/
```

## 提交前检查

运行：

```powershell
python .\platform-core\scripts\validate_kb.py --json
python .\platform-core\scripts\search_kb.py "continuous meta analysis" --json
```

扫描敏感内容：

```powershell
rg -n "paths.yaml|C:\\Users|F:\\|api_key|token" .
Get-ChildItem -Recurse -Include *.pdf,*.docx,*.pptx,.Rhistory
```

## 开发风格

- 文档优先清楚。
- 路径优先使用相对路径或配置。
- 示例尽量小、可检查。
- 授权不清的数据用合成数据替代。
- 不提交本地执行输出。

