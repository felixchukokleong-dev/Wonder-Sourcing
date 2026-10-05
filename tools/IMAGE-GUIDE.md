# Images

## Current state

Real photography is now on the site. `images/` holds the five branded stat
cards plus 18 photographs from supplier showrooms and warehouses in Foshan, in
two widths each (540w and 1080w).

| Where | Photos | What they are |
| --- | --- | --- |
| `why-foshan.html` | 8 | Showroom floors — chair rows, armchair halls, warehouse racking |
| `services.html` | 10 | Product shots plus warehouse stock and consolidation |

Both galleries use the same horizontal scroll-snap rail as the stat cards, so
no new CSS was needed. Markup lives between `<!-- ws:gallery:start/end -->`
markers, which makes the blocks safe to regenerate.

Total for all 36 photo files: **2,155 KB**, down from 2,876 KB of source JPEG.
A phone only ever downloads the 540w set — about 350 KB on `why-foshan.html`
and 390 KB on `services.html`.

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
