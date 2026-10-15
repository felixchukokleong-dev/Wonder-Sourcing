"""Inject GA4 + Search Console verification + conversion tracking into all pages.

Usage:
    python3 set_analytics.py --ga4 G-XXXXXXXXXX --gsc abc123token          # apply
    python3 set_analytics.py --ga4 G-XXXXXXXXXX --dry-run                  # preview only
    python3 set_analytics.py --remove                                      # strip everything

Idempotent: re-running replaces the previous block instead of duplicating it.
"""
import re, os, sys, argparse, html

REPO = '/Users/felixchukokleong/projects/Wonder-Sourcing'
START = '<!-- ws:analytics:start -->'
END = '<!-- ws:analytics:end -->'

def build(ga4, gsc):
    out = [START]
    if gsc:
        out.append('<meta name="google-site-verification" content="%s">' % html.escape(gsc, quote=True))
    if ga4:
        out.append('<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>' % ga4)
        out.append('<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
                   "gtag('js',new Date());gtag('config','%s');</script>" % ga4)
    out.append('<script>(function(){')
    out.append("function t(n,p){if(typeof gtag==='function')gtag('event',n,p||{});}")
    out.append("document.addEventListener('click',function(e){var a=e.target&&e.target.closest?e.target.closest('a[href]'):null;")
    out.append("if(!a)return;var h=a.getAttribute('href')||'';")
    out.append("if(h.indexOf('wa.me')>-1)t('contact_whatsapp',{link_url:h});")
    out.append("else if(h.indexOf('mailto:')===0)t('contact_email',{link_url:h});")
    # Primary conversion micro-actions: the 'Start a brief' buttons (nav CTA and
    # cta-strip) and content-to-content hops (blog cards / related guides).
    out.append("else if(a.classList.contains('nav-cta')||a.closest('.cta-strip'))t('start_brief_click',{link_url:h});")
    out.append("else if(a.closest('.blog-card')||a.closest('.related-guides'))t('guide_click',{link_url:h});},true);")
    # NOTE: generate_lead{form_id:'sourcing_inquiry'} deliberately does NOT fire on
    # every submit. contact.html posts to Web3Forms via fetch, and the event fires
    # from handleInquirySubmit only after the POST succeeds — so GA4 counts real
    # submissions, not clicks that never left the browser.
    out.append('})();</script>')
    out.append(END)
    return '\n'.join(out)

def strip(h):
    return re.sub(re.escape(START) + '[\s\S]*?' + re.escape(END) + r'\n?', '', h)

def strip_strays(h, ga4):
    """Strip hand-written gtag snippets that live outside the managed block.

    Ten guide pages shipped with a hand-written Google tag in <head>; adding
    the managed block on top of it double-counted every pageview on those
    pages. Stray inline config scripts and gtag.js loader tags are now removed
    on every run. A stray referencing a DIFFERENT measurement ID is returned
    to the caller so it can abort instead of silently deleting another
    property's tag.
    """
    ids = set()
    def inline_cb(m):
        ids.update(re.findall(r"gtag\(\s*['\"]config['\"]\s*,\s*['\"]([A-Za-z0-9-]+)", m.group(0)))
        return ''
    # inline scripts that call gtag('config', ...) - the managed block was
    # already removed by strip() before this runs, so anything matching is stray
    h = re.sub(r'<script>(?:(?!</script>)[\s\S])*?gtag\(\s*[\'"]config[\'"](?:(?!</script>)[\s\S])*?</script>',
               inline_cb, h)
    def src_cb(m):
        q = re.search(r'id=([A-Za-z0-9-]+)', m.group(0))
        if q: ids.add(q.group(1))
        return ''
    h = re.sub(r'(?:<!--\s*Google tag \(gtag\.js\)\s*-->\s*)?'
               r'<script[^>]+src="https://www\.googletagmanager\.com/gtag/js\?id=[A-Za-z0-9-]+"[^>]*>\s*</script>\s*',
               src_cb, h)
    foreign = ids - ({ga4} if ga4 else set())
    return h, foreign, bool(ids)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ga4'); ap.add_argument('--gsc')
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--remove', action='store_true')
    ap.add_argument('--dir', default=REPO, help='directory to operate on (default: the repo)')
    a = ap.parse_args()

    if a.ga4:
        a.ga4 = a.ga4.strip()
        if not re.fullmatch(r'G-[A-Za-z0-9]{4,16}', a.ga4):
            sys.exit('ERROR: --ga4 does not look like a GA4 measurement ID.\n'
                     '       Expected the form G-AB12CD34EF (GA4 > Admin > Data streams).')
    if a.gsc:
        a.gsc = a.gsc.strip()
    if not a.remove and not (a.ga4 or a.gsc):
        sys.exit('ERROR: nothing to do - pass --ga4 and/or --gsc, or --remove.')

    os.chdir(a.dir)
    block = build(a.ga4 or '', a.gsc or '')

    files = sorted(f for f in os.listdir('.') if f.endswith('.html'))
    touched = 0
    strays = 0
    for f in files:
        h = open(f, encoding='utf-8').read()
        h = strip(h)
        h, foreign, removed = strip_strays(h, a.ga4 or '')
        if foreign and not a.remove:
            sys.exit('ERROR: %s has a hand-written gtag for a different measurement ID: %s\n'
                     '         Remove it manually, or re-run with that ID via --ga4.'
                     % (f, ', '.join(sorted(foreign))))
        if removed: strays += 1
        if a.remove:
            if h != open(f, encoding='utf-8').read():
                open(f, 'w', encoding='utf-8').write(h); touched += 1
            continue
        if '</head>' not in h:
            print('SKIP (no </head>):', f); continue
        h = h.replace('</head>', block + '\n</head>', 1)
        if '</body>' in h:
            pass  # events ride along in the head block; no body edit needed
        if a.dry_run:
            if f == 'index.html':
                print('--- would insert before </head> in all %d files ---' % len(files))
                print(block)
            touched += 1
        else:
            open(f, 'w', encoding='utf-8').write(h); touched += 1
    print(('DRY RUN: ' if a.dry_run else '') + '%d files %s' % (touched, 'stripped' if a.remove else 'updated'))
    if strays:
        print('stray hand-written gtag snippets removed from %d files' % strays)


if __name__ == '__main__':
    main()