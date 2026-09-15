# Analytics & Search Console setup

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
