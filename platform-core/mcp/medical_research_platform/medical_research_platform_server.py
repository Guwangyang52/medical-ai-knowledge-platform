from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


PLATFORM_CORE = Path(__file__).resolve().parents[2]
EXECUTION_PLATFORM = PLATFORM_CORE.parent
SCRIPTS_DIR = PLATFORM_CORE / "scripts"
PYTHON_EXE = Path(sys.executable)


TOOLS: dict[str, dict[str, Any]] = {
    "knowledge.search": {
        "description": "Search analysis templates in the Obsidian-derived knowledge base.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "problem_type": {"type": "string"},
                "language": {"type": "string"},
                "tag": {"type": "string"},
                "best": {"type": "boolean"},
                "limit": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
    "knowledge.validate": {
        "description": "Validate wiki/analyses template structure and manifest coverage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "json": {"type": "boolean"},
                "csv": {"type": "string"},
            },
        },
    },
    "analysis.create_task": {
        "description": "Create a standard analysis task directory under the execution platform.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "template_dir": {"type": "string"},
                "task_id": {"type": "string"},
                "copy_template_code": {"type": "boolean"},
                "force": {"type": "boolean"},
            },
            "required": ["name"],
        },
    },
    "analysis.run_r": {
        "description": "Run an R analysis task directory with Rscript.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_dir": {"type": "string"},
                "script": {"type": "string"},
            },
            "required": ["task_dir"],
        },
    },
    "analysis.run_python": {
        "description": "Run a Python analysis task directory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_dir": {"type": "string"},
                "script": {"type": "string"},
                "timeout": {"type": "integer"},
                "script_args": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["task_dir"],
        },
    },
    "archive.result": {
        "description": "Archive task outputs and generate result_summary/output_manifest/knowledge_candidate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_dir": {"type": "string"},
            },
            "required": ["task_dir"],
        },
    },
}


def run_command(args: list[str], cwd: Path = EXECUTION_PLATFORM) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    completed = subprocess.run(
        args,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "command": args,
    }


def tool_knowledge_search(arguments: dict[str, Any]) -> dict[str, Any]:
    query = str(arguments.get("query", "")).strip()
    if not query:
        raise ValueError("query is required")

    args = [
        str(PYTHON_EXE),
        str(SCRIPTS_DIR / "search_kb.py"),
        query,
        "--json",
        "--limit",
        str(int(arguments.get("limit", 5))),
    ]
    if arguments.get("best"):
        args.append("--best")
    if arguments.get("problem_type"):
        args.extend(["--problem-type", str(arguments["problem_type"])])
    if arguments.get("language"):
        args.extend(["--language", str(arguments["language"])])
    if arguments.get("tag"):
        args.extend(["--tag", str(arguments["tag"])])

    result = run_command(args)
    try:
        parsed = json.loads(result["stdout"]) if result["stdout"].strip() else {}
    except json.JSONDecodeError:
        parsed = {"raw_stdout": result["stdout"]}
    result["parsed"] = parsed
    return result


def tool_knowledge_validate(arguments: dict[str, Any]) -> dict[str, Any]:
    args = [str(PYTHON_EXE), str(SCRIPTS_DIR / "validate_kb.py")]
    if arguments.get("json", True):
        args.append("--json")
    if arguments.get("csv"):
        args.extend(["--csv", str(arguments["csv"])])
    result = run_command(args)
    try:
        parsed = json.loads(result["stdout"]) if result["stdout"].strip().startswith("{") else {}
    except json.JSONDecodeError:
        parsed = {}
    result["parsed"] = parsed
    return result


def tool_analysis_create_task(arguments: dict[str, Any]) -> dict[str, Any]:
    name = str(arguments.get("name", "")).strip()
    if not name:
        raise ValueError("name is required")

    args = [str(PYTHON_EXE), str(SCRIPTS_DIR / "create_analysis_project.py"), name]
    if arguments.get("description"):
        args.extend(["--description", str(arguments["description"])])
    if arguments.get("template_dir"):
        args.extend(["--template-dir", str(arguments["template_dir"])])
    if arguments.get("task_id"):
        args.extend(["--task-id", str(arguments["task_id"])])
    if arguments.get("copy_template_code"):
        args.append("--copy-template-code")
    if arguments.get("force"):
        args.append("--force")
    return run_command(args)


