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
    out.append("else if(h.indexOf('mailto:')===0)t('contact_email',{link_url:h});},true);")
    out.append("document.addEventListener('submit',function(e){var f=e.target;")
    out.append("if(f&&f.classList&&f.classList.contains('manifest-form'))t('form_submit',{form_id:'sourcing_inquiry'});},true);")
    out.append('})();</script>')
    out.append(END)
    return '\n'.join(out)

def strip(h):
    return re.sub(re.escape(START) + '[\s\S]*?' + re.escape(END) + r'\n?', '', h)

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
    for f in files:
        h = open(f, encoding='utf-8').read()
        h = strip(h)
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


if __name__ == '__main__':
    main()