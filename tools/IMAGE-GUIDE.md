# Images

## Current state

Real photography is now on the site. `images/` holds the five branded stat
cards plus 18 photographs from supplier showrooms and warehouses in Foshan, in
two widths each (540w and 1080w). **Every image is 4:5** — 1080x1350 for the
large set, 540x675 for the small one.

| Where | Photos | What they are |
| --- | --- | --- |
| `why-foshan.html` | 8 | Showroom floors — chair rows, armchair halls, warehouse racking |
| `services.html` | 10 | Product shots plus warehouse stock and consolidation |

Both galleries use the same horizontal scroll-snap rail as the stat cards, so
no new CSS was needed. Markup lives between `<!-- ws:gallery:start/end -->`
markers, which makes the blocks safe to regenerate.

## One format, everywhere

**Every image is 4:5 — 1080x1350 at full width, 540x675 at half.** No
exceptions, including the five branded stat cards.

This is the single rule that keeps the galleries tidy. The photographs arrived
at seven different aspect ratios between 0.57 and 0.85, and because the rail
sizes cards from their intrinsic ratio, a mixed set renders with ragged,
staggered bottoms. Pinning the format means every card is the same height and
the rail reads as one set. 4:5 was chosen because the stat cards already used
it and the `why-foshan.html` gallery sits directly beneath them.

| Slug | Before | After |
| --- | --- | --- |
| `product-home-office` | 1080x1895 (0.570) | 1080x1350 (0.800) |
| `product-leather-sofa` | 1080x1854 (0.583) | 1080x1350 (0.800) |
| `product-striped-daybed` | 1080x1852 (0.583) | 1080x1350 (0.800) |
| `product-slat-bench` | 1080x1269 (0.851) | 1080x1350 (0.800) |
| `product-sculpted-sideboard` | 1080x1299 (0.831) | 1080x1350 (0.800) |
| `showroom-*` (all 8) | 1080x1440 (0.750) | 1080x1350 (0.800) |
| `stock-side-tables-carton` | 1080x1496 (0.722) | 1080x1350 (0.800) |
| `stock-side-tables-nested` | 1080x1493 (0.723) | 1080x1350 (0.800) |
| `warehouse-stock-chairs` | 1080x1560 (0.692) | 1080x1350 (0.800) |
| `stat-*` (all 5) | 1080x1350 (0.800) | unchanged |

Cropping is centred horizontally, but the **vertical anchor is tuned per
image** so the subject survives the trim. A blind centre crop on the tall
portraits pushed the daybed down and filled the frame with ceiling:

- `0.50` — most showroom shots, and the wide shots cropped at the sides
  (`product-slat-bench`, `product-sculpted-sideboard`, the two dining tables)
- `0.55` — `product-leather-sofa`, `stock-side-tables-nested`
  (biased up: furniture sits low in frame)
- `0.58` — `product-home-office`
- `0.60` — `stock-side-tables-carton`, `warehouse-stock-chairs` (biased down,
  to hold the stacked cartons rather than the ceiling)
- `0.72` — `product-striped-daybed`, to centre the bed under the tree

Reproduce with `python3 tools/optimize_images.py <source> --anchor <0-1>`. If a
crop ever looks wrong, re-run at a different anchor and eyeball the result.

> **Note on `product-slat-bench`:** the Chinese factory sign in the top-right
> runs off the edge of the *source* photo, not the crop — the source is only
> 1170px wide, so the 4:5 window only slides 70px across it and no horizontal
> anchor can rescue the text. It is left as-is: background signage bleeding off
> the frame is normal in a real warehouse photograph. Do not try to "fix" it
> with a crop anchor.

`tools/optimize_images.py` crops to this format on the way in, so a future batch
cannot reintroduce mixed ratios. The markup also carries a belt-and-braces
`aspect-ratio:4/5;object-fit:cover` so the rendered box stays correct even if a
non-conforming file ever slips past the tool. Keep the `width`/`height`
attributes equal to the real pixel size of the 1080w file — they are what
reserve layout space and stop the page jumping while images load.

Total for all 46 files (23 images x 2 widths): **2,257 KB**, down from 2,876 KB
of source JPEG. A phone only ever downloads the 540w set — about 441 KB on
`why-foshan.html` (8 photos plus the 5 stat cards) and 217 KB on `services.html`.

### What is still missing

The photography covers **showrooms and stock**, not operations. The site still
has no images of:

- a **factory floor mid-production** — the single most important missing shot
- **QC inspection in progress** — this is the claimed differentiator
- a **container being loaded** — makes consolidation tangible
- your **warehouse with palletised orders**
- a **team or inspector portrait** — E-E-A-T

Those five remain the priority. Only you can shoot them.

---

## Processing photos

```bash
# one photo
python3 tools/optimize_images.py ~/Pictures/qc-inspection.jpg --name qc-inspection

# a whole folder
python3 tools/optimize_images.py ~/Pictures/foshan-trip --name factory-floor
```

The tool resizes to 540w and 1080w, converts to WebP, strips EXIF (which matters:
photos shot in a supplier's factory often carry GPS coordinates and camera
serials) and fixes phone-photo rotation. It then prints ready-to-paste markup.

