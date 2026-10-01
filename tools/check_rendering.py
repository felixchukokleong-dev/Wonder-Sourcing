"""Rendering guard: fails when content is hidden by CSS with nothing to reveal it.

Why this exists
---------------
The landed-cost calculator shipped invisible. Its CSS carried the site-wide
`.reveal{opacity:0}` scroll animation, but the IntersectionObserver that adds
`.in` was missing from that one page out of 71, so the panels sat at opacity 0
permanently.

Every other check passed. The page returned 200, the canonical was present, the
JSON-LD parsed, the body had 700 words. Nothing that reads text can see CSS.

Three checks, run across every .html page:

  1. UNCONDITIONAL HIDING
     A selector sets opacity:0 / visibility:hidden / display:none and no other
     rule ever restores that property, so the element can never be seen. Rules
     inside an @media block are exempt (hiding something on small screens is
     intentional), as are rules revealed by a pseudo-class.

  2. REVEAL WITHOUT A SCRIPT
     The element is restored only by an additional class - `.reveal` needing
     `.reveal.in` - but no inline script on the page ever adds that class. This
     is the calculator bug exactly. A :hover/:focus/:target reveal is a
     CSS-only path and is not flagged.

  3. JS DEREFERENCE OF A MISSING ELEMENT
     `document.getElementById('x').value` where no element has id="x". That
     throws a TypeError and kills the remainder of the script block, so anything
     later in the same block silently never runs. Aliases of the form
     `var $ = function(id){ return document.getElementById(id); }` are followed.

Exit status is 1 if any check fails, so it can gate a commit or a deploy.

Usage:
    python3 tools/check_rendering.py             # check the repo
    python3 tools/check_rendering.py -v          # also list what was inspected
    python3 tools/check_rendering.py --dir DIR   # check a different directory
"""
import re, os, sys, argparse, collections

REPO = '/Users/felixchukokleong/projects/Wonder-Sourcing'

PSEUDO = re.compile(r'::?[a-zA-Z-]+(?:\([^)]*\))?')


# --------------------------------------------------------------------------
# CSS parsing
# --------------------------------------------------------------------------
def parse_css(css):
    """Yield (media_context, selector, declarations) for every leaf rule.

    Walks braces by hand so @media nesting is tracked. Good enough for
    hand-written stylesheets; not a full CSS parser.
    """
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    rules, stack, buf, i, n = [], [], '', 0, len(css)
    while i < n:
        ch = css[i]
        if ch == '{':
            sel = buf.strip()
            buf = ''
            if sel.startswith('@'):
                stack.append(sel)
            else:
                j = css.find('}', i)
                if j == -1:
                    break
                rules.append((tuple(stack), sel, css[i + 1:j]))
                i = j  # consume the '}' without popping the media stack
        elif ch == '}':
            if stack:
                stack.pop()
            buf = ''
        else:
            buf += ch
        i += 1
    return rules


def hides(decl):
    """Which properties this declaration block hides the element with."""
    found = set()
    if re.search(r'opacity\s*:\s*0(?![.\d])', decl):
        found.add('opacity')
    if re.search(r'visibility\s*:\s*hidden', decl):
        found.add('visibility')
    if re.search(r'display\s*:\s*none', decl):
        found.add('display')
    return found


def restores(decl, prop):
    """Does this declaration block undo a hide of `prop`?"""
    m = re.search(prop + r'\s*:\s*([^;]+)', decl)
    if not m:
        return False
    val = m.group(1).strip().lower()
    if prop == 'opacity':
        return val not in ('0', '0.0')
    if prop == 'visibility':
        return val != 'hidden'
    return val != 'none'


def normalise(sel):
    """Selector -> (pseudo-free form, class tokens it requires)."""
    bare = PSEUDO.sub('', sel)
    bare = re.sub(r'\s*([>+~])\s*', r' \1 ', bare)
    bare = ' '.join(bare.split())
    return bare, set(re.findall(r'\.([A-Za-z0-9_-]+)', bare))


def split_selectors(sel):
    """'.a, .b' -> ['.a', '.b'] (naive: these sheets never nest commas)."""
    return [s.strip() for s in sel.split(',') if s.strip()]


