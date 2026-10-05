"""Build privacy-policy.html and terms.html from the site's own page shell.

Both pages are assembled from contact.html rather than hand-written, so the
head, nav, footer, stylesheet and analytics block are identical to every other
page by construction. Hand-copying that shell is how the calculator page ended
up missing a script the other 70 pages had.

Usage:  python3 tools/build_legal.py
"""
import re, os, json, html

REPO = '/Users/felixchukokleong/projects/Wonder-Sourcing'
SHELL = 'contact.html'
SITE = 'https://www.wondersourcing.com/'

EMAIL = 'hello@wondersourcing.com'
PHONE = '+86 189 4131 5597'
UPDATED = '30 September 2026'

PAGES = []

# ---------------------------------------------------------------- privacy ----
PAGES.append(dict(
    file='privacy-policy.html',
    title='Privacy Policy — Wonder Sourcing',
    description=('How Wonder Sourcing handles personal data: what we collect '
                 'through our website and enquiry forms, why, who we share it '
                 'with, and the rights you have across Southeast Asia.'),
    crumb='Privacy Policy',
    eyebrow='Legal',
    h1='Privacy policy',
    lede=('What we collect when you use this website or send us an enquiry, why '
          'we hold it, and what you can ask us to do with it.'),
    body='''
      <div class="legal">
        <p class="updated">Last updated: {updated}</p>

        <h2>Who is responsible for your data</h2>
        <p>The data controller is <strong>Wonder Sourcing Limited</strong>, operating from Chancheng District,
        Foshan, Guangdong, China. For any question about this policy or about
        your data, write to <a href="mailto:{email}">{email}</a>.</p>

        <h2>What we collect</h2>
        <p><strong>What you send us.</strong> When you use the enquiry form, email
        us or message us on WhatsApp, we receive whatever you choose to include.
        The enquiry form collects your company name, your country, the product
        category you are sourcing, your estimated monthly volume, and your project
        details. If you email or message us, we receive your email address or
        phone number and anything else in that message.</p>

        <p><strong>What is collected automatically.</strong> We use Google
        Analytics 4 to understand how the site is used: which pages are read,
        roughly where visitors connect from, and which device or browser is used.
        Google Analytics sets cookies and records your IP address. See
        &ldquo;Analytics and cookies&rdquo; below.</p>

        <p>We do not ask for, and do not want, special category data such as
        health, biometric or political information. Please do not send it.</p>

        <h2>Why we use it, and on what basis</h2>
        <ul>
          <li><strong>To answer your enquiry and quote for work</strong> &mdash;
          because you asked us to, and to take steps towards a contract.</li>
          <li><strong>To run and improve the website</strong> &mdash; on the basis
          of our legitimate interest in understanding what is useful and what is
          not.</li>
          <li><strong>To keep records of enquiries and orders</strong> &mdash; on
          the basis of our legitimate interest in operating the business, and to
          meet accounting and legal obligations.</li>
        </ul>
        <p>Where the law requires consent for a particular use, we will ask for it
        separately and you can withdraw it at any time.</p>

        <h2>Analytics and cookies</h2>
        <p>We use Google Analytics 4 (measurement ID G-VTRDBDYT7Y). It helps us
        see which guides are read and how buyers reach us. Google Analytics sets
        first-party cookies in your browser and processes your IP address.</p>
        <p>You can refuse or remove analytics cookies through your browser
        settings, and Google offers a browser add-on that opts you out of Google
        Analytics across every site that uses it. Blocking analytics does not
        prevent you from using any part of this site.</p>

        <h2>Who we share it with</h2>
        <p>We do not sell your personal data, and we do not share it for anyone
        else&rsquo;s marketing. We share it only with the service providers that
        make the site and our work possible:</p>
        <ul>
          <li><strong>Google</strong> &mdash; analytics.</li>
          <li><strong>Vercel</strong> &mdash; website hosting.</li>
          <li><strong>Our email provider</strong> &mdash; where your enquiry
          arrives and is stored.</li>
          <li><strong>Factories and inspectors</strong> &mdash; but only where
          doing so is necessary to quote for or carry out work you have asked us
          to do, and only the details needed for that.</li>
        </ul>
        <p>We may also disclose information where we are legally required to, or
        to establish or defend a legal claim.</p>

        <h2>Where your data goes</h2>
        <p>We are based in China and our service providers operate
        internationally, so your information may be stored or processed outside
        your own country &mdash; including in China, the United States and the
        European Union. Where data moves out of a jurisdiction that restricts
        transfers, we rely on the safeguards those providers put in place, such as
        standard contractual clauses.</p>

        <h2>How long we keep it</h2>
        <p>Enquiries that do not lead to work are kept for up to two years, so we
        can pick up a conversation you may return to. Records connected to actual
        orders are kept for as long as we are required to keep business and
        accounting records. Analytics data is retained according to the period set
        in our Google Analytics configuration. You can ask us to delete anything
        sooner &mdash; see below.</p>

        <h2>Keeping it secure</h2>
        <p>The site is served over HTTPS. Access to enquiry records is limited to
        the people who need them to do the work. No system is perfectly secure,
        and we cannot promise absolute security, but we keep the amount of data we
        hold to what the purpose requires.</p>

        <h2>Your rights</h2>
        <p>Depending on where you live, you may have the right to:</p>
        <ul>
          <li>ask for a copy of the personal data we hold about you;</li>
          <li>have inaccurate data corrected;</li>
          <li>ask us to delete data we no longer need;</li>
          <li>object to, or ask us to restrict, processing based on our
          legitimate interests;</li>
          <li>withdraw consent you previously gave;</li>
          <li>receive certain data in a portable format;</li>
          <li>complain to your local data protection regulator.</li>
        </ul>
        <p>To exercise any of these, email
        <a href="mailto:{email}">{email}</a>. We will respond within 30 days, and
        will tell you if we need longer. This policy is written to meet the
        requirements we are most likely to be held to across our markets &mdash;
        Singapore&rsquo;s PDPA, Malaysia&rsquo;s PDPA, Thailand&rsquo;s PDPA,
        Indonesia&rsquo;s PDP Law, the Philippines&rsquo; Data Privacy Act and
        Vietnam&rsquo;s PDPD &mdash; along with the GDPR for any visitor from the
        EU or UK.</p>

        <h2>Children</h2>
        <p>This site is for business buyers. It is not directed at children, and
        we do not knowingly collect data from them.</p>

        <h2>Links to other sites</h2>
        <p>Our pages link to services we do not control, such as WhatsApp. Once
        you follow a link off this site, that provider&rsquo;s own privacy policy
        applies, not this one.</p>

        <h2>Changes to this policy</h2>
        <p>If we change how we handle personal data we will update this page and
        the date at the top. Material changes affecting existing enquiries will be
        communicated directly.</p>

        <h2>Contact</h2>
        <p class="legal-contact">Wonder Sourcing Limited<br>
        Chancheng District, Foshan, Guangdong, China<br>
        <a href="mailto:{email}">{email}</a> &middot; {phone}</p>
      </div>
'''.format(updated=UPDATED, email=EMAIL, phone=PHONE),
))

