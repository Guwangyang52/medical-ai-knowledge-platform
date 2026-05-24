# Execution Platform Rules

You are working in the execution side of a local AI research platform.

The paired knowledge vault is:

```text
../my-vault/
```

Use the vault for reusable knowledge. Use this execution platform for task work, logs, outputs, runners, and MCP tooling.

## Work Order

1. Read `../my-vault/CLAUDE.md` or `../my-vault/AGENTS.md`.
2. Read `../my-vault/wiki/index.md`.
3. Search `../my-vault/wiki/analyses/*/manifest.yaml`.
4. Prefer reusing a matched wiki analysis template.
5. Create task directories under `projects/`.
6. Copy or adapt template code into `projects/<task>/src/`.
7. Put user task data under `projects/<task>/data/`.
8. Write generated outputs under `projects/<task>/output/`.
9. Write logs under `projects/<task>/logs/`.
10. Write interpretation and promotion notes under `projects/<task>/report/`.

## Standard Task Structure

```text
projects/<task>/
├── task.md
├── run_manifest.yaml
├── data/
├── src/
├── output/
├── report/
└── logs/
```

## Tooling

Core scripts are under:

```text
platform-core/scripts/
```

Recommended calls:

```powershell
python .\platform-core\scripts\search_kb.py "continuous meta analysis" --json
python .\platform-core\scripts\validate_kb.py --json
python .\platform-core\scripts\create_analysis_project.py "demo task"
python .\platform-core\scripts\run_r_task.py ".\projects\<task>"
python .\platform-core\scripts\run_python_task.py ".\projects\<task>" --script "src/analysis.py"
python .\platform-core\scripts\archive_result.py ".\projects\<task>"
```

MCP prototype:

```text
platform-core/mcp/medical_research_platform/
```

## Promotion Boundary

Do not write successful task outputs directly into `../my-vault/wiki/`.

Instead:

1. Generate `report/result_summary.md`.
2. Generate `report/knowledge_candidate.md`.
3. Ask the user whether the candidate should be promoted.
4. Only then update `../my-vault/wiki/` or `../my-skills/`.

## Do Not

- Do not overwrite source data in the vault.
- Do not run temporary analysis inside `../my-vault/wiki/analyses/`.
- Do not hard-code local user paths in reusable scripts.
- Do not promote failed or unreviewed outputs.
