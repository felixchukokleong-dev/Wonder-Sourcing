# Images

## Current state

The site had **zero images** until the brand stat cards were added. That is still
the single biggest gap in the SEO audit: no photographs means no visual proof of
the factories, inspections or containers, no Google Images traffic, and weaker
engagement on a product category that is bought with the eyes.

### What exists now

`images/` holds the five branded stat cards, in two widths each:

| File | Size | Used on |
| --- | --- | --- |
| `stat-1-3000-factories-*.webp` | 540 / 1080 | `why-foshan.html` |
| `stat-2-240-audited-*.webp` | 540 / 1080 | `why-foshan.html` |
| `stat-3-inspections-*.webp` | 540 / 1080 | `why-foshan.html` |
| `stat-4-6-countries-*.webp` | 540 / 1080 | `why-foshan.html` |
| `stat-5-12-years-*.webp` | 540 / 1080 | `why-foshan.html` |

They appear as a swipeable "By the numbers" rail above the closing CTA on
`why-foshan.html`. Total 222 KB for all ten files, down from 551 KB of source
JPEG — and they are served responsively, so a phone only downloads the 540w set.

### What is still missing: real photographs

Those cards are graphics that restate numbers already on the page. They do not
replace photography. **You still need real photos**, and only you can take them.

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
