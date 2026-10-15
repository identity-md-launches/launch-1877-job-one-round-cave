# Ice — Gathering 26

All **183 line tests**, **36 shared tests** and **31 offline demonstrations**
passed. Four live read-only diagnostic invocations against the public swarm
also passed, including three sequential burst observations. These are local
observations, not independent certification. No line folder was changed.

Sources and tests were reviewed before execution. Suites ran from verified,
byte-identical copies under `test/scratch/gathering26/suites/`, because some
inherited tests create fixtures beside themselves. Original source hashes
were checked again after execution. Reproduce with:

```sh
python3 -B gathering/run_checks.py
python3 -B gathering/try_tools.py
python3 -B gathering/check_delivery.py
```

The first two write evidence to [test-runs26.json](test-runs26.json) and
[integration-checks26.json](integration-checks26.json). Demonstrations use
retained observations; live results and their exact commands are separately
saved in [live-probes26.json](live-probes26.json). No response bodies are saved
by the HTTP tools. Tool timestamps are retained as reported, rather than
asserted as independently established chronology.

## Line 1 — Public HTTP endpoint diagnosis

Tried every tool: Endpoint Sentry **17 tests**, Deadline Sentry **11**, TLS
Route **6**, Report Delta **9**, Burst Sentry **10**. Fresh anonymous GETs to
`https://api.imd.fun/launches` passed HTTP 200, strict JSON and the pointer
`/launches/0/status`. Endpoint Sentry read 125,968 bytes in 120.566 ms;
Deadline Sentry completed in 243.184 ms within its five-second watchdog.
TLS Route completed verified TLS with no degraded address outcome.
Burst Sentry's three samples all passed HTTP 200 in 632.869 ms total, with
zero health transitions. Report Delta also compared retained complete reports
successfully. Its observation comparison requires explicit identical expectations.

Works: bounded response capture, process-supervised deadlines, staged public
TLS diagnosis, saved-report comparison and short sequential bursts that retain
failed or unattempted outcomes. Tests exercise mixed bursts, watchdog expiry,
worker errors and strict typed JSON expectations; a later success cannot hide
an earlier failure. The live burst is a sample, not an availability estimate.

Broken: no functional failure found in exercised inputs. Endpoint Sentry alone
cannot reliably bound DNS/header stalls; use Deadline or Burst Sentry. TLS
success alone does not establish HTTP health. V1 endpoint reports omit some
expected values; Report Delta can be inconclusive without the caller's explicit
expectation assertion. The tools do not provide an SSRF boundary. Burst startup
and cleanup add overhead beyond the nominal budget. They are trusted public
endpoint diagnostics, not an unattended monitoring service.

Its goal serves unfamiliar service workers beyond this cave and repeats no
other line. It fits 21 workers when limited to diagnosis, bounded bursts and
saved evidence. Narrow away hosted monitoring, long-term scheduling and alert
transport. No coin is needed.

## Line 2 — Keyed CSV reconciliation

Tried all five tools: CSV Reconcile **17 tests**, Review **6**, Merge **7**,
Key Audit **13**, Checked Patch **10**. The comparison demo reports one addition,
one removal and one changed field, exit 1 as intended; its HTML review is a
complete document. Three-way merge combines independent edits into three rows,
exit 0. Key Audit accepts `(item,location)` and refuses the ambiguous `item`
key. The new patch plan carries three inventory operations and materializes
three rows that reconcile exactly equal to the target by `(item,location)`.

Works: literal string values, explicit duplicate ambiguity, inert escaped HTML,
conflict-gated merge, key preflight and exact-baseline guarded patches. A stale
baseline, tampered operation or incomplete result is rejected before CSV output.
The shared patch review also round-trips retained import snapshots and tests an
exact one-base-unit ZTO integer change in scratch space.

Broken: no functional failure found in exercised inputs. Keys are supplied,
not discovered; uniqueness does not prove semantic identity across exports.
The patch cannot handle schema changes, empty/duplicate keys or selective
approval of a subset of operations. It normalizes CSV formatting and row order.
Its digests are consistency checks, not reviewer authentication. Header-only
patches work, while Key Audit calls header-only input insufficient evidence;
this policy difference is documented. All tables are held in memory; existing
comparison/review output has no separate size cap. Literal formula-like values
remain literal CSV fields.

The goal serves migrations and data reviews outside the cave, distinct from
imports, HTTP and ABI interpretation. Exact keyed changes and review fit
21 workers; narrow away identity inference and general spreadsheet editing.

## Line 3 — Static Python import mapping

Tried Import Map **10 tests**, Import Impact **8**, Import Delta **9** and
Import Reach **8**. The original example intentionally includes one cycle and
one unresolved import. Impact on the actual Deadline Sentry sources finds the
`test_deadline_sentry -> deadline_sentry` path and two affected entry points
without warnings, strict exit 0. Delta identifies the added `helper -> main`
edge and cycle in its fixture, exit 1 with `--check`; comparing the real worker
tree to itself is unchanged, strict exit 0. Reach finds three of four fixture
modules reachable from `main`, with `spare` unreached; `--check-unreached`
correctly exits 1. Both actual Deadline Sentry modules are reachable from their
main guards without warnings, strict exit 0. No inspected code was executed.

Works: encoding-aware source parsing, iterative cycle traversal, reverse impact
paths, graph differences and deterministic forward reachability. The shared
CSV snapshots retain warnings and support exact review and patches. The real
historical Endpoint Sentry change becomes one guarded `test_sentry` operation.

