#!/usr/bin/env python3
"""Trace modules reachable through explicit local imports from Python entry points."""

import argparse
from collections import deque
import importlib.util
import json
from pathlib import Path
import sys


def load_mapper():
    """Load the delivered mapper, never code from the inspected project."""
    path = Path(__file__).resolve().parents[1] / "import-map" / "import_map.py"
    spec = importlib.util.spec_from_file_location("pepeolithic_import_mapper", path)
    mapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mapper)
    return mapper


def trace(report, starts=None):
    """Find shortest, deterministic paths from selected roots to local modules."""
    records = {item["module"]: item for item in report["modules"]}
    seeds = sorted(set(starts)) if starts else sorted(
        name for name, item in records.items() if item["entrypoint"]
    )
    if not seeds:
        raise ValueError("no __main__ entry points found; supply --start MODULE")
    unknown = sorted(set(seeds) - records.keys())
    if unknown:
        raise ValueError("unknown start module(s): " + ", ".join(unknown))

    graph = {name: set() for name in records}
    for edge in report["edges"]:
        graph[edge["from"]].add(edge["to"])
    parent = {name: None for name in seeds}
    distance = {name: 0 for name in seeds}
    pending = deque(seeds)
    while pending:
        source = pending.popleft()
        for target in sorted(graph[source]):
            if target not in parent:
                parent[target] = source
                distance[target] = distance[source] + 1
                pending.append(target)

    reached = []
    for name in sorted(parent, key=lambda item: (distance[item], item)):
        path = [name]
        while parent[path[-1]] is not None:
            path.append(parent[path[-1]])
        item = records[name]
        reached.append({"module": name, "path": item["path"],
                        "distance": distance[name], "import_path": path[::-1]})
    unreached = [{"module": name, "path": records[name]["path"]}
                 for name in sorted(records.keys() - parent.keys())]
    dynamic = [{"module": item["module"], "path": item["path"], "line": line}
               for item in report["modules"]
               for line in item["dynamic_import_lines"]]
    return {"starts": seeds, "reached": reached, "unreached": unreached,
            "issues": report["issues"], "cycles": report["cycles"],
            "dynamic_imports": dynamic,
            "summary": {"module_count": len(records), "reached_count": len(reached),
                        "unreached_count": len(unreached)},
            "scope": "Explicit static local imports only. Unreached does not mean unused."}


def format_text(result):
    summary = result["summary"]
    lines = ["Starts: " + ", ".join(result["starts"]),
             f"Reached: {summary['reached_count']} of {summary['module_count']} modules"]
    for item in result["reached"]:
        lines.append(" -> ".join(item["import_path"]))
    lines.append(f"Unreached from these starts: {summary['unreached_count']}")
    for item in result["unreached"]:
        lines.append(f"  {item['module']} ({item['path']})")
    lines.append(f"Scan warnings: {len(result['issues'])} issues, "
                 f"{len(result['cycles'])} cycle groups, "
                 f"{len(result['dynamic_imports'])} dynamic import calls")
    lines.append(result["scope"])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="explicit Python import root inside the current workspace")
    parser.add_argument("--start", action="append", metavar="MODULE",
                        help="exact dotted start module; repeat to select multiple starts (default: all __main__ guards)")
    parser.add_argument("--json", action="store_true", help="emit deterministic JSON with scan warnings")
    parser.add_argument("--strict", action="store_true", help="exit 1 for scan issues, cycles or dynamic imports")
    parser.add_argument("--check-unreached", action="store_true", help="exit 1 if some modules are unreached from selected starts")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        if not root.is_relative_to(Path.cwd().resolve()) or not root.is_dir():
            raise ValueError("root must be an existing directory inside the current workspace")
        result = trace(load_mapper().inspect(root), args.start)
    except (OSError, ValueError, RuntimeError, RecursionError) as exc:
        print("import-reach: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else format_text(result))
    warnings = result["issues"] or result["cycles"] or result["dynamic_imports"]
    return int(bool(args.strict and warnings or args.check_unreached and result["unreached"]))


if __name__ == "__main__":
    sys.exit(main())
