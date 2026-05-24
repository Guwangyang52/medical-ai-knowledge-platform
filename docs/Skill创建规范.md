# Skill 创建规范

每个 skill 一个目录：

```text
skill-name/
  SKILL.md
  manifest.yaml
  scripts/
  templates/
  examples/
  tests/
```

从任务到 skill 的推荐流程：

```text
任务运行成功 -> archive_result 生成 knowledge_candidate -> 用户确认 -> 整理 SKILL.md -> 下一次复用
```

