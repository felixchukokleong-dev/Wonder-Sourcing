"""Adds a "Related guides" block to every article (internal linking pass).

Reuses the section groupings and card blurbs already curated in blog.html, so
anchor text and descriptions stay consistent with the blog index.

Per article: 3 sibling articles from its own blog.html section (rotated, so
every article RECEIVES links rather than only the first few), plus curated
cross-section links.

Idempotent: wraps output in <!-- ws:related:start/end --> markers and strips
the previous block before re-inserting, so it is safe to re-run and tune.

Usage:  python3 tools/internal_links.py
"""
import re, os, html, collections, json

os.chdir('/Users/felixchukokleong/projects/Wonder-Sourcing')
START='<!-- ws:related:start -->'; END='<!-- ws:related:end -->'
ANCHOR='  <section class="cta-strip">'
c=html.escape

# ---------- card metadata from blog.html ----------
bh=open('blog.html',encoding='utf-8').read()
cards={}; cur=None
for m in re.finditer(r'<div class="blog-section-label">(.*?)</div>|<a class="blog-card" href="([^"]+)">\s*<div class="cat">(.*?)</div>\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>',bh,re.S):
    if m.group(1) is not None:
        cur=html.unescape(m.group(1).strip()); continue
    cards[m.group(2)]=dict(cat=html.unescape(m.group(3).strip()), title=html.unescape(re.sub('<[^>]*>','',m.group(4)).strip()),
                           desc=html.unescape(re.sub('<[^>]*>','',m.group(5)).strip()), section=cur)
clusters=collections.defaultdict(list)
for href,meta in cards.items(): clusters[meta['section']].append(href)

SINGLETON_RELATED={
 'sourcing-dining-tables-chairs-china.html':['hotel-hospitality-furniture-procurement-guide.html','choosing-furniture-materials-for-export.html','minimum-order-quantity-furniture-china.html','furniture-factory-vetting-checklist.html'],
 'furniture-sourcing-guide-interior-designers.html':['hotel-hospitality-furniture-procurement-guide.html','custom-furniture-manufacturing-oem-odm.html','choosing-furniture-materials-for-export.html','what-is-lecong-furniture-city.html'],
 'fsc-certification-sustainable-furniture-sourcing.html':['choosing-furniture-materials-for-export.html','rattan-outdoor-furniture-sourcing-foshan.html','furniture-factory-vetting-checklist.html','building-long-term-factory-relationships.html'],
 'how-to-pay-furniture-factory-china-safely.html':['understanding-fob-pricing-furniture.html','avoid-furniture-sourcing-scams-china.html','building-long-term-factory-relationships.html','incoterms-furniture-importers-guide.html'],
 'multi-country-furniture-distribution-sourcing.html':['how-to-consolidate-factory-orders.html','lcl-vs-fcl-furniture-shipping.html','furniture-import-duties-southeast-asia.html','importing-furniture-into-singapore.html'],
 'furniture-sourcing-glossary-import-terms.html':['incoterms-furniture-importers-guide.html','understanding-fob-pricing-furniture.html','lcl-vs-fcl-furniture-shipping.html','furniture-import-duties-southeast-asia.html'],
}
EXTRA={
 'understanding-fob-pricing-furniture.html':['how-to-pay-furniture-factory-china-safely.html','furniture-sourcing-glossary-import-terms.html'],
 'minimum-order-quantity-furniture-china.html':['sourcing-dining-tables-chairs-china.html','how-to-pay-furniture-factory-china-safely.html'],
 'custom-furniture-manufacturing-oem-odm.html':['furniture-sourcing-guide-interior-designers.html'],
 'avoid-furniture-sourcing-scams-china.html':['how-to-pay-furniture-factory-china-safely.html'],
 'building-long-term-factory-relationships.html':['fsc-certification-sustainable-furniture-sourcing.html'],
 'how-to-source-furniture-from-foshan-china.html':['furniture-sourcing-glossary-import-terms.html','fsc-certification-sustainable-furniture-sourcing.html'],
 'lcl-vs-fcl-furniture-shipping.html':['multi-country-furniture-distribution-sourcing.html'],
 'how-to-consolidate-factory-orders.html':['multi-country-furniture-distribution-sourcing.html'],
 'incoterms-furniture-importers-guide.html':['furniture-sourcing-glossary-import-terms.html'],
 'furniture-import-duties-southeast-asia.html':['furniture-sourcing-glossary-import-terms.html','multi-country-furniture-distribution-sourcing.html'],
 'furniture-shipping-costs-explained.html':['how-to-pay-furniture-factory-china-safely.html'],
 'choosing-furniture-materials-for-export.html':['fsc-certification-sustainable-furniture-sourcing.html','sourcing-dining-tables-chairs-china.html'],
 'rattan-outdoor-furniture-sourcing-foshan.html':['fsc-certification-sustainable-furniture-sourcing.html'],
 'hotel-hospitality-furniture-procurement-guide.html':['sourcing-dining-tables-chairs-china.html','furniture-sourcing-guide-interior-designers.html'],
 'sourcing-furniture-for-airbnb-short-term-rentals.html':['sourcing-dining-tables-chairs-china.html','furniture-sourcing-guide-interior-designers.html'],
 'furniture-factory-vetting-checklist.html':['fsc-certification-sustainable-furniture-sourcing.html'],
 'common-furniture-defects-qc.html':['fsc-certification-sustainable-furniture-sourcing.html'],
 'importing-furniture-into-singapore.html':['multi-country-furniture-distribution-sourcing.html'],
 'importing-furniture-into-malaysia.html':['multi-country-furniture-distribution-sourcing.html'],
}

