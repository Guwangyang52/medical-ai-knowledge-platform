# 《机器学习及 Python 应用》陈强：神经网络 raw 示例

这个目录用于展示：当用户把一本书或课程配套资料放入 `raw/` 后，如何只抽取其中一个主题，整理成可被 LLM 检索和执行的 wiki 模板。

本开源 starter **不包含原书 PDF、PPT 或配套代码原文**。这些资料可能受版权保护，不适合直接提交到公开 GitHub。

## 本地原始资料对应范围

在用户自己的本地知识库中，可将以下资料放入本目录：

```text
MLPython-PPT-PDF/第15章-人工神经网络.pdf
MLPython_Programs/Chap15_ANN_sklearn.py
MLPython_Programs/Chap15_ANN_keras.py
```

如果用户拥有合法副本，可保留在自己的 `my-vault/raw/` 中；不要上传到公开仓库。

## 开源版保留内容

本目录只保留：

- `原始资料清单.md`：说明本地可放哪些第 15 章材料
- `整理说明.md`：说明如何从 raw 整理到 wiki
- `神经网络章节摘录笔记.md`：不含原文的大纲式摘录和整理线索
- `code/README.md`：说明原代码文件的本地放置方式
- `notes/README.md`：整理备注

对应 wiki 模板位于：

```text
wiki/analyses/Python-神经网络/
```

## 整理原则

- raw 保留原始材料的可追溯线索。
- wiki 只保留可复用知识结构、运行入口和非侵权示例代码。
- 公开 GitHub 中使用合成数据或开源库内置数据。
- 不把整章原文、课件截图、PDF、配套源代码全文复制进 starter。
