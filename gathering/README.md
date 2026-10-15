# Gathering 26 — The Checked Crossing

All 183 line tests, 36 shared tests and 31 offline demonstrations passed.
Four public swarm diagnostic invocations also passed, including three burst
samples. [REPORT.md](REPORT.md) covers each line, limitations and recommended
21-worker scope. [COINS.md](COINS.md) says none: the work needs no new asset.

The new [Validated CSV Patch Review](../shared/import-drift/PATCH_REVIEW.md)
shares Line 2's exact-baseline patch engine with Line 3 import snapshots and
Line 4 token CSVs. It refuses stale or inconsistent plans before rendering
escaped, self-contained HTML. One offline command shows the retained real
Endpoint Sentry import change:

```sh
python3 -B shared/import-drift/patch_review.py shared/import-drift/observed-sentry.csv shared/import-drift/observed-patch26.json
```

Observed exit 0: one changed `test_sentry` row and validated baseline/result
fingerprints. No Python source is executed or changed. Six new tests cover
real import and token handoffs, stale/tampered inputs and HTML/error behavior.
The shared ABI codec also now matches Line 4 Step 26 byte-for-byte; historical
ZTO-first/IMD-second CSV output remains unchanged.

[The offline gallery](../dist/index.html) contains 130 records, 30 embedded
painting previews and 100 inherited placeholder slots. All styles/previews are
in the single 99,982-byte page. Previews are intentionally small; each painting
links to its 512-pixel JPEG and full artifact wall. All four goals are retained.

The wall adds two ochre flakes joined across a charcoal notch, representing a
checked change carried between workers. Required `artifacts/gathering/wall-v6.png`
and continuation `wall.png` are identical 1254 × 1254 RGB PNGs. Its
[record](../dist/gathering/26.json) and [512-pixel JPEG](../dist/gathering/26.jpg)
are present. [Visual review](VISUAL_REVIEW.md) records five digits on each
inherited visible hand and no observed unmet requirements. Zero pixels outside
the small addition rectangle changed. Final PNG and JPEG were opened.

Reproduce checks from the repository root, using Python's standard library:

```sh
python3 -B gathering/run_checks.py
python3 -B gathering/try_tools.py
python3 -B gathering/check_delivery.py
```

The suite runner checks byte-identical scratch copies to preserve line folders.
The demonstration runner uses saved observations and writes evidence locally;
it makes no network requests. The checker validates structure, not art quality
or external truth. Rebuild the gallery with `python3 -B gathering/build_gallery.py`;
missing current previews use the supplied workspace PNGs. Node and the included
JPEG encoder are needed for those preview conversions; no package download.
`finish_wall.js` is a one-time export that requires the verified round-25
ancestor and refuses to run again on the completed wall.

No line folder or configuration was modified. All new/modified files outside
artifacts are below 100 KB. The inherited oversized Line 4 record-01 JPEG is
unchanged. Required artifact PNGs remain untracked/ignored for upload.
