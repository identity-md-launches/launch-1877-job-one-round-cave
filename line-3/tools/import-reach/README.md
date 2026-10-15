# Import Reach

Import Reach shows which Python modules can be reached through explicit local
imports from selected starts. By default it starts at every source module with
a `__main__` guard; `--start MODULE` chooses an exact dotted module instead and
can be repeated. It reports a shortest import path to each reached module and
lists the modules unreached from those starts. It reads source through the
sibling Import Map tool without importing or executing the inspected project.
Keep `import-map/` alongside this folder when copying it. Python 3.9+ and only
the standard library are required.

From the repository root, run this working example:

```sh
python3 -B line-3/tools/import-reach/reach.py line-3/tools/import-reach/examples
```

Tried locally: it found four modules and three reached from `main`:
`main -> core -> helper` is the longest path. `spare` is unreached from this
start. The scan returned no issues, cycles or dynamic import calls; exit 0.
`--check-unreached` makes that example exit 1. `--json` includes exact paths,
distances, counts and all scan warnings. `--strict` exits 1 for any scan issue,
cycle or recognized dynamic import call. Both flags can be combined. Bad roots,
unknown starts, or no detected entry point without `--start` exit 2 with no
partial success report. The root must be an existing import root inside the
current workspace. The CLI writes no output files.

I also scanned the actual `line-1/tools/deadline-sentry` source without running
it. Both modules were reachable from its two `__main__` guards, with no scan
warnings; `--json --strict` exited 0. Eight local behavioral tests passed,
including source execution traps, cycles, deterministic shortest paths,
multi-start selection, CLI status codes, and 80 independently checked random
graphs. Reproduce them with:

```sh
python3 -B -m unittest discover -s line-3/tools/import-reach -v
```

An unreached module is a **review candidate**, not proof that it is unused.
Imports can come from packaging entry points, external callers, dynamic calls,
plugins, hooks, and implicit package initialization; conditional imports may
appear in the graph even when their branch never runs. A parse error can hide
an edge, so inspect warnings before using `--check-unreached` in automation.
The mapper's conservative handling of attributes and namespace packages also
applies. Whole-tree scanning has no aggregate file or memory limit, and a
full witness path for every reached module can take quadratic output space in
a long chain. This tool needs no network, coin, wallet, payment or transaction.
