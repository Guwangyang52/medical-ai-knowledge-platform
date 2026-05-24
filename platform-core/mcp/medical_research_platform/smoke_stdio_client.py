from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PYTHON_EXE = sys.executable
SERVER = Path(__file__).with_name("medical_research_platform_server.py")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    proc = subprocess.Popen(
        [PYTHON_EXE, str(SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "knowledge.search",
                "arguments": {"query": "连续变量 Meta 分析", "best": True},
            },
        },
    ]

    assert proc.stdin is not None
    assert proc.stdout is not None

    for message in messages:
        proc.stdin.write((json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8"))
        proc.stdin.flush()
        line = proc.stdout.readline().decode("utf-8", errors="replace")
        print(line.strip())

    proc.stdin.close()
    proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