# --------------------------------------------------------------------------
# JS inspection
# --------------------------------------------------------------------------
def js_adds_class(js, token):
    """Does any inline script add `token` as a class?"""
    t = re.escape(token)
    patterns = [
        r'classList\s*\.\s*(?:add|toggle|remove)\s*\(\s*[\'"]%s[\'"]' % t,
        r'className\s*(?:\+?=)[^;]*[\'"]\s*%s(?:\s|[\'"])' % t,
        r'setAttribute\s*\(\s*[\'"]class[\'"]',
    ]
    for p in patterns:
        if re.search(p, js):
            return True
    # token chosen dynamically, e.g. classList.add(ok ? 'in' : 'out')
    for m in re.finditer(r'classList\s*\.\s*(?:add|toggle|remove)\s*\(([^)]*)\)', js):
        if re.search(r'[\'"]%s[\'"]' % t, m.group(1)):
            return True
    return False


def js_toggles_attribute(js, attr):
    """Does any inline script add or remove this attribute on an element?

    Covers `el.hidden = false`, `removeAttribute('hidden')`,
    `toggleAttribute('hidden')` and `setAttribute('aria-hidden', ...)`. An
    element hidden by `[hidden]` in CSS and revealed by script is a legitimate
    pattern that no class-based check can see.
    """
    a = re.escape(attr)
    pats = [
        r'removeAttribute\s*\(\s*[\'"]%s[\'"]' % a,
        r'toggleAttribute\s*\(\s*[\'"]%s[\'"]' % a,
        r'setAttribute\s*\(\s*[\'"]%s[\'"]' % a,
        r'\.\s*%s\s*=' % a,
    ]
    return any(re.search(p, js) for p in pats)


def attr_tokens(bare):
    """Attribute names a selector tests, e.g. .x[hidden] -> {'hidden'}."""
    return set(re.findall(r'\[([a-zA-Z_][\w-]*)', bare))


def aliases_of_getelementbyid(js):
    """Names that resolve to document.getElementById."""
    names = set(['document.getElementById'])
    pat = (r'(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*'
           r'(?:function\s*\([^)]*\)\s*\{\s*return\s+)?document\s*\.\s*getElementById')
    names |= set(re.findall(pat, js))
    return names


def js_id_derefs(js):
    """Yield (id, expression) for every getElementById(...).prop dereference."""
    out = []
    for name in aliases_of_getelementbyid(js):
        pat = re.escape(name) + r'\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)\s*(\.\w+)'
        for m in re.finditer(pat, js):
            out.append((m.group(1), "%s('%s')%s" % (name, m.group(1), m.group(2))))
    return out


def id_set(html):
    return set(re.findall(r'\bid\s*=\s*[\'"]([^\'"]+)[\'"]', html))


def markup_tokens(html):
    """Every class token and id that actually appears in the markup."""
    classes, ids = set(), id_set(html)
    for m in re.findall(r'class\s*=\s*[\'"]([^\'"]*)[\'"]', html):
        classes |= set(m.split())
    return classes, ids


def selector_tokens(bare):
    """Class and id tokens a selector targets."""
    return (set(re.findall(r'\.([A-Za-z0-9_-]+)', bare)),
            set(re.findall(r'#([A-Za-z0-9_-]+)', bare)))


