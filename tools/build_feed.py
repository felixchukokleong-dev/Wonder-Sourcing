"""Build feed.xml — RSS 2.0 feed of every guide page that carries BlogPosting schema.

Mirrors build_sitemap.py's philosophy: generated, not hand-maintained, and
rebuildable from the files that exist. Takes the 30 most recently published
articles; descriptions only (no full text) so the feed points home rather than
competing with the pages.

Usage:  python3 tools/build_feed.py [--check]
"""
import re, os, sys, glob, json, argparse
from email.utils import format_datetime
from datetime import datetime, timezone

REPO = '/Users/felixchukokleong/projects/Wonder-Sourcing'
SITE = 'https://www.wondersourcing.com/'
LIMIT = 30

def collect():
    items = []
    for f in sorted(glob.glob('*.html')):
        if f in ('404.html', 'index.html', 'blog.html'):
            continue
        s = open(f, encoding='utf-8').read()
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                d = json.loads(b)
            except Exception:
                continue
            if d.get('@type') != 'BlogPosting':
                continue
            pub = d.get('datePublished', '')
            try:
                dt = datetime.strptime(pub, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            items.append({
                'title': d.get('headline', f),
                'link': d.get('url', SITE + f),
                'desc': d.get('description', ''),
                'pub': dt,
            })
            break  # one BlogPosting per page
    items.sort(key=lambda x: x['pub'], reverse=True)
    return items[:LIMIT]

def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;'))

def build():
    items = collect()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0">',
           '<channel>',
           '<title>Wonder Sourcing — Insights</title>',
           '<link>%sblog.html</link>' % SITE,
           '<description>Practical guides on sourcing, inspecting and shipping furniture from Foshan, China to Southeast Asia.</description>',
           '<language>en</language>',
           '<lastBuildDate>%s</lastBuildDate>' % format_datetime(datetime.now(timezone.utc))]
    for it in items:
        out += ['<item>',
                '<title>%s</title>' % esc(it['title']),
                '<link>%s</link>' % it['link'],
                '<guid isPermaLink="true">%s</guid>' % it['link'],
                '<pubDate>%s</pubDate>' % format_datetime(it['pub']),
                '<description>%s</description>' % esc(it['desc']),
                '</item>']
    out += ['</channel>', '</rss>']
    return '\n'.join(out) + '\n', len(items)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    os.chdir(REPO)
    xml, n = build()
    if a.check:
        cur = open('feed.xml', encoding='utf-8').read() if os.path.exists('feed.xml') else ''
        if cur == xml:
            print('feed.xml is current (%d items)' % n); return 0
        print('feed.xml is OUT OF DATE'); return 1
    open('feed.xml', 'w', encoding='utf-8').write(xml)
    print('feed.xml rebuilt: %d items' % n)
    return 0

if __name__ == '__main__':
    sys.exit(main())