### Quality is 72, and that is deliberate

The default was 84, which suited the flat-colour stat cards. It is wrong for
photography: a showroom has gradients, shadow noise and high-frequency chair
frames, and at 84 this folder came out **larger** than the source JPEGs
(2,876 KB → 3,161 KB). At 72 it is 2,155 KB and visually indistinguishable at
display size.

If you add flat-colour graphics rather than photographs, pass `--quality 84`.

### Rename before you build

Source photos usually arrive as camera or social-media hashes
(`488523582_17904028896155371_...jpg`), which produce unusable filenames and
meaningless URLs. Rename each photo to describe its subject
(`product-leather-sofa.jpg`) before running the tool. The tool derives the
output name from the input name.

### Curate before you process

Of 24 photos supplied, 6 were dropped rather than published:

| Dropped | Why |
| --- | --- |
| Photoshoot in progress, two people holding cameras | Identifiable faces, and the subject is the shoot rather than the furniture |
| Two extreme close-ups of one metal side table | No legible subject |
| Two alternate angles of the same warehouse corner | Same scene twice |
| Close-up of a table's trestle legs | Same table already published in full |

Publishing near-duplicates dilutes a gallery and wastes bandwidth. It also
gives Google several competing candidates for the same image.

---

## Shot list

Priority order. Shoot in landscape unless noted, and avoid heavy filters — these
are meant to read as documentary evidence, not advertising.

| # | Shot | Where it goes | Why it matters |
| --- | --- | --- | --- |
| 1 | Factory floor mid-production, workers at a line | `why-foshan.html`, `services.html` | Proves you are physically there |
| 2 | Your inspector measuring/checking a piece with a clipboard or phone | `quality-control.html` | This is your differentiator; show it |
| 3 | Lecong Furniture City showroom aisle | `why-foshan.html` | Reinforces the scale claim |
| 4 | Container being loaded, boxes stacked inside | `services.html`, `how-to-consolidate-factory-orders.html` | Makes consolidation tangible |
| 5 | Your Foshan warehouse with palletised orders | `services.html` | Backs the consolidation promise |
| 6 | Upholstery/sewing line, fabric rolls | `choosing-furniture-materials-for-export.html` | Material category pages |
| 7 | Finished furniture staged for packing | home page hero area | Gives the home page a visual |
| 8 | Team photo, or an inspector's own portrait | `contact.html` | Personal trust, E-E-A-T |
| 9 | A real QC photo report (redacted client details) | `quality-control.html` | Shows the actual deliverable |

**Avoid:** stock photography. Buyers in this category are experienced importers;
generic warehouse stock images read as fake and undermine the whole positioning.

You do not need all nine at once. **Shots 1, 2 and 4 alone** would transform the
site's credibility.

---

## Processing photos

```bash
# one photo
python3 tools/optimize_images.py ~/Pictures/qc-inspection.jpg --name qc-inspection

# a whole folder
python3 tools/optimize_images.py ~/Pictures/foshan-trip --name factory-floor
```

The tool resizes to 540w and 1080w, converts to WebP, strips EXIF (which matters:
photos shot in a supplier's factory often carry GPS coordinates and camera
serials) and fixes phone-photo rotation. It then prints ready-to-paste markup.

---

## Markup pattern

Every content image should look like this. Each attribute earns its place:

```html
<img src="images/factory-floor-540.webp"
     srcset="images/factory-floor-540.webp 540w, images/factory-floor-1080.webp 1080w"
     sizes="(max-width:760px) 92vw, 560px"
     width="1080" height="1350" loading="lazy" decoding="async"
     alt="Two workers assembling oak dining chairs on the production line at a Shunde factory">
```

| Attribute | Why |
| --- | --- |
| `srcset` + `sizes` | Phones download the 540w file instead of the 1080w one — roughly half the bytes |
| `width` + `height` | Lets the browser reserve space before load. Omitting these is the classic cause of layout shift (CLS), which is a Core Web Vital |
| `loading="lazy"` | Defers offscreen images. Do **not** use it on the hero image |
| `decoding="async"` | Decodes off the main thread so text paints first |
| `alt` | Required for accessibility and for Google Images |

WebP now has universal support in browsers that matter (95%+), so no JPEG
fallback is needed.

---

## Writing alt text

Describe what is in the photo, for someone who cannot see it. Do not stuff
keywords.

- Good: `Inspector measuring the frame of an upholstered dining chair with a tape measure`
- Bad: `furniture sourcing china furniture inspection quality control foshan`
- Purely decorative (spacers, rules): use `alt=""`

---

## Adding an OG image per page (optional)

Social shares currently all use the single branded `og-image.jpg`. Once you have
real photography, a page-specific `og:image` measurably lifts click-through from
WhatsApp and LinkedIn — your main referral channels. Point
`<meta property="og:image">` at a 1200x630 crop for the important pages,
keeping the current card as the default.

---

## Image sitemap (optional)

Once the site has real photography, adding `<image:image>` entries to
`sitemap.xml` helps Google discover images it might otherwise miss. Not worth it
for the current stat cards, which are graphics rather than photos.
