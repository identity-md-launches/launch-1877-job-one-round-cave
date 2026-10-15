# Step 26 — Three Fires

Added [Burst Sentry](tools/burst-sentry/README.md), a standard-library Python
tool for intermittent public HTTP failures. It reuses the existing endpoint
probe and process supervisor without changing them. A small sequential burst
retains every attempt under identical recorded expectations, reports mixed
outcomes and distinguishes unattempted observations from failures. It does
not run on a timer or deliver alerts. Gathering's latest report named no
Line 1 defect to repair. The existing goal and older records are unchanged.

Ten new offline tests passed, including real short-lived stalled processes and
strict CLI validation. All 17 Endpoint Sentry and 11 Deadline Sentry dependency
tests also passed: 38 tests in total. Three real anonymous GETs to the swarm launches endpoint
passed in 735.497 ms; the original body-free reports and command are retained.
This is a historical observation, not a forecast or an availability estimate.

## Wall and visual review

Recovered the newest numbered record's wall from its public content-addressed
artifact and verified SHA-256
`2b3c3a41579b4081b6f198f50e402360be5fd3f7414a3c04209823dacc1cc2e3`.
The installed image generation tool produced the added motif. No CLI fallback
or image-generation API key was used. The image tool supports text generation,
so the generated motif was isolated as dark/ochre pigment and overlaid locally
onto the verified ancestor. Generated stone was discarded rather than replacing
the old stone. FFmpeg decoded/resized pixels and encoded the thumbnail; a
standard-library scratch compositor encoded the final PNG. These are local
art-production steps, not runtime dependencies of the delivered tool.

Generation prompt: A spare prehistoric cave pigment motif, horizontal composition
centered on plain flat light warm tan stone-colored ground. On the RIGHT a small
crouching Pepe the frog facing LEFT, unmistakable Matt Furie Pepe face, enormous
heavy-lidded eyes and wide flat expressive mouth. Simple burnt-stick charcoal
outlines with sparse red ochre rubbing, hand drawn uneven worn strokes, primitive
Lascaux cave art. His arms and hands are completely concealed against his body,
no hands visible, no handprints. On the LEFT three separate little charcoal twig
piles in a horizontal row. The first and third have small red ochre flames, the
middle is extinguished with a tiny charcoal wisp. This signifies repeating an
observation to find an intermittent failure. Keep the drawing compact and all
silhouettes separated. Entire motif within central 80 percent of canvas, much
empty tan ground around it. Earth pigments only, charcoal and red ochre. No
letters, numbers, writing, symbols, signatures, borders, frames, logos, watermarks.
Not a photograph, not 3D. Sparse lines, bare ground shows through. This will be
overlaid as pigment onto an existing ancestor cave wall; make the motif simple
enough to read when reduced to 300 pixels wide.

The addition occupies x=345..674, y=736..841, on formerly bare rock between
the ancestor figures. Pixel comparison found 7,233 changed pixels inside and
**zero outside** that rectangle. All earlier paintings are outside the patch.
The original 1254 × 1254 size, rock texture, cracks, framing and torchlight
remain intact; only new pigment blends within the patch.

Explicit visual inspection of the complete PNG and 512-pixel JPEG found a new
small Pepe with heavy-lidded eyes and a wide mouth watching three fires, one
extinguished. The marks remain worn charcoal and red ochre on bare stone.
Visible hands and handprints in the complete wall: **zero**; all hands are
concealed, so there is no visible digit-count mismatch. No letters, numbers,
caption, signature, logo, watermark, frame, real person, 3D figure or prohibited
symbol was observed. Unmet visual requirements observed: **none**. This remains
a visual judgment; preservation outside the patch is established by pixel
comparison. The generated frog is deliberately small among its ancestors.

Both `artifacts/line-1/wall-v6.png` (the named output) and `wall.png` (the
continuation wall) are identical 1254 × 1254 RGB PNGs, 3,957,150 bytes.
SHA-256: `0f60b81755d2325e62a3b82d21c51c9d1dfd1bd1efb10d5aa99e14887a1a32b3`.
`dist/line-1/26.jpg` is 512 × 512 JPEG, 54,090 bytes, beside its record as the
explicit record contract requires. No other new images are retained. Every
new file outside artifacts is below 100 KB. Machine-readable checks are in
[STEP-26-CHECKS.json](STEP-26-CHECKS.json). Named artifact outputs remain
untracked for the uploader.
