from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none"}:
        return None
    return value.strip('"').strip("'")


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    pending_key: tuple[int, dict[str, Any], str] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if line.startswith("- "):
            item = parse_scalar(line[2:])
            if not isinstance(parent, list):
                if pending_key is None:
                    continue
                _, pending_parent, key = pending_key
                new_list: list[Any] = []
                pending_parent[key] = new_list
                stack.append((pending_key[0], new_list))
                parent = new_list
            parent.append(item)
            continue

        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value == "":
            new_dict: dict[str, Any] = {}
            if isinstance(parent, dict):
                parent[key] = new_dict
                pending_key = (indent, parent, key)
                stack.append((indent, new_dict))
            continue

        if isinstance(parent, dict):
            parent[key] = parse_scalar(raw_value)
            pending_key = None

    return root


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def candidate_config_paths() -> list[Path]:
    paths: list[Path] = []
    env_path = os.environ.get("MAKP_PATHS_CONFIG", "").strip()
    if env_path:
        paths.append(Path(env_path))

    root = repo_root()
    paths.extend(
        [
            root / "config" / "paths.yaml",
            root.parent / "config" / "paths.yaml",
        ]
    )
    return paths


def load_paths_config() -> dict[str, Any]:
    for path in candidate_config_paths():
        if path.exists():
            config = parse_simple_yaml(path)
            config["_config_dir"] = str(path.parent)
            return config
    return {}


def get_path(config: dict[str, Any], dotted_key: str, fallback: Path) -> Path:
    current: Any = config
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return fallback
        current = current[part]
    if not current:
        return fallback
    resolved = Path(str(current))
    if resolved.is_absolute():
        return resolved
    config_dir = config.get("_config_dir", "")
    if config_dir:
        return (Path(str(config_dir)) / resolved).resolve()
    return resolved


def default_analyses_dir() -> Path:
    return get_path(
        load_paths_config(),
        "knowledge.analyses",
        repo_root() / "starter-vault" / "wiki" / "analyses",
    )


def default_projects_dir() -> Path:
    return get_path(
        load_paths_config(),
        "execution.projects",
        repo_root() / "user-space" / "execution-platform" / "projects",
    )


def default_rscript_path() -> Path:
    return get_path(load_paths_config(), "runtime.rscript_path", Path("Rscript"))


def default_python_path() -> Path:
    return get_path(load_paths_config(), "runtime.python_path", Path("python"))