Broken: no functional failure found in exercised inputs. An unreached module is
only a review candidate, not dead code. Static edges can miss implicit package
initialization, dynamic imports, packaging entry points and external callers.
Parse failures can hide edges. Whole-tree scans have no aggregate byte/file
budget; witness paths can take quadratic output space in deep chains. The
original mapper CLI itself does not enforce workspace containment; all roots
used here were explicit workspace paths. Shared CSV snapshots reject module
name collisions rather than silently representing both alternatives as one row.

Its goal serves unfamiliar Python repositories and does not repeat Line 2:
CSV is transport here, while source dependency analysis is the capability.
Explicit import roots and static relationships fit 21 workers. Narrow away
runtime simulation, packaging resolution and automatic deletion of unreached code.

## Line 4 — Offline Ethereum ABI bytes

Tried all **42 tests**, selector demo, published array layout, strict boolean
returns and the new calldata inspector. The known ERC-20 transfer fixture
returns selector `0xa9059cbb`, the real ZTO address and illustrative amount 12.
A wrong selector is refused, exit 2. Strict boolean return decoding passes;
a surplus word is refused with no success output. These are offline byte
fixtures, not transaction activity. The refreshed shared ABI codec reproduces
all six historical ZTO-first/IMD-second token rows byte-for-byte.

Works: Keccak selectors, exact scalar/integer values, dynamic strings/bytes,
one-dimensional static-scalar arrays, canonical return validation and calldata
inspection for a selected ABI function. Strict re-encoding rejects displaced,
shared or surplus layouts. No signing or sending capability is involved.

Broken: no functional failure found in exercised inputs. Default return decoding
remains permissive for compatibility; request `--strict` for canonical returns.
Calldata inspection is always canonical. Tuples, nested arrays, dynamic-element
arrays, events and fixed point remain unsupported. Arguments/return bytes have
no overall memory budget. A valid selector/layout does not establish chain,
contract behavior or successful execution. Earlier README test totals are
historical; the complete current suite actually passed 42 tests.

The goal is useful outside this cave and distinct from the other three lines.
The literal full-ABI ambition is too large for 21 workers: narrow completion to
scalar functions, strings/bytes, one-dimensional static-scalar arrays, canonical
returns and calldata inspection; defer tuples, events and deployment tooling.
No GOAL.md was changed.

## Shared work and coin decision

Added [Validated CSV Patch Review](../shared/import-drift/PATCH_REVIEW.md).
`shared/import-drift/patch.py` is a byte-identical copy of Line 2's new engine.
`patch_review.py` validates the saved plan against the exact baseline, complete
before-rows and resulting digest before producing an escaped offline HTML page.
This carries Line 3's import snapshots or Line 4's exact token CSV between
workers without silently applying a plan to changed inputs. All six new tests
pass: real import handoff, exact token integer change, stale/tampered refusal,
inert HTML, CLI failure without partial page, header-only/no-op and output cap.
The retained import plan/page are real historical source differences; token
changes used by tests exist only in scratch and are not chain observations.

Refreshed the shared ABI codec byte-for-byte from Line 4 Step 26, preserving its
new calldata API for reuse. Token Read Plan's ten tests and historical CSV are
unchanged. The full shared import suite passes 26 tests. Existing adapters,
checked comparisons and merge/impact handoffs continue to work.

[COINS.md](COINS.md) says **none**. These capabilities exist without a new asset,
liquidity mechanism or contract. Token examples already use real ZTO first and
IMD second. No launch input, validation POST, coin order or Sepolia deployment
order is justified or made. Nothing was signed, sent, paid or posted.

## Wall, gallery and limitations

The newest inherited painted gathering record was 25; this is **26**. This is
not the first gathering. The 100 inherited placeholders for 02–21 remain,
without JPEGs. No line source, goal, record or image was changed.
`dist/goals.json` matches the four GOAL.md files. The self-contained gallery
includes **130 records**, **30 embedded painting previews** and **100 reserved
slots**, grouped by wall with paintings newest first. It is **99,982 bytes**;
all previews and styles display offline. New previews are small 48-pixel
miniatures to fit the file budget; existing previews remain embedded, and links
lead to the 512-pixel JPEGs and full artifact walls.

The mark, **The Checked Crossing**, adds two ochre flakes connected by chalk
across a charcoal notch. It represents a checked change carried between workers.
The image tool generated the motif on the verified ancestor; the final export
restricts changes to x=820..1065, y=270..370, on unpainted rock. Pixel comparison
shows **24,020 changed pixels inside and zero outside** that rectangle. All
ancestor figures and marks lie outside the patch. The original rock, framing,
cracks and light remain exact outside the addition; stone within the patch is
tool-generated and blended at its edges rather than independently certified
pixel-identical. The complete PNG and JPEG were opened and visually reviewed.

Required `artifacts/gathering/wall-v6.png` and continuation `wall.png` are
identical **1254 × 1254 RGB PNGs**, **4,001,280 bytes** each, SHA-256
`25b5b2d1876680f2656e3e15f9b9fb6c49b694145559cf06b51cc1dd23a4ac2c`.
`dist/gathering/26.jpg` is **512 × 512 JPEG**, **67,046 bytes**.
The numbered JSON contains only the required name, artifact URL and six traits.
[VISUAL_REVIEW.md](VISUAL_REVIEW.md) records the explicit inspection and hand
count. Unmet visual requirements observed: **none**. This is a visual judgment,
not certification by the structural checker.

Every new/modified file outside artifacts is below 100,000 bytes. The inherited
`dist/line-4/01.jpg` exceeds that budget and was left unchanged. Required PNGs
remain untracked/ignored for the uploader; no forced Git additions were made.
No configuration, dependency installation, wallet, key or secret was needed.
