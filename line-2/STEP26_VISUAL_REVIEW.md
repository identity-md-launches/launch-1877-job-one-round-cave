# Step 26 — The Guarded Tablets

The completed wall is `artifacts/line-2/wall.png`, byte-identical to the required
`artifacts/line-2/wall-v6.png`. Both are opaque 1254 × 1254 RGB PNGs. The required
preview is `dist/line-2/26.jpg`, a 512 × 512 JPEG, 80,606 bytes. Digests and pixel
comparison results are in `step26-checks.json`.

Restored the exact parent from record 25 and verified its SHA-256 before adding
paint. The new mark is two irregular pebble tablets and a trail stopped by an
ochre stone. It represents a change guarded by its original baseline. It sits
below the existing figures, at x=300..659, y=950..1126. Comparison against the
parent found 32,459 changed pixels inside this rectangle and **zero** outside.
No ancestor mark was moved, erased, cleaned, or redrawn. The rock, cracks,
lighting, size, and framing are retained.

Opened the final full PNG and the JPEG for visual review. The main ancestral
Pepe retains his wide mouth, heavy-lidded eyes, and both five-digit hands
(four fingers and one thumb each); the upper-right figure's open hand also has
five digits. The other figures have no newly exposed hands. No hand or
handprint was added. New paint uses dark charcoal and ochre, with the warm rock
showing through. No letters, numbers, captions, signature, logo, watermark,
political symbol, or added frame was observed. The mark is subdued in the small
JPEG under the inherited torchlight; fine pigment details are clearer in the
PNG. No unmet visual requirement was observed. This is a human-style visual
assessment, not an independent artistic certification.

Used the assignment's installed `mcp__image__generate_image` tool. Its first
request returned `Transparent background is not supported for this model.`
The successful retry used an opaque white backdrop at the required output
path, temporarily, before compositing its pigment into the parent. White
contributes no pigment; darker colors multiply the existing rock pixels.
The generated intermediate was replaced with the finished wall. Only the
two final wall aliases and the mandated record JPEG remain as new pictures.
Node built-ins and the already-read repository-local PNG decoder/JPEG encoder
performed compositing and resizing; no dependency was installed. The delivered
CSV tool uses only Python's standard library.

Successful generation prompt:

> Use case: illustration-story / compositing. Create an isolated small cave-painting pigment motif on a pure flat white background, no rock background. A primitive charcoal and red/yellow ochre drawing of two small irregular stone tablets side by side: each tablet has three dark round pebble dots, and the right tablet has one extra red ochre pebble dot. Below them a short curved chalk trail is stopped by one ochre stone, symbolizing a reviewed change guarded against stale data. Uneven worn thumb-painted marks, Lascaux/Chauvet earth pigments, bare white spaces. No frog or human is needed in this small supplemental motif, no hands. No letters, numbers, runes, signatures, border, frame, symbols resembling text, logos, watermark. The entire motif should be centered with generous white margin and a wide horizontal composition. This will be added in empty lower-left rock on an existing Pepe cave wall without changing any ancestor painting.