RELATED={}
for sec,members in clusters.items():
    N=len(members)
    for i,a in enumerate(members):
        if a in SINGLETON_RELATED:
            RELATED[a]=SINGLETON_RELATED[a]; continue
        if N<4:
            RELATED[a]=[m for m in members if m!=a][:5] or []; continue
        pick=[]
        for t in [members[(i+1)%N],members[(i+2)%N],members[(i+3)%N]]+EXTRA.get(a,[]):
            if t!=a and t not in pick: pick.append(t)
        RELATED[a]=pick[:5]

CARD='''        <a href="%s" style="display:block;border:1px solid var(--line);background:var(--white);padding:18px 20px;text-decoration:none;color:inherit;">
          <span style="display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--stamp);margin-bottom:9px;">%s</span>
          <span style="display:block;font-family:var(--display);text-transform:uppercase;letter-spacing:.02em;font-weight:600;line-height:1.12;font-size:16px;">%s</span>
          <span style="display:block;margin-top:9px;font-size:13px;line-height:1.5;color:var(--ink-soft);">%s</span>
        </a>'''

def block(a):
    sec=cards[a]['section']; N=len(clusters[sec])
    heading='More on '+c(sec.lower()) if (N>=4 and a not in SINGLETON_RELATED) else 'Related guides'
    inner='\n'.join(CARD % (t, c(cards[t]['cat']), c(cards[t]['title']), c(cards[t]['desc'])) for t in RELATED[a] if t in cards)
    return (START+'\n  <section class="related-guides" style="padding:52px 0 4px;">\n    <div class="wrap">\n'
            '      <div class="eyebrow">Related guides</div>\n'
            '      <h2 style="margin:14px 0 24px;font-size:27px;">'+heading+'</h2>\n'
            '      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(248px,1fr));gap:14px;">\n'
            +inner+'\n      </div>\n    </div>\n  </section>\n'+END+'\n')

def strip(h): return re.sub(re.escape(START)+r'[\s\S]*?'+re.escape(END)+r'\n?','',h)

n=0; skipped=[]
for a in sorted(RELATED):
    h=open(a,encoding='utf-8').read(); h0=h
    h=strip(h)
    if h.count(ANCHOR)!=1:
        skipped.append(a); continue
    h=h.replace(ANCHOR, block(a)+ANCHOR, 1)
    if h!=h0: open(a,'w',encoding='utf-8').write(h); n+=1
print('related blocks inserted:',n)
print('skipped:',skipped)