# ------------------------------------------------------------------ terms ----
PAGES.append(dict(
    file='terms.html',
    title='Terms of Use — Wonder Sourcing',
    description=('The terms that apply to this website, and what our sourcing, '
                 'auditing and inspection work does and does not promise buyers '
                 'from Foshan, China.'),
    crumb='Terms of Use',
    eyebrow='Legal',
    h1='Terms of use',
    lede=('The rules that apply to this website, and the limits of what our '
          'sourcing and quality work can promise.'),
    body='''
      <div class="legal">
        <p class="updated">Last updated: {updated}</p>

        <h2>About these terms</h2>
        <p>This website is operated by <strong>Wonder Sourcing Limited</strong>, based in Chancheng District,
        Foshan, Guangdong, China. By using the site you accept these terms. If
        you do not accept them, please do not use the site.</p>
        <p>These terms cover <strong>the website</strong>. Work we carry out for
        you &mdash; sourcing, factory auditing, inspection, consolidation &mdash;
        is governed by the agreement we sign with you, and where the two differ,
        that agreement prevails.</p>

        <h2>Information on this site is general, not an offer</h2>
        <p>Our guides, market pages and cost explanations are written to help
        buyers understand how sourcing from China works. They are general
        information, not advice for your particular order, and nothing on this
        site is an offer capable of acceptance.</p>
        <p>Figures need particular care. Import duty rates, destination tax rates,
        freight costs, lead times and minimum order quantities all change, differ
        by product and HS code, and depend on details only you and your customs
        broker have. The calculator on this site uses rates pre-filled as
        <em>examples</em> for illustration. Confirm anything that matters with
        your own broker before you rely on it or quote it onward.</p>

        <h2>What our work does and does not promise</h2>
        <p>We act as your sourcing agent. We do not manufacture anything, and we
        are not the seller of the furniture.</p>
        <ul>
          <li><strong>Verification is due diligence, not a guarantee.</strong>
          When we audit a factory or check a business licence, we report what we
          find through the checks we agreed. That reduces your risk; it does not
          remove it, and it is not a warranty of any factory&rsquo;s future
          conduct.</li>
          <li><strong>Inspection is sampling.</strong> Pre-shipment inspection
          checks a sample of the order against an agreed specification and
          standard. It substantially lowers the chance of defects reaching you.
          It does not inspect every unit, and it cannot.</li>
          <li><strong>Specifications are yours to approve.</strong> Product
          quality is judged against the sample, drawing and tolerances you sign
          off. If a specification is silent on something, that thing is not
          controlled.</li>
          <li><strong>Third parties can fail.</strong> Factories miss dates,
          shipping lines roll sailings, customs holds containers. We work to
          prevent these and to resolve them quickly, but we cannot guarantee
          outcomes controlled by others.</li>
        </ul>

        <h2>Content accuracy and availability</h2>
        <p>We try to keep this site accurate and current, and we correct errors
        when we find them. We do not warrant that every page is complete, current
        or error-free, and we may change, suspend or remove any part of the site
        at any time.</p>

        <h2>Intellectual property</h2>
        <p>The text, design, code and branding on this site belong to Wonder
        Sourcing Limited or are used with permission. You are welcome to read,
        print and share our guides for your own business purposes. Please do not
        republish them wholesale as your own, or use our branding in a way that
        suggests a relationship that does not exist. Product images and
        specifications belonging to factories or brands remain theirs.</p>

        <h2>Links we do not control</h2>
        <p>We link to outside services such as WhatsApp and to third-party sites.
        We do not control them and are not responsible for their content,
        availability or how they handle your data.</p>

        <h2>Limitation of liability</h2>
        <p>To the fullest extent permitted by law, we are not liable for indirect
        or consequential losses, loss of profit, loss of business opportunity, or
        losses arising from information on this website being relied on without
        your own verification. Nothing here limits liability that cannot lawfully
        be limited, including for fraud or for death or personal injury caused by
        our negligence. Liability for work we carry out for you is dealt with in
        your service agreement, not here.</p>

        <h2>If part of these terms is unenforceable</h2>
        <p>If a provision is found unenforceable, the rest stays in force and that
        provision is read as narrowly as possible to give it effect.</p>

        <h2>Governing law</h2>
        <p>These terms are governed by the laws of the Hong Kong Special
        Administrative Region. We would much rather resolve any disagreement by
        talking first, and we will always try to.</p>

        <h2>Changes to these terms</h2>
        <p>We may update these terms; the date at the top shows the current
        version. Continuing to use the site after a change means you accept the
        updated terms.</p>

        <h2>Contact</h2>
        <p class="legal-contact">Wonder Sourcing Limited<br>
        Chancheng District, Foshan, Guangdong, China<br>
        <a href="mailto:{email}">{email}</a> &middot; {phone}</p>
      </div>
'''.format(updated=UPDATED, email=EMAIL, phone=PHONE),
))


