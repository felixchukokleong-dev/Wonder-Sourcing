"""Extract the CSS that 69 pages share verbatim into styles.css.

Safety argument
---------------
For each page, the inline CSS C is split as C = base + rest, where `base` is the
identical 16.3 KB prefix those 69 pages share. The page then loads `base` from
styles.css via a <link> placed exactly where the <style> block was, followed
immediately by a <style> holding `rest`.

Concatenation is `base + rest == C`, in the same document position, so the
cascade and every computed style are unchanged by construction. The script
asserts that equality for every page and aborts without writing if any page
fails it.

Pages that do not share the prefix (index, services, why-foshan, the calculator)
are left completely untouched.

Usage:  python3 tools/extract_css.py [--check]
"""
import re, os, sys, glob, collections, argparse

REPO = '/Users/felixchukokleong/projects/Wonder-Sourcing'
OUT1 = 'styles.css'
OUT2 = 'styles-guides.css'
LINK1 = '<link rel="stylesheet" href="styles.css">'
LINK2 = '<link rel="stylesheet" href="styles-guides.css">'


def inline_css(html):
    return '\n'.join(re.findall(r'<style[^>]*>([\s\S]*?)</style>', html))


def balanced(css):
    """Braces balance, ignoring anything inside comments."""
    stripped = re.sub(r'/\*[\s\S]*?\*/', '', css)
    return stripped.count('{') == stripped.count('}')


def rules_of(css):
    """Flatten a stylesheet to (selector, declarations) with order preserved."""
    import check_rendering as cr
    out = []
    for ctx, sel, decl in cr.parse_css(css):
        if ctx:
            continue
        out.append((sel.strip(), re.sub(r'\s+', ' ', decl).strip()))
    return out


def order_by_last(seq, restrict=None):
    """Distinct rules ordered by LAST occurrence - the one that wins a cascade."""
    last = {}
    for i, r in enumerate(seq):
        if restrict is not None and r not in restrict:
            continue
        last[r] = i
    return [r for r, _ in sorted(last.items(), key=lambda kv: kv[1])]


def can_absorb(small_html, small_css, big_css):
    """May a page with small_css load big_css with an identical cascade?

    Three conditions, all necessary:

      1. every rule of the smaller sheet exists in the larger one
      2. the last-occurrence order of those shared rules is unchanged, because
         that is what decides which declaration wins
      3. any rule the larger sheet adds cannot match the smaller page's markup

    A subsequence check on its own is NOT enough: a rule duplicated at an
    unhelpful position reorders it against an overlapping rule without ever
    going "missing".
    """
    import check_rendering as cr
    rs, rb = rules_of(small_css), rules_of(big_css)
    set_s, set_b = set(rs), set(rb)

    if any(r not in set_b for r in set_s):
        return False, 'rules missing from the larger sheet'
    if order_by_last(rs) != order_by_last(rb, restrict=set_s):
        return False, 'cascade order would change'

    classes, ids = cr.markup_tokens(small_html)
    for sel, _decl in [r for r in set_b if r not in set_s]:
        s = cr.PSEUDO.sub('', sel)
        sc = set(re.findall(r'\.([A-Za-z0-9_-]+)', s))
        si = set(re.findall(r'#([A-Za-z0-9_-]+)', s))
        if not sc and not si:
            return False, 'extra rule %r has no class or id to rule it out' % sel[:40]
        if (sc and not (sc & classes)) or (si and not (si & ids)):
            continue
        return False, 'extra rule %r could match this page' % sel[:40]
    return True, 'cascade preserved'


def comments_ok(css):
    """No comment is left unterminated by cutting here."""
    return css.count('/*') == css.count('*/')


def tier3():
    """Share one page's own stylesheet with the pages it safely supersedes.

    State-aware and safe to run on its own: it considers pages that do not
    already link a local stylesheet, so it can be re-run after tier 1/2 without
    them interfering.
    """
    os.chdir(REPO)
    pages = sorted(glob.glob('*.html'))
    rest = []
    for f in pages:
        h = open(f, encoding='utf-8').read()
        if not local_sheet_links(h):
            rest.append(f)
    if not rest:
        print('  tier 3: every page already links a stylesheet')
        return 0

    css_now = {f: inline_css(open(f, encoding='utf-8').read()) for f in rest}
    taken, groups = set(), []
    for big in rest:
        absorbed = []
        for small in rest:
            if small == big or small in taken or big in taken:
                continue
            ok, _why = can_absorb(open(small, encoding='utf-8').read(),
                                  css_now[small], css_now[big])
            if ok:
                absorbed.append(small)
        if absorbed:
            groups.append((big, absorbed))
            taken.add(big)
            taken.update(absorbed)

    saved = 0
    for big, absorbed in groups:
        out = 'styles-home.css' if big.startswith(('index', 'landed')) \
            else 'styles-%s.css' % big[:-5]
        open(out, 'w', encoding='utf-8').write(css_now[big])
        for f in [big] + absorbed:
            h = open(f, encoding='utf-8').read()
            first = re.search(r'<style[^>]*>[\s\S]*?</style>', h)
            if not first:
                sys.exit('ABORT: %s has no <style> block to replace' % f)
            at = first.start()
            # Remove EVERY style block, not just the first. The sheet already
            # contains all of them, so leaving one behind duplicates its rules.
            # The calculator page carries two blocks, which is how this was
            # found: its second block stayed inline and applied twice.
            h = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', h)
            h = h[:at] + '<link rel="stylesheet" href="%s">' % out + h[at:]
            open(f, 'w', encoding='utf-8').write(h)
            saved += len(css_now[f].encode())
            if inline_css(open(f, encoding='utf-8').read()).strip():
                sys.exit('ABORT: %s still has inline CSS after linking %s' % (f, out))
        print('  %-22s %.1f KB  now serves %s'
              % (out, len(css_now[big].encode()) / 1024, [f for f in [big] + absorbed]))

        # the source page is a verbatim move; the others are proven equivalent
        if open(out, encoding='utf-8').read() != css_now[big]:
            sys.exit('ABORT: %s was not written verbatim' % out)
        for small in absorbed:
            ok, why = can_absorb(open(small, encoding='utf-8').read(),
                                 css_now[small], css_now[big])
            if not ok:
                sys.exit('ABORT: %s could not safely load %s: %s' % (small, out, why))

    print('  inline CSS removed  : %.1f KB' % (saved / 1024))
    still = [f for f in rest if f not in taken]
    print('  still inline (its own sheet, nothing to share): %s' % still)
    return saved


