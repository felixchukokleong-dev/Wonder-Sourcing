# Analytics & Search Console setup

> **Threads social proof** (`index.html`, between `<!-- ws:threads:start -->` and
> `<!-- ws:threads:end -->`): Meta offers **no profile or feed embed**. The
> official oEmbed endpoint renders *one post at a time* and needs an app access
> token, so a live "latest posts" feed is not possible without one. What ships
> today is therefore static by design:
>
> - the follow card (handle, follower count, bio) — hand-maintained
> - two real post embeds, live as of commit `HEAD`: `/post/Ddysa9Bmphs` and
>   `/post/Ddq_rddCCYD`
>
> **To add another post:** open it on Threads → `...` → **Get embed code** →
> paste the blockquote inside its own `<div class="t-post">` at the bottom of
> the rail. The renderer script at the foot of `index.html` upgrades each
> blockquote in place. No code changes needed.
>
> **Do not paste the `<script src=.../embed.js>` tag** that Threads appends to
> its snippet — it is already loaded once at the foot of the page, and a second
> copy is wasted bytes.
>
> Each blockquote carries inline `max-width:650px`, so it is wrapped in
> `.t-post` and overridden in CSS. Without the wrapper the embed would ignore
> the rail's card width and blow the layout out to 650px.
>
> **Check the shortcode before pasting.** Threads' *Get embed code* copies the
> **most recent** post, not whichever post you have open, so it is easy to send
> the same snippet twice. Two cards with the same shortcode would also mean a
> duplicate `id="ig-tp-..."`, which is invalid HTML and can break the upgrade
> script. `grep -o 'post/Dd[a-zA-Z0-9_]*' index.html | sort | uniq -c` should
> show each shortcode exactly twice (the permalink and the `href`).
>
> **Two things to keep honest.** The follower count in `.threads-count b` is
> hardcoded — re-check it against the profile periodically or it will drift and
> quietly become a false claim. And do not scrape the profile to populate the
> rail: Threads renders client-side so permalinks are not even in the HTML, and
> scraping it is contrary to Meta's terms. Pasting the official embed code is
> the supported route.
>
> If you later obtain a Meta app token, the oEmbed endpoint
> (`graph.threads.net/v1.0/oembed?url=<permalink>`) can populate the slots
> server-side at deploy time — but the access token must stay on the server and
> never be committed to this repo.

The site has **no analytics and no Search Console verification** — nothing is being
measured. This document wires both up in one command.

## Step 1 — Get a GA4 measurement ID

1. Go to <https://analytics.google.com> → **Admin** → **Create property**
2. Name it `Wonder Sourcing`, set timezone **China (GMT+8)** and currency **USD**
3. Add a **Web** data stream with URL `https://www.wondersourcing.com`
4. Copy the **Measurement ID** — it looks like `G-AB12CD34EF`

## Step 2 — Get a Search Console verification token

1. Go to <https://search.google.com/search-console> → **Add property**
2. Choose **URL prefix** and enter `https://www.wondersourcing.com`
3. Expand **HTML tag**; copy only the `content="..."` value, e.g. `AbC123...xyz`

## Step 3 — Apply (run once from the repo root)

```bash
python3 tools/set_analytics.py --ga4 G-AB12CD34EF --gsc AbC123...xyz
```

Preview without writing anything:

```bash
python3 tools/set_analytics.py --ga4 G-AB12CD34EF --gsc AbC123...xyz --dry-run
```

Undo everything:

```bash
python3 tools/set_analytics.py --remove
```

The script is **idempotent** — run it as often as you like, it replaces its own
block instead of duplicating it. It wraps everything in
`<!-- ws:analytics:start -->` / `<!-- ws:analytics:end -->` markers so it can
always find and remove its own edits.

## Step 4 — Verify it works

1. Deploy, then open the site and check GA4 → **Reports → Realtime**
2. Click a WhatsApp link and submit the contact form; within ~30s you should see
   `contact_whatsapp` and `generate_lead` events appear
3. In Search Console, watch **Pages → Indexing** for the 404s that were removed

## Events tracked

| Event | Trigger | Why it matters |
| --- | --- | --- |
| `contact_whatsapp` | Any `wa.me` link click (floating button on every page) | Your primary inbound channel |
| `contact_email` | Any `mailto:` link click | Secondary contact route |
| `generate_lead` | Submit on `.manifest-form` (the sourcing brief) | The real conversion |

> **Note:** the brief form is a `mailto:` form — it opens the visitor's mail client
> rather than posting to a server, so closing the mail client loses the lead. If
> lead volume matters, move the form to a real endpoint (Formspree, Web3Forms, or a
> Vercel serverless function). That change is separate from analytics.

## Consent

GA4 sets cookies. Your audience is primarily Southeast Asia, but if you get
meaningful EU/UK traffic you need a consent banner before GA4 fires, or switch to a
cookieless tool (Plausible, Umami, or Vercel Web Analytics, which is a dashboard
toggle for Vercel-hosted sites).

## Alternative: Vercel Web Analytics

Since this site is already on Vercel, you can enable **Web Analytics** in the Vercel
project dashboard as a cookie-free option. GA4 is recommended if you also want
Search Console–style query data, funnels, or ad-platform integrations.
