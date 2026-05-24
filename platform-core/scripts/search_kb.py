from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from platform_config import default_analyses_dir

DEFAULT_ANALYSES_DIR = default_analyses_dir()

FIELD_WEIGHTS = {
    "title": 8,
    "ai_usage.retrieval_keywords": 7,
    "methods": 6,
    "problem_type": 4,
    "tags": 3,
    "packages": 3,
    "id": 2,
    "language": 1,
    "ai_usage.adaptation_rules": 1,
}

GENERIC_TERMS = {
    "meta",
    "分析",
    "meta分析",
    "机器学习",
    "模型",
    "方法",
    "r",
    "数据",
}

ALIASES = {
    "网状": ["nma", "network"],
    "nma": ["网状"],
    "贝叶斯": ["bayesian"],
    "随机森林": ["randomforest", "random-forest", "random_forest"],
    "xgboost": ["boosting", "树与集成"],
    "pca": ["主成分分析", "降维"],
    "k-means": ["kmeans", "聚类"],
    "knn": ["k近邻"],
    "svm": ["支持向量机"],
    "逻辑回归": ["logistic"],
    "lasso": ["惩罚回归", "特征选择"],
    "ridge": ["惩罚回归"],
    "rcs": ["限制性立方样条"],
    "剂量反应": ["dose-response", "dose_response"],
}


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


def get_nested(data: dict[str, Any], dotted_key: str) -> Any:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def flatten_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(flatten_value(item) for item in value)
    if isinstance(value, dict):
        return " ".join(flatten_value(item) for item in value.values())
    return str(value)


def normalize_text(value: str) -> str:
    return value.lower().replace("_", "-")


def tokenize(query: str) -> list[str]:
    raw_terms = [term.strip().lower() for term in re.split(r"[\s,，;；]+", query) if term.strip()]
    expanded: list[str] = []
    for term in raw_terms:
        normalized = normalize_text(term)
        expanded.append(normalized)
        expanded.extend(normalize_text(alias) for alias in ALIASES.get(normalized, []))
    return list(dict.fromkeys(expanded))


def term_weight(term: str) -> float:
    return 0.2 if term in GENERIC_TERMS else 1.0


def exactish_match(term: str, value: str) -> bool:
    if not term:
        return False
    return term in value


def score_manifest(manifest: dict[str, Any], query_terms: list[str]) -> tuple[float, dict[str, list[str]], list[str]]:
    score = 0.0
    matched: dict[str, list[str]] = {}
    why: list[str] = []

    for field, field_weight in FIELD_WEIGHTS.items():
        value = normalize_text(flatten_value(get_nested(manifest, field)))
        if not value:
            continue
        terms = [term for term in query_terms if exactish_match(term, value)]
        if not terms:
            continue
        matched[field] = terms
        term_score = sum(term_weight(term) for term in terms)
        score += field_weight * term_score
        why.append(f"{field} matched: {', '.join(terms)}")

    title = normalize_text(str(manifest.get("title", "")))
    if title and normalize_text(" ".join(query_terms)) in title:
        score += 10
        why.append("query phrase appears in title")

    return score, matched, why


def load_manifests(analyses_dir: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for manifest_path in sorted(analyses_dir.glob("*/manifest.yaml")):
        manifest = parse_simple_yaml(manifest_path)
        manifest["_manifest_path"] = str(manifest_path)
        manifest["_template_dir"] = str(manifest_path.parent)
        results.append(manifest)
    return results


def passes_filters(
    manifest: dict[str, Any],
    problem_type: str,
    language: str,
    template_type: str,
    tag: str,
) -> bool:
    if problem_type and problem_type not in str(manifest.get("problem_type", "")):
        return False
    if language and language.lower() != str(manifest.get("language", "")).lower():
        return False
    if template_type and template_type.lower() != str(manifest.get("type", "")).lower():
        return False
    if tag:
        tags = normalize_text(flatten_value(manifest.get("tags", "")))
        if normalize_text(tag) not in tags:
            return False
    return True


def next_action_for(item: dict[str, Any]) -> str:
    return (
        "Read manifest.yaml and README.md, then create an analysis task with create_analysis_project.py "
        "if the template matches the user's data."
    )


def search(
    query: str,
    analyses_dir: Path,
    limit: int,
    problem_type: str = "",
    language: str = "",
    template_type: str = "",
    tag: str = "",
) -> list[dict[str, Any]]:
    query_terms = tokenize(query)
    has_specific_terms = any(term_weight(term) >= 1.0 for term in query_terms)
    ranked: list[dict[str, Any]] = []

    for manifest in load_manifests(analyses_dir):
        if not passes_filters(manifest, problem_type, language, template_type, tag):
            continue

        score, matched, why = score_manifest(manifest, query_terms)
        if score <= 0:
            continue

        item = {
            "score": round(score, 3),
            "id": manifest.get("id", ""),
            "title": manifest.get("title", ""),
            "problem_type": manifest.get("problem_type", ""),
            "language": manifest.get("language", ""),
            "type": manifest.get("type", ""),
            "matched_fields": list(matched.keys()),
            "matched_terms": matched,
            "why_matched": why,
            "template_dir": manifest["_template_dir"],
            "manifest_path": manifest["_manifest_path"],
        }
        item["next_action"] = next_action_for(item)
        if not has_specific_terms:
            item["next_action"] = (
                "Query is too broad. Ask for outcome type or method, such as 连续变量, 二分类, "
                "剂量反应, 网状Meta, 相关系数, or 单个率."
            )
        ranked.append(item)

    ranked.sort(key=lambda item: (-item["score"], item["title"]))
    for index, item in enumerate(ranked):
        item["rank"] = index + 1
        item["recommended"] = index == 0 and has_specific_terms
    return ranked[:limit]


def print_text(results: list[dict[str, Any]]) -> None:
    if not results:
        print("No matched templates.")
        return

    for item in results:
        marker = " [recommended]" if item.get("recommended") else ""
        print(f"{item['rank']}. {item['title']} [{item['id']}]{marker}")
        print(f"   score: {item['score']}")
        print(f"   problem_type: {item['problem_type']}")
        print(f"   language: {item['language']}")
        print(f"   matched_fields: {', '.join(item['matched_fields'])}")
        print(f"   why: {'; '.join(item['why_matched'][:3])}")
        print(f"   template_dir: {item['template_dir']}")
        print(f"   manifest: {item['manifest_path']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Search analysis templates in the medical research knowledge base.")
    parser.add_argument("query", help="Search query, for example: 连续变量 Meta 分析")
    parser.add_argument("--analyses-dir", default=str(DEFAULT_ANALYSES_DIR), help="Path to wiki/analyses")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results")
    parser.add_argument("--best", action="store_true", help="Return only the top recommended result")
    parser.add_argument("--problem-type", default="", help="Filter by problem_type, for example: Meta分析")
    parser.add_argument("--language", default="", help="Filter by language, for example: R")
    parser.add_argument("--template-type", default="", help="Filter by manifest type")
    parser.add_argument("--tag", default="", help="Filter by tag")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    analyses_dir = Path(args.analyses_dir)
    if not analyses_dir.exists():
        raise SystemExit(f"Analyses directory does not exist: {analyses_dir}")

    limit = 1 if args.best else args.limit
    results = search(
        args.query,
        analyses_dir,
        limit,
        problem_type=args.problem_type,
        language=args.language,
        template_type=args.template_type,
        tag=args.tag,
    )
    if args.json:
        print(json.dumps({"query": args.query, "count": len(results), "results": results}, ensure_ascii=False, indent=2))
    else:
        print_text(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
