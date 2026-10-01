# Site tools

Scripts in this directory that generate or repair parts of the site. Run them
from the repository root. Each is idempotent unless noted, so re-running one is
safe.

| Tool | What it does | When to run it |
| --- | --- | --- |
| `check_rendering.py` | Fails if content is hidden by CSS with nothing to reveal it | Before every push — a pre-push hook runs it |
| `build_sitemap.py` | Rebuilds `sitemap.xml` from the files that exist | After adding or removing any page |
| `build_legal.py` | Regenerates `privacy-policy.html` and `terms.html` from the site shell | After editing the wording in the script |
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

## Adding a page

1. Write it, or generate it
2. Run `python3 tools/build_sitemap.py`
3. Run `python3 tools/internal_links.py` if it is an article
4. Run `python3 tools/check_rendering.py --strict`
5. Commit and push — the hook re-checks on the way out
