# Python-神经网络

这是一个 Python 神经网络分析模板，用于演示如何把 raw 中的机器学习资料整理成可被 Codex / Claude Code 检索、复制和执行的 wiki 模板。

开源版使用纯 Python 合成数据和最小 MLP 示例，不包含原书 PDF、PPT 或配套代码全文。

## 适用场景

- 医学或科研数据的二分类预测
- 多分类预测的入门模板
- 与逻辑回归、随机森林、SVM 等模型做基线对照
- 将原始 Python 机器学习脚本整理成可复用执行模板

## 方法要点

本模板使用 Python 标准库实现一个最小二分类 MLP。这样用户无需先安装 scikit-learn、TensorFlow 或 Keras，也能跑通执行平台闭环。

更完整的方法解释见：

```text
方法说明.md
```

核心流程：

1. 准备特征矩阵和标签。
2. 划分训练集和测试集。
3. 训练一个单隐藏层神经网络。
4. 输出准确率、混淆矩阵和训练损失。
5. 用户后续可替换为 scikit-learn / Keras 版本。

## 运行入口

```text
code.py
```

在执行平台中创建任务后复制为：

```text
projects/<task>/src/analysis.py
```

运行：

```powershell
python .\platform-core\scripts\run_python_task.py ".\projects\<task>" --script "src/analysis.py"
```

## 输出

```text
output/metrics.json
output/confusion_matrix.csv
output/training_loss.csv
```

Python runner 还会自动生成：

```text
logs/stdout.log
logs/stderr.log
run_manifest.yaml
report/result_summary.md
report/output_manifest.json
```

## 迁移到用户自己的数据

如果用户上传自己的医学数据，LLM 应先确认：

- 结局变量是哪一列
- 是二分类、多分类还是连续结局
- 是否存在缺失值
- 是否有训练/测试集划分要求
- 是否需要类别不平衡处理
- 是否需要可解释性分析
- 是否可以安装 scikit-learn / TensorFlow / Keras 等外部依赖

对于真实医学数据，不要直接提交到公开 GitHub。

## 与原始资料的关系

本模板参考 raw 中“第 15 章神经网络”这一主题线索，但不复制原书 PDF、课件或配套代码全文。

公开版本保留的是：

- 神经网络分析流程
- 可运行的最小示例
- 医学数据适配规则
- scikit-learn / Keras 迁移方向
