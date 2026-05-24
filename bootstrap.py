from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def q(path: Path) -> str:
    return str(path).replace("\\", "\\\\")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a local Medical AI Knowledge Platform workspace.")
    parser.add_argument("root", help="Install directory, for example <YOUR_INSTALL_DIR>")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    install_root = Path(args.root).resolve()
    vault_path = install_root / "my-vault"
    execution_path = install_root / "execution-platform"
    platform_core_path = execution_path / "platform-core"
    projects_path = execution_path / "projects"
    logs_path = execution_path / "logs"
    outputs_path = execution_path / "outputs"
    skills_path = install_root / "my-skills"

    for path in [install_root, execution_path, projects_path, logs_path, outputs_path, execution_path / "config", skills_path]:
        path.mkdir(parents=True, exist_ok=True)

    shutil.copytree(repo_root / "starter-vault", vault_path, dirs_exist_ok=True)
    shutil.copytree(repo_root / "platform-core", platform_core_path, dirs_exist_ok=True)
    shutil.copytree(repo_root / "starter-skills", skills_path, dirs_exist_ok=True)
    shutil.copytree(repo_root / "execution-platform-template", execution_path, dirs_exist_ok=True)

    paths_yaml = f"""platform_root: "{q(install_root)}"
vault_path: "{q(vault_path)}"
execution_platform: "{q(execution_path)}"

knowledge:
  index: "{q(vault_path / "wiki" / "index.md")}"
  analyses: "{q(vault_path / "wiki" / "analyses")}"
  concepts: "{q(vault_path / "wiki" / "concepts")}"
  sources: "{q(vault_path / "wiki" / "sources")}"

execution:
  projects: "{q(projects_path)}"
  outputs: "{q(outputs_path)}"
  logs: "{q(logs_path)}"

runtime:
  python_path: ""
  rscript_path: "Rscript"
"""
    (execution_path / "config" / "paths.yaml").write_text(paths_yaml, encoding="utf-8")

    workspace = {
        "folders": [
            {"name": "my-vault", "path": "my-vault"},
            {"name": "execution-platform", "path": "execution-platform"},
            {"name": "my-skills", "path": "my-skills"},
        ],
        "settings": {"files.encoding": "utf8"},
    }
    (install_root / "workspace.code-workspace").write_text(json.dumps(workspace, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Initialized platform at: {install_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