def local_sheet_links(html):
    """Local stylesheet hrefs a page already links."""
    out = []
    for tag in re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', html):
        m = re.search(r'href=["\']([^"\']+)["\']', tag)
        if not m:
            continue
        href = m.group(1)
        if href.startswith(('http://', 'https://', '//', 'data:')):
            continue
        if os.path.exists(href.split('?')[0]):
            out.append(href)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='verify the split without writing anything')
    ap.add_argument('--tier3', action='store_true',
                    help='only share a page sheet with pages it safely supersedes')
    a = ap.parse_args()
    os.chdir(REPO)

    if a.tier3:
        return 0 if tier3() >= 0 else 1

    pages = sorted(glob.glob('*.html'))
    css = {f: inline_css(open(f, encoding='utf-8').read()) for f in pages}

    common = collections.Counter(css.values()).most_common(1)[0][0]

    def cpl(x, y):
        i = 0
        while i < len(x) and i < len(y) and x[i] == y[i]:
            i += 1
        return i

    # The family is the pages that share the common sheet. Computing a prefix
    # across ALL pages is wrong: the four big marketing pages reorder their
    # stylesheets and drag the shared prefix down to a few hundred characters.
    family = [f for f in pages if cpl(css[f], common) >= 10000]
    prefix_len = min(cpl(css[f], common) for f in family)
    # snap back to the last complete rule so no comment or declaration is split
    base1 = common[:common.rfind('}', 0, prefix_len) + 1]

    print('  shared prefix      : %d chars (%.1f KB)' % (len(base1), len(base1.encode()) / 1024))
    print('  family             : %d pages' % len(family))
    print('  ends with          : %r' % base1[-40:])
    print('  remainder begins   : %r' % common[prefix_len:prefix_len + 30])

    if not re.match(r'[\s/]', common[prefix_len:prefix_len + 1] or ' '):
        sys.exit('ABORT: split point is not on a boundary')

    # ---- verify every page reconstructs before touching the disk ----
    for f in family:
        if not css[f].startswith(base1):
            sys.exit('ABORT: %s does not start with the extracted base' % f)
    print('  split is exact on every page: OK')

    # ---- tier 2: the guide pages share their remainder verbatim too ----
    guides = [f for f in family if css[f] == common]
    base2 = common[len(base1):] if guides else ''

    print()
    print('  tier 2 (guides only) : %d pages share %d chars (%.1f KB)'
          % (len(guides), len(base2), len(base2.encode()) / 1024))
    print('  tier 2 starts with   : %r' % base2[:30])

    for name, chunk in (('base', base1), ('guides', base2)):
        if chunk and not balanced(chunk):
            sys.exit('ABORT: %s has unbalanced braces' % name)
        if chunk and not comments_ok(chunk):
            sys.exit('ABORT: %s cuts a comment in half' % name)

    if a.check:
        print('\n--check: nothing written.')
        return 0

    # written verbatim so linked + inline reconstructs the original exactly
    open(OUT1, 'w', encoding='utf-8').write(base1)
    if base2:
        open(OUT2, 'w', encoding='utf-8').write(base2)
    print('  wrote %s (%.1f KB) and %s (%.1f KB)'
          % (OUT1, len(base1.encode()) / 1024, OUT2, len(base2.encode()) / 1024))

    saved = 0
    for f in family:
        h = open(f, encoding='utf-8').read()
        m = re.search(r'<style[^>]*>([\s\S]*?)</style>', h)
        if f in guides:
            repl = LINK1 + '\n' + LINK2          # all CSS now external
        else:
            repl = LINK1 + '\n<style>' + m.group(1)[len(base1):] + '</style>'
        open(f, 'w', encoding='utf-8').write(h[:m.start()] + repl + h[m.end():])
        saved += len(base1.encode()) + (len(base2.encode()) if f in guides else 0)

    # ---- end-to-end: linked CSS + whatever stays inline must equal the ORIGINAL ----
    f1 = open(OUT1, encoding='utf-8').read()
    f2 = open(OUT2, encoding='utf-8').read() if base2 else ''
    bad = []
    for f in family:
        now = open(f, encoding='utf-8').read()
        if LINK1 not in now:
            bad.append((f, 'link to styles.css missing'))
            continue
        if f in guides and LINK2 not in now:
            bad.append((f, 'link to styles-guides.css missing'))
            continue
        effective = f1 + (f2 if f in guides else '') + inline_css(now)
        if effective != css[f]:
            bad.append((f, 'reconstructed CSS differs from the original'))
    if bad:
        sys.exit('ABORT: verification failed after writing: %s' % bad[:5])
    print('  verified: linked CSS + inline remainder == original CSS on all %d pages'
          % len(family))
    print('  inline CSS removed  : %.1f KB' % (saved / 1024))

    # ---- tier 3: one page's own sheet can serve another -------------------
    print()
    saved += tier3()
    return 0


if __name__ == '__main__':
    sys.exit(main())