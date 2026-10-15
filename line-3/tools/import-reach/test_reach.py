"""Behavioral checks for explicit static forward reachability."""

import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("reach.py")
SPEC = importlib.util.spec_from_file_location("pepeolithic_import_reach", SCRIPT)
REACH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REACH)


def synthetic(names, edges, entrypoints=(), *, issues=(), dynamics=(), cycles=()):
    return {"modules": [{"module": name, "path": name + ".py",
                         "entrypoint": name in entrypoints,
                         "dynamic_import_lines": [7] if name in dynamics else []}
                        for name in names],
            "edges": [{"from": source, "to": target} for source, target in edges],
            "issues": list(issues), "cycles": list(cycles)}


class ImportReachTests(unittest.TestCase):
    def test_example_reaches_three_and_identifies_spare(self):
        report = REACH.load_mapper().inspect(SCRIPT.parent / "examples")
        result = REACH.trace(report)
        self.assertEqual(result["starts"], ["main"])
        self.assertEqual(result["summary"], {"module_count": 4, "reached_count": 3,
                                              "unreached_count": 1})
        self.assertEqual(result["unreached"], [{"module": "spare", "path": "spare.py"}])
        self.assertEqual(next(x for x in result["reached"] if x["module"] == "helper")["import_path"],
                         ["main", "core", "helper"])

    def test_sorted_shortest_witness_and_explicit_seeds(self):
        report = synthetic("abcd", [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")], ("a",))
        result = REACH.trace(report)
        self.assertEqual(next(x for x in result["reached"] if x["module"] == "d")["import_path"],
                         ["a", "b", "d"])
        selected = REACH.trace(report, ["c", "b", "c"])
        self.assertEqual(selected["starts"], ["b", "c"])
        self.assertEqual(next(x for x in selected["reached"] if x["module"] == "d")["import_path"],
                         ["b", "d"])
        self.assertEqual([x["module"] for x in selected["unreached"]], ["a"])

    def test_cycle_terminates_and_flags_remain_visible(self):
        issue = {"type": "parse_error", "path": "other.py", "line": 1, "detail": "bad"}
        report = synthetic("abc", [("a", "b"), ("b", "a")], ("a",),
                           issues=(issue,), dynamics=("b",), cycles=(("a", "b"),))
        result = REACH.trace(report)
        self.assertEqual([x["module"] for x in result["reached"]], ["a", "b"])
        self.assertEqual(result["unreached"], [{"module": "c", "path": "c.py"}])
        self.assertEqual(result["issues"], [issue])
        self.assertEqual(result["cycles"], [("a", "b")])
        self.assertEqual(result["dynamic_imports"],
                         [{"module": "b", "path": "b.py", "line": 7}])

    def test_requires_known_start(self):
        report = synthetic("ab", [("a", "b")])
        with self.assertRaisesRegex(ValueError, "supply --start"):
            REACH.trace(report)
        with self.assertRaisesRegex(ValueError, "unknown start module"):
            REACH.trace(report, ["missing"])

    def test_random_graphs_match_independent_set_search(self):
        rng = random.Random(20261015)
        for _ in range(80):
            names = list("abcdefghi")
            edges = [(a, b) for a in names for b in names if rng.random() < 0.15]
            starts = rng.sample(names, rng.randint(1, 3))
            result = REACH.trace(synthetic(names, edges), starts)
            expected = set(starts)
            while True:
                more = expected | {target for source, target in edges if source in expected}
                if more == expected:
                    break
                expected = more
            self.assertEqual({x["module"] for x in result["reached"]}, expected)
            self.assertEqual({x["module"] for x in result["unreached"]}, set(names) - expected)
            for item in result["reached"]:
                path = item["import_path"]
                self.assertIn(path[0], starts)
                self.assertEqual(path[-1], item["module"])
                self.assertTrue(all((a, b) in edges for a, b in zip(path, path[1:])))

    def test_scanning_source_does_not_execute_it(self):
        scratch = Path("test/scratch")
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            root = Path(temp)
            marker = root / "executed"
            (root / "main.py").write_text(
                "from pathlib import Path\n"
                + "Path(" + repr(str(marker)) + ").write_text('ran')\n"
                + "import helper\n"
                + "if __name__ == '__main__': pass\n", encoding="utf-8")
            (root / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
            result = REACH.trace(REACH.load_mapper().inspect(root))
            self.assertEqual(result["summary"]["reached_count"], 2)
            self.assertFalse(marker.exists())

    def test_cli_status_and_json(self):
        root = SCRIPT.parent / "examples"
        run = subprocess.run([sys.executable, "-B", str(SCRIPT), str(root), "--json",
                              "--check-unreached"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["summary"]["unreached_count"], 1)
        selected = subprocess.run([sys.executable, "-B", str(SCRIPT), str(root),
                                   "--start", "spare", "--json"], capture_output=True, text=True)
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertEqual(json.loads(selected.stdout)["summary"]["reached_count"], 1)

    def test_cli_rejects_roots_outside_workspace_and_unknown_modules(self):
        outside = subprocess.run([sys.executable, "-B", str(SCRIPT), "/tmp"],
                                 capture_output=True, text=True)
        self.assertEqual(outside.returncode, 2)
        self.assertFalse(outside.stdout)
        unknown = subprocess.run([sys.executable, "-B", str(SCRIPT),
                                  str(SCRIPT.parent / "examples"), "--start", "ghost"],
                                 capture_output=True, text=True)
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("unknown start", unknown.stderr)


if __name__ == "__main__":
    unittest.main()
