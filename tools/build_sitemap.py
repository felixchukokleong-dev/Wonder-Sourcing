"""Rebuild sitemap.xml from the files that actually exist.

The sitemap is generated rather than hand-maintained because it was reverted
twice by uploads from stale local copies, and because it had drifted to 93 URLs
of which 25 pointed at pages that did not exist.

Rules:
  - every .html file except 404.html becomes a URL, and nothing else does
  - <lastmod> is the date of the last commit that touched that file, so it is
    per-page rather than one blanket date
  - priority/changefreq come from a small table, with sensible defaults

Usage:  python3 tools/build_sitemap.py [--check]

--check writes nothing and exits 1 if sitemap.xml does not match, so it can be
used as a guard.
"""
import re, os, sys, subprocess, argparse
from datetime import date

REPO = '/Users/felixchukokleong/projects/Wonder-Sourcing'
SITE = 'https://www.wondersourcing.com/'

# page -> (priority, changefreq)
KEY = {
    'services.html':              ('0.9', 'monthly'),
    'quality-control.html':       ('0.9', 'monthly'),
    'landed-cost-calculator.html': ('0.9', 'monthly'),
    'contact.html':               ('0.8', 'monthly'),
    'markets.html':               ('0.8', 'monthly'),
    'why-foshan.html':            ('0.8', 'monthly'),
    'blog.html':                  ('0.8', 'weekly'),
}
EXCLUDE = {'404.html'}


def lastmod(path):
    """Last commit date for the file, or today's date if it is not committed yet."""
    d = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', path],
                       capture_output=True, text=True).stdout.strip()
    return d or date.today().isoformat()


def build():
    files = sorted(f for f in os.listdir('.') if f.endswith('.html'))
    pages = [f for f in files if f not in EXCLUDE]
    if 'index.html' not in pages:
        sys.exit('index.html not found - refusing to write a sitemap without the homepage')

    entries = [(SITE, 'weekly', '1.0', 'index.html')]
    for f in pages:
        if f == 'index.html':
            continue
        if f in KEY:
            p, c = KEY[f]
        elif f.startswith('market-'):
            p, c = '0.7', 'monthly'
        else:
            p, c = '0.6', 'monthly'
        entries.append((SITE + f, c, p, f))

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, c, p, f in entries:
        out += ['  <url>', '    <loc>%s</loc>' % loc,
                '    <lastmod>%s</lastmod>' % lastmod(f),
                '    <changefreq>%s</changefreq>' % c,
                '    <priority>%s</priority>' % p, '  </url>']
    out.append('</urlset>')
    return '\n'.join(out) + '\n', len(entries), len(files) - len(EXCLUDE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='write nothing; exit 1 if the file is out of date')
    a = ap.parse_args()

    os.chdir(REPO)
    xml, n_urls, n_pages = build()

    if a.check:
        current = open('sitemap.xml', encoding='utf-8').read() if os.path.exists('sitemap.xml') else ''
        if current == xml:
            print('sitemap.xml is current (%d URLs)' % n_urls)
            return 0
        live = len(re.findall(r'<loc>', current))
        print('sitemap.xml is OUT OF DATE: file has %d URLs, pages need %d'
              % (live, n_urls))
        print('run: python3 tools/build_sitemap.py')
        return 1

    open('sitemap.xml', 'w', encoding='utf-8').write(xml)
    print('sitemap.xml rebuilt: %d URLs from %d content pages' % (n_urls, n_pages))
    return 0


if __name__ == '__main__':
    sys.exit(main())
