# Medical AI Knowledge Vault Rules

You are working inside a local AI-readable research knowledge vault.

This vault has two layers:

```text
raw/   original source material
wiki/  structured knowledge compiled for humans and LLMs
```

The paired execution platform lives next to this vault after bootstrap:

```text
../execution-platform/
```

## Core Principle

Do not treat this vault as a scratch directory. Use `raw/` for source material, `wiki/` for curated reusable knowledge, and `execution-platform/projects/` for temporary analysis tasks.

## Query Workflow

When the user asks a research or analysis question:

1. Read `wiki/index.md` first.
2. Search `wiki/analyses/*/manifest.yaml`.
3. For a likely match, read the matched `README.md`, `manifest.yaml`, and `code.R` or `code.py`.
4. Prefer adapting an existing template over generating a new analysis from scratch.
5. If execution is needed, create or use a task under `../execution-platform/projects/`.
6. Keep outputs, logs, and temporary reports inside the task directory.
7. Only propose changes to `wiki/` after the task succeeds and the user confirms the result is reusable.

## Ingest Workflow

When the user adds new source material:

1. Put original papers, datasets, scripts, screenshots, and notes under `raw/`.
2. Keep raw material readable and traceable. Do not delete or overwrite it casually.
3. For analysis projects, use `raw/analyses/<project-name>/`.
4. Each public or reusable raw project should include `README.md` and `SOURCE.md`.
5. Read all relevant raw material before creating wiki content.
6. Compile the reusable knowledge into `wiki/analyses/<project-name>/`.
7. Update `wiki/index.md` and `wiki/log.md`.

## raw -> wiki Compilation

When compiling `raw/analyses/<project-name>/` into `wiki/analyses/<project-name>/`, create:

```text
README.md
manifest.yaml
code.R or code.py
data/
output/
```

The wiki `README.md` should include:

- Problem background.
- Applicable scenarios.
- Input data requirements.
- Code logic.
- Output interpretation.
- Common errors.
- Adaptation guide for new data.
- Link or path to the raw source project.

The `manifest.yaml` is for programmatic search by Codex, Claude Code, and MCP tools.

## Execution Boundary

Temporary work belongs in:

```text
../execution-platform/projects/<task>/
```

Use this task structure:

```text
task.md
run_manifest.yaml
data/
src/
output/
report/
logs/
```

Do not run temporary analysis directly inside `wiki/analyses/`.

## Knowledge Promotion

After a task succeeds:

1. Summarize outputs in `report/result_summary.md`.
2. Write reusable lessons to `report/knowledge_candidate.md`.
3. Ask the user whether to promote the candidate into `wiki/` or `my-skills/`.
4. Promote only after user confirmation.

## Lint Workflow

Periodically check:

- `wiki/index.md` covers major wiki pages.
- `wiki/analyses/*` have `README.md`, `manifest.yaml`, and runnable code or clear code notes.
- Raw projects that have been compiled are linked from wiki pages.
- There are no empty concept notes in `wiki/concepts/`.
- Paths are relative or config-driven.

## Do Not

- Do not overwrite user source data.
- Do not put private or unauthorized files into publishable examples.
- Do not write temporary outputs directly into `wiki/`.
- Do not promote a failed or unverified run as a standard template.
- Do not hard-code local paths into reusable templates.

