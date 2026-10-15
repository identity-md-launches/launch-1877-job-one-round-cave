# Burst Sentry

Find intermittent public HTTP failures using 2–10 sequential, anonymous GET
observations under one total time budget. Each attempt uses exactly the same
status, strict JSON and JSON-pointer/value expectations. Every attempt is
retained, including failures and killed workers, so a later success cannot
hide an earlier failure. Python 3.9+ standard library only; no installation.

One command from the repository root shows it working on the real swarm:

```sh
python3 -B line-1/tools/burst-sentry/burst_sentry.py https://api.imd.fun/launches --samples 3 --budget 10 --per-probe 3 --timeout 2 --json --expect-path /launches/0/status
```

On 2026-10-15 at 18:02 UTC, this command returned `all_passed`, exit 0.
All three observations returned HTTP 200, strict JSON and the expected pointer;
each read 125,968 bytes. Total measured burst time was 735.497 ms. The command
and body-free evidence are in [observed-live.json](observed-live.json).
This observation establishes neither future availability nor an availability
percentage. The offline checks deliberately exercise mixed and failed results.

Keep the sibling `endpoint-sentry/sentry.py` and
`deadline-sentry/deadline_sentry.py` when copying this tool. Burst Sentry
imports those explicit workspace sources; it uses Endpoint Sentry's validation
and Deadline Sentry's single-process supervisor. The child runs the original
Endpoint Sentry with isolated Python, closed stdin and captured output.
No additional dependencies or external service are needed.

## Results and budgets

The CLI prints one `burst-sentry/v1` JSON report containing the full shared
expectations, limits, summary and each observation. `compare_value` distinguishes
an expected JSON `null` from an omitted value expectation. Use `--expect-value`
with `--expect-path` to compare a typed JSON value, including the empty root
pointer. Boolean `false` differs from numeric zero.

- `all_passed`: every requested sample ran and passed; exit 0.
- `mixed`: all samples ran, with both passing and failing observations; exit 1.
- `all_failed`: all samples ran and failed; exit 1.
- `incomplete`: fewer samples ran than requested; exit 1, or 2 for a local worker
  error. `not_attempted` counts missing observations separately from failures.

Invalid CLI arguments return exit 2 before any connection. Worker startup,
protocol or argument errors stop the burst immediately and return exit 2;
inspect `stop_reason` before interpreting any summary. A per-probe watchdog
expiry is a failed sample, not a completed HTTP observation. It may be followed
by another sample while total budget remains. No partial success is retained.

Defaults: three samples, 12-second total budget, three seconds per watchdog,
two-second child timeout, 256 KiB per response and three redirects. `--budget`
accepts up to 120 seconds; per-probe/child timeouts up to 15 seconds; response
bytes up to 1 MiB. Before each launch the remaining total budget caps its
watchdog. Process creation, OS scheduling, cleanup and JSON serialization may
add overhead; this is an operational limit, not a hard real-time guarantee.
No sleeps, intervals, parallel requests, persistent monitor or background job
are involved. Each invocation starts at most ten child processes sequentially.
Redirects can add GETs per sample; they retain the sibling's limits and rules.

`health_transitions` counts changes in consecutive observed pass/fail outcomes;
it does not infer unobserved events. Failure counts distinguish transport stages,
watchdog errors and failed checks such as `check:status` or `check:json_value`.
One observation can fail several checks. Last-hop statuses count observed
responses only; a redirect or a partial body is not proof of endpoint health.
Body digests remain in the original sample evidence; a changing digest alone
does not make a sample fail. The tool does not calculate an SLA or claim a
root cause from a small burst.

Use only trusted public HTTPS endpoints with non-secret URLs and safe GET
semantics. The original tool verifies TLS, sends its dedicated User-Agent,
rejects credentials and unsafe redirects, bounds bodies and stores no response
bodies. It does not filter private IP addresses or provide an SSRF boundary.
URLs and redirect destinations appear in the JSON; do not supply secrets.
There is no proxy discovery, environment inspection, wallet access, signing,
transaction, payment or posting. No coin is needed for HTTP diagnosis.

## Offline verification

```sh
python3 -B -m unittest discover -s line-1/tools/burst-sentry -v
```

Ten tests passed. They exercise mixed/all-failed outcomes, unchanged commands,
body-only changes, total-budget exhaustion, missing observations, worker errors,
strict argument validation, typed expectations and CLI exit codes. Two actual
30-second stalled child processes are killed and reaped after 80 ms each;
their printed partial success is discarded. Tests use no network or packages.
