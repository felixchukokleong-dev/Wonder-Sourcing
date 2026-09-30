# Rendering guard

## What happened

The landed-cost calculator was live, returning 200, with a correct canonical,
valid JSON-LD and 700 words of body copy. It was also **completely invisible.**

The site animates content in on scroll:

```css
.reveal    { opacity:0; transform:translateY(18px); }
.reveal.in { opacity:1; transform:none; }
```

Something has to add that `.in`. Every page carried this near `</body>`:

```js
const els = document.querySelectorAll('.reveal');
const io = new IntersectionObserver((entries)=>{
  entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
},{threshold:0.15});
els.forEach(el=>io.observe(el));
```

`landed-cost-calculator.html` was the one page of 71 missing it. Both
`div.calc-panel.reveal` (the inputs) and `div.calc-out.reveal` (the results) sat
at `opacity:0` forever. The page worked perfectly for anyone reading the HTML
source and for nobody else.

## Why the existing checks could not see it

Worth stating plainly, because it is the reason this tool exists:

| Check | Result on the broken page |
| --- | --- |
| HTTP status | 200 |
| Canonical, OG, Twitter, robots | all present |
| JSON-LD | 3 blocks, valid |
| Word count | 699 |
| Script syntax | clean |
| Broken links | none |

**Nothing that reads text can see CSS.** Every one of those checks passed while
the page was blank to a visitor.

## What the tool checks

Run from the repo root:

```bash
python3 tools/check_rendering.py           # exit 1 on any failure
python3 tools/check_rendering.py -v        # also list what was inspected
python3 tools/check_rendering.py --strict  # also fail on dead CSS
```

Three checks, across every `.html` page:

**1. Hidden forever.** A selector sets `opacity:0`, `visibility:hidden` or
`display:none` and no other rule ever restores that property. The element can
never be seen. Rules inside an `@media` block are exempt, because hiding
something on small screens is intentional.

**2. Revealed only by a class no script adds.** The element is restored solely by
an extra class — `.reveal` needing `.reveal.in` — but no inline script on the
page adds that class. This is the calculator bug exactly. A `:hover`, `:focus` or
`:target` reveal is a CSS-only path and is not flagged, which matters: the
WhatsApp button's `Chat on WhatsApp` label is hidden at `opacity:0` and revealed
by `.whatsapp-float:hover`, and a naive check would have reported 71 false
positives.

**3. JS dereference of a missing element.** `document.getElementById('x').value`
where no element has `id="x"`. That throws, killing the remainder of the script
block, so anything later in the same block silently never runs. Aliases such as
`var $ = function(id){ return document.getElementById(id); }` are followed, since
that is the pattern the calculator page uses.

Dead CSS — a hiding rule whose selector matches no element — is reported
separately and does **not** fail the build. A guard that cries wolf gets switched
off. `--strict` opts into failing on it.

## What it found on the current site

```
PASS: nothing is hidden by CSS without a way for it to appear.

Dead CSS (matches no element, so it hides nothing):
  index.html                   .burger
  landed-cost-calculator.html  .burger
```

`.burger{display:none}` is a leftover rule from a mobile menu button that is no
longer in the markup. Harmless, but safe to delete.

Both checks were verified by reintroducing the bug in a scratch copy:

| Introduced fault | Result |
| --- | --- |
| Deleted the reveal observer from the calculator page | `NO SCRIPT REVEALS IT .reveal` — revealed only by class `"in"`, which no script adds |
| Renamed `id="rows"` to `id="rowz"`, leaving the script alone | `MISSING ELEMENT $('rows').innerHTML` — no element has id `"rows"` |

Both exit 1.

## What it cannot catch

Be clear about the boundary:

- **Text that is present but wrong.** Wrong prices, broken promises, a heading
  that says the opposite of the paragraph under it.
- **Anything behind a runtime error.** If a script throws for a reason not
  visible statically — a failed `fetch`, a missing `IntersectionObserver` in an
  old browser — this tool will not know.
- **Whether the visible result is correct.** It proves content *can* appear, not
  that it appears the way you intended.
- **Layout.** Something can be visible and still overlap, overflow or sit off
  screen at one breakpoint.

For all of those the only reliable test is opening the page in a browser, on a
phone width as well as a desktop one.

## Making it automatic

There is no CI in this repo, so nothing runs this for you. A pre-push hook makes
it a gate before anything reaches production:

```bash
cat > .git/hooks/pre-push <<'HOOK'
#!/bin/sh
python3 tools/check_rendering.py || {
  echo; echo "Push blocked: fix the rendering problems above, or 'git push --no-verify'."
  exit 1
}
HOOK
chmod +x .git/hooks/pre-push
```

Hooks live in `.git/`, so they are not shared by a clone and must be installed
on each machine. If this repo ever gets a CI pipeline, the same one-liner is the
whole build step.