def tool_analysis_run_r(arguments: dict[str, Any]) -> dict[str, Any]:
    task_dir = str(arguments.get("task_dir", "")).strip()
    if not task_dir:
        raise ValueError("task_dir is required")

    args = [str(PYTHON_EXE), str(SCRIPTS_DIR / "run_r_task.py"), task_dir]
    if arguments.get("script"):
        args.extend(["--script", str(arguments["script"])])
    return run_command(args)


def tool_analysis_run_python(arguments: dict[str, Any]) -> dict[str, Any]:
    task_dir = str(arguments.get("task_dir", "")).strip()
    if not task_dir:
        raise ValueError("task_dir is required")

    args = [str(PYTHON_EXE), str(SCRIPTS_DIR / "run_python_task.py"), task_dir]
    if arguments.get("script"):
        args.extend(["--script", str(arguments["script"])])
    if arguments.get("timeout"):
        args.extend(["--timeout", str(int(arguments["timeout"]))])
    for item in arguments.get("script_args", []) or []:
        args.append(str(item))
    return run_command(args)


def tool_archive_result(arguments: dict[str, Any]) -> dict[str, Any]:
    task_dir = str(arguments.get("task_dir", "")).strip()
    if not task_dir:
        raise ValueError("task_dir is required")

    args = [str(PYTHON_EXE), str(SCRIPTS_DIR / "archive_result.py"), task_dir]
    return run_command(args)


TOOL_HANDLERS = {
    "knowledge.search": tool_knowledge_search,
    "knowledge.validate": tool_knowledge_validate,
    "analysis.create_task": tool_analysis_create_task,
    "analysis.run_r": tool_analysis_run_r,
    "analysis.run_python": tool_analysis_run_python,
    "archive.result": tool_archive_result,
}


def ensure_utf8_stdio() -> None:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def mcp_tool_schema(name: str, meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "description": meta["description"],
        "inputSchema": meta["inputSchema"],
    }


def content_response(payload: Any) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, ensure_ascii=False, indent=2),
            }
        ]
    }


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")

    if method == "notifications/initialized":
        return None

    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "medical-research-platform", "version": "0.1.0"},
            }
        elif method == "tools/list":
            result = {"tools": [mcp_tool_schema(name, meta) for name, meta in TOOLS.items()]}
        elif method == "tools/call":
            params = request.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {}) or {}
            if name not in TOOL_HANDLERS:
                raise ValueError(f"Unknown tool: {name}")
            result = content_response(TOOL_HANDLERS[name](arguments))
        else:
            raise ValueError(f"Unsupported method: {method}")

        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": str(exc)},
        }


def stdio_loop() -> int:
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    for raw_line in stdin:
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
        else:
            response = handle_request(request)
        if response is not None:
            stdout.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))
            stdout.flush()
    return 0


def call_tool_for_cli(name: str, arguments_json: str, arguments_file: str = "") -> int:
    if arguments_file:
        arguments = json.loads(Path(arguments_file).read_text(encoding="utf-8"))
    else:
        arguments = json.loads(arguments_json) if arguments_json else {}
    if name not in TOOL_HANDLERS:
        raise SystemExit(f"Unknown tool: {name}")
    print(json.dumps(TOOL_HANDLERS[name](arguments), ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Medical research platform MCP stdio server.")
    parser.add_argument("--call", help="Call one tool directly for smoke testing")
    parser.add_argument("--arguments", default="{}", help="JSON arguments for --call")
    parser.add_argument("--arguments-file", default="", help="JSON argument file for --call")
    args = parser.parse_args()

    if args.call:
        return call_tool_for_cli(args.call, args.arguments, args.arguments_file)
    return stdio_loop()


if __name__ == "__main__":
    raise SystemExit(main())