# ----------------------------------------------------------------- build ----
LEGAL_CSS = '''
  /* ---------- legal pages ---------- */
  .legal{max-width:74ch;}
  .legal h2{font-family:var(--display);text-transform:uppercase;letter-spacing:.02em;
    font-size:21px;margin:38px 0 12px;}
  .legal h2:first-of-type{margin-top:10px;}
  .legal p{margin:0 0 14px;line-height:1.72;}
  .legal ul{margin:0 0 16px;padding-left:22px;}
  .legal li{margin-bottom:9px;line-height:1.66;}
  .legal a{color:var(--stamp);text-decoration:underline;}
  .legal .updated{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;
    text-transform:uppercase;color:var(--ink-soft);margin-bottom:26px;}
'''

FOOT_BOTTOM = '<span>© 2026 Wonder Sourcing</span>'


def e(s):
    return html.escape(s, quote=True)


def shell():
    return open(os.path.join(REPO, SHELL), encoding='utf-8').read()


def jd(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))


def build(page):
    h = shell()
    url = SITE + page['file']
    title, desc = page['title'], page['description']

    # ---- head -------------------------------------------------------------
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % e(title),
               h, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content=".*?">',
               '<meta name="description" content="%s">' % e(desc),
               h, count=1, flags=re.S)
    h = h.replace(SITE + 'contact.html', url)
    for pat, val in [
        (r'(<meta property="og:title" content=").*?(">)', e(title)),
        (r'(<meta property="og:description" content=").*?(">)', e(desc)),
        (r'(<meta name="twitter:title" content=").*?(">)', e(title)),
        (r'(<meta name="twitter:description" content=").*?(">)', e(desc)),
    ]:
        h = re.sub(pat, lambda m, v=val: m.group(1) + v + m.group(2), h, count=1)

    # ---- JSON-LD: replace WebPage + Breadcrumb, keep Organization ---------
    webpage = {"@context": "https://schema.org", "@type": "WebPage",
               "@id": url + "#webpage", "url": url, "name": title,
               "description": desc, "isPartOf": {"@id": SITE + "#website"},
               "inLanguage": "en"}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList",
             "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
                 {"@type": "ListItem", "position": 2, "name": page['crumb'],
                  "item": url}]}
    blocks = re.findall(r'<script type="application/ld\+json">\s*([\s\S]*?)\s*</script>', h)
    if len(blocks) >= 3:
        h = h.replace(blocks[1].strip(), jd(webpage), 1)
        h = h.replace(blocks[2].strip(), jd(crumb), 1)

    # ---- nav: neither legal page sits in the nav --------------------------
    h = h.replace('<li><a class="active" href="contact.html">Contact</a></li>',
                  '<li><a href="contact.html">Contact</a></li>', 1)

    # ---- styles -----------------------------------------------------------
    h = h.replace('</style>', LEGAL_CSS + '</style>', 1)

    # ---- main -------------------------------------------------------------
    start, end = h.index('<main>'), h.index('</main>')
    main = ('<main>\n\n'
            '  <section class="pagehero">\n'
            '    <div class="wrap reveal">\n'
            '      <div class="crumb"><a href="/">Home</a> / %s</div>\n'
            '      <div class="eyebrow">%s</div>\n'
            '      <h1>%s</h1>\n'
            '      <p class="lede">%s</p>\n'
            '    </div>\n'
            '  </section>\n\n'
            '  <section>\n'
            '    <div class="wrap reveal">\n%s\n    </div>\n'
            '  </section>\n\n'
            % (e(page['crumb']), e(page['eyebrow']), e(page['h1']),
               e(page['lede']), page['body']))
    h = h[:start] + main + h[end:]

    # ---- footer links -----------------------------------------------------
    h = h.replace(FOOT_BOTTOM,
                  FOOT_BOTTOM + '\n      <span><a href="privacy-policy.html">Privacy</a> '
                  '&middot; <a href="terms.html">Terms</a></span>', 1)
    return h


def main():
    os.chdir(REPO)
    for page in PAGES:
        out = build(page)
        open(page['file'], 'w', encoding='utf-8').write(out)
        body = out[out.index('<main>'):out.index('</main>')]
        body = re.sub(r'<(script|style)[^>]*>[\s\S]*?</\1>', ' ', body, flags=re.S)
        words = len(re.sub('<[^>]*>', ' ', body).split())
        print('  %-24s %3d words   title %2d chars' % (page['file'], words, len(page['title'])))


if __name__ == '__main__':
    main()

