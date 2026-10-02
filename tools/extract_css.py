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


def comments_ok(css):
    """No comment is left unterminated by cutting here."""
    return css.count('/*') == css.count('*/')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='verify the split without writing anything')
    a = ap.parse_args()
    os.chdir(REPO)

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
    print('  untouched pages     : %s' % [f for f in pages if f not in family])
    return 0


if __name__ == '__main__':
    sys.exit(main())