# --------------------------------------------------------------------------
# per-page analysis
# --------------------------------------------------------------------------
def analyse(path):
    html = open(path, encoding='utf-8').read()

    styles = re.findall(r'<style[^>]*>([\s\S]*?)</style>', html)
    blocks = re.findall(r'<script(?![^>]*ld\+json)[^>]*>([\s\S]*?)</script>', html)
    js = '\n'.join(b for b in blocks if b.strip())

    rules = []
    for st in styles:
        rules.extend(parse_css(st))

    # hidden selectors at top level, with the properties used to hide them
    hidden = {}   # bare selector -> (props, tokens)
    for ctx, sel, decl in rules:
        if ctx:
            continue                      # media-scoped hiding is intentional
        for one in split_selectors(sel):
            props = hides(decl)
            if props:
                bare, tokens = normalise(one)
                if bare in hidden:
                    hidden[bare][0].update(props)
                else:
                    hidden[bare] = (set(props), tokens)

    # every rule that restores one of those properties, and how it qualifies
    reveals = []
    for ctx, sel, decl in rules:
        for one in split_selectors(sel):
            bare, tokens = normalise(one)
            has_pseudo = bool(PSEUDO.search(one))
            for target, (props, ttokens) in hidden.items():
                same = bare == target
                adds = (bare.startswith(target) and tokens and ttokens
                        and tokens > ttokens)
                if (same or adds) and any(restores(decl, p) for p in props):
                    reveals.append((target, tokens, tokens - ttokens, has_pseudo))

    fails = []
    ok_css = ok_js = ok_attr = 0

    # A rule can only hide something if an element actually carries its class or
    # id. Rules that match nothing are dead CSS - worth reporting, but they are
    # not invisible content, and a guard that cries wolf gets switched off.
    classes, ids = markup_tokens(html)
    dead, live = [], {}
    for sel, (props, tokens) in hidden.items():
        sc, si = selector_tokens(sel)
        if (sc or si) and not (sc & classes) and not (si & ids):
            dead.append(sel)
        else:
            live[sel] = (props, tokens)

    for sel, (props, _tokens) in sorted(live.items()):
        rel = [r for r in reveals if r[0] == sel]
        if not rel:
            # An attribute-qualified rule - .form-fallback[hidden] - is revealed
            # by script removing the attribute, not by another CSS rule. No
            # class-based check can see that, so test it explicitly.
            attrs = attr_tokens(sel)
            if attrs and any(js_toggles_attribute(js, a) for a in attrs):
                ok_attr += 1
                continue
            fails.append(('hid', sel, 'hidden with %s and never restored'
                          % '/'.join(sorted(props))))
            continue
        if any(r[3] for r in rel):
            ok_css += 1                   # :hover / :focus / :target - no JS needed
            continue
        needed = set()
        for r in rel:
            needed |= r[2]
        if not needed:
            ok_css += 1
            continue
        missing = [t for t in sorted(needed) if not js_adds_class(js, t)]
        if missing:
            fails.append(('cls', sel,
                          'revealed only by class "%s", which no script adds'
                          % '", "'.join(missing)))
        else:
            ok_js += 1

    present = id_set(html)
    seen = set()
    for _id, expr in js_id_derefs(js):
        if _id not in present and (expr,) not in seen:
            seen.add((expr,))
            fails.append(('dom', expr, 'no element has id="%s"' % _id))

    return dict(hidden=live, dead=dead, fails=fails, ok_css=ok_css,
                ok_js=ok_js, ok_attr=ok_attr)


LABEL = {'hid': 'HIDDEN FOREVER', 'cls': 'NO SCRIPT REVEALS IT',
         'dom': 'MISSING ELEMENT'}


def main():
    ap = argparse.ArgumentParser(
        description='Fail if content is hidden by CSS with nothing to reveal it.')
    ap.add_argument('--dir', default=REPO)
    ap.add_argument('-v', '--verbose', action='store_true',
                    help='list every hidden selector that was inspected and passed')
    ap.add_argument('--strict', action='store_true',
                    help='also fail on dead CSS rules that hide nothing')
    a = ap.parse_args()

    os.chdir(a.dir)
    pages = sorted(f for f in os.listdir('.') if f.endswith('.html'))
    if not pages:
        sys.exit('No .html files in %s' % a.dir)

    total = collections.Counter()
    n_css = n_js = n_attr = 0
    failed = []
    dead_all = []
    for f in pages:
        r = analyse(f)
        n_css += r['ok_css']
        n_js += r['ok_js']
        n_attr += r['ok_attr']
        for sel in r['dead']:
            dead_all.append((f, sel))
        for kind, where, why in r['fails']:
            total[kind] += 1
            print('%-30s %-20s %s' % (f, LABEL[kind], where))
            print('%-30s %-20s   %s' % ('', '', why))
        if r['fails']:
            failed.append(f)
        elif a.verbose:
            for sel, (props, _t) in sorted(r['hidden'].items()):
                print('%-30s ok                   %s (%s)'
                      % (f, sel, '/'.join(sorted(props))))

    if dead_all:
        print('Dead CSS (matches no element, so it hides nothing):')
        for f, sel in dead_all:
            print('  %-28s %s' % (f, sel))
        print()

    print('checked %d pages - %d hidden by a pseudo-class (no JS needed), '
          '%d revealed by a class a script adds, %d revealed by a script '
          'toggling an attribute' % (len(pages), n_css, n_js, n_attr))
    if total:
        print('FAIL: %d problem(s) on %d page(s) - %s'
              % (sum(total.values()), len(failed),
                 ', '.join('%d %s' % (n, LABEL[k].lower())
                           for k, n in sorted(total.items()))))
        print()
        print('Invisible content still returns 200 and passes every check that reads')
        print('text. Open these pages in a browser before dismissing this.')
        return 1
    if dead_all and a.strict:
        print('FAIL (--strict): %d dead CSS rule(s) hiding nothing.' % len(dead_all))
        return 1
    print('PASS: nothing is hidden by CSS without a way for it to appear.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
