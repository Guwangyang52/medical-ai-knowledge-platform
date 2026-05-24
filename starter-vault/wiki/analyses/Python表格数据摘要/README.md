# Python 表格数据摘要

这是一个 Python 分析模板，用于演示如何把 raw 中的 Python 小项目整理成可被 Codex / Claude Code 检索、复制和执行的 wiki 模板。

## 适用场景

- 用户上传的是 Python 脚本项目
- 输入是 CSV / TSV / Excel 等表格数据
- 需要先做数据结构检查、描述性统计或轻量数据摘要
- 后续可以扩展为机器学习、回归建模、生存分析或可视化任务

## 输入数据

示例数据：

```text
data/sample_table.csv
```

推荐最小要求：

- 第一行为列名
- 每一行代表一个样本或观测
- 数值列可以被 Python 转换为 `float`
- 分类变量可以保留为字符串

## 运行入口

```text
code.py
```

在执行平台中创建任务后，复制为：

```text
projects/<task>/src/analysis.py
```

然后运行：

```powershell
python .\platform-core\scripts\run_python_task.py ".\projects\<task>" --script "src/analysis.py"
```

## 输出

脚本会写入：

```text
output/summary.json
```

Python runner 还会自动维护：

```text
logs/stdout.log
logs/stderr.log
run_manifest.yaml
report/result_summary.md
report/output_manifest.json
```

## LLM 使用建议

当用户上传 Python 项目时，先做以下判断：

1. 找到主入口脚本，例如 `main.py`、`analysis.py`、`train.py`、`notebook.ipynb`。
2. 识别输入数据位置和文件格式。
3. 识别依赖包，例如 `requirements.txt`、`pyproject.toml`、`environment.yml`。
4. 把可复用逻辑整理成 wiki 模板的 `code.py`。
5. 把用户任务运行放在 execution-platform 的 `projects/<task>/`，不要在 wiki 里直接运行。

如果项目包含隐私数据、真实患者数据或未授权数据，不要放入 GitHub starter。
