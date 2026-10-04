# Site tools

Scripts in this directory that generate or repair parts of the site. Run them
from the repository root. Each is idempotent unless noted, so re-running one is
safe.

| Tool | What it does | When to run it |
| --- | --- | --- |
| `check_rendering.py` | Fails if content is hidden by CSS with nothing to reveal it | Before every push — a pre-push hook runs it |
| `build_sitemap.py` | Rebuilds `sitemap.xml` from the files that exist | After adding or removing any page |
| `build_legal.py` | Regenerates `privacy-policy.html` and `terms.html` from the site shell | After editing the wording in the script |
| `extract_css.py` | Moves the CSS shared across pages into `styles.css` / `styles-guides.css` | Only after adding pages that share the existing sheet |
| `internal_links.py` | Regenerates the "Related guides" blocks on every article | After adding or removing an article |
| `set_analytics.py` | Injects or removes the GA4 block and event tracking | After changing the measurement ID |
| `optimize_images.py` | Builds responsive image variants from source photographs | After adding source images |

## The two that guard the build

```bash
python3 tools/check_rendering.py --strict   # exit 1 on any problem
python3 tools/build_sitemap.py --check      # exit 1 if the sitemap is stale
```

Both exit non-zero on failure, so they can gate a deploy. There is no CI in this
repository; a pre-push hook runs the rendering guard (see `RENDERING-GUIDE.md`).
Hooks live in `.git/`, so a new clone needs one installed.

## Why these are generated rather than hand-maintained

`sitemap.xml` and the legal pages were both hand-maintained at different points
and both drifted:

- the sitemap reached 93 URLs, of which 25 pointed at pages that did not exist,
  and every URL carried the same blanket `lastmod`
- `blog.html` and `sitemap.xml` were each reverted twice by uploads from local
  copies that predated the changes on `main`

Generating them means the output is derived from the files that are actually
present, and cannot disagree with them.

`build_legal.py` reads `contact.html` and reuses its head, nav, footer,
stylesheet and analytics block. That is deliberate: hand-copying a page shell is
how the calculator page ended up missing a script that the other 70 pages had.

## Extracting shared CSS

`extract_css.py` moved 1.4 MB of duplicated CSS out of the pages and into two
cached files, taking the average page from 37.8 KB to 18.9 KB. It works by
splitting each page's inline CSS at a rule boundary:

```
original inline CSS  ==  styles.css  +  styles-guides.css  +  what stays inline
```

Because the concatenation and its position in `<head>` are unchanged, the
cascade and every computed style are identical. The script asserts that equality
against the original for all 69 pages before and after writing, and aborts
without writing if any page fails, if a chunk has unbalanced braces, or if the
cut would split a comment.

**If you add a new page**, check whether it shares the existing sheet. If it
does, re-run `extract_css.py`; if it has its own CSS, leave it inline.

### Sharing one page's sheet with another (tier 3)

`index.html`, `services.html`, `why-foshan.html` and `landed-cost-calculator.html`
reorder their stylesheets relative to the shared sheet, so they cannot reuse it.
Two of them can still share with each other:

```bash
python3 tools/extract_css.py --tier3
```

This looks for a pair where one page's sheet is a safe superset of another's, and
gives them a single file. Today that found `index.html` (137 rules) inside
`landed-cost-calculator.html` (163 rules), so both now load `styles-home.css`.

"It is a superset" is not enough to be safe. `can_absorb()` requires three things:

1. every rule of the smaller sheet exists in the larger one
2. the **last-occurrence order** of those shared rules is unchanged — that is
   what decides which declaration wins
3. every rule the larger sheet adds cannot match the smaller page's markup

Condition 2 is the one that is easy to get wrong. An earlier version checked
only that the smaller sheet's rules appeared somewhere in the larger one as an
ordered subsequence. That is *not* sufficient: a rule repeated at an unhelpful
position reorders it against an overlapping rule without anything ever going
missing. Compare rules by last occurrence, not by first match.

Tier 3 also removes **every** `<style>` block, not just the first.
`landed-cost-calculator.html` carried two, and replacing only the first left its
second block inline and applied twice — harmless in that case because the
declarations were identical, but wrong.

`services.html` and `why-foshan.html` keep their CSS inline. Nothing safely
absorbs them, and since their CSS is unique to them, a separate file would be an
extra request for no caching benefit.

### Result

```
                    before      after
styles.css            -        14.9 KB  ->  69 pages
styles-guides.css     -         7.0 KB  ->  56 pages
styles-home.css       -        20.4 KB  ->   2 pages
inline CSS         1,547 KB      89 KB         55% -> 7%
total HTML         2,793 KB   1,342 KB
average page        37.8 KB    18.4 KB
```

**The guard reads linked stylesheets.** `check_rendering.py` follows local
`<link rel="stylesheet">` tags, so `.reveal` hiding in `styles-guides.css` is
still checked on every page that loads it. Without that, the guard would have
gone quiet on 56 pages while continuing to report PASS — worth remembering if
the CSS is ever restructured again. Dead-CSS reporting deliberately stays on
page-local rules only, since a selector in a shared sheet is expected to match
nothing on most of the pages that load it.

## Adding a page

1. Write it, or generate it
2. Run `python3 tools/build_sitemap.py`
3. Run `python3 tools/internal_links.py` if it is an article
4. Run `python3 tools/check_rendering.py --strict`
5. Commit and push — the hook re-checks on the way out
