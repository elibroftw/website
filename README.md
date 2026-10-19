# Website

My personal website. The frontend is now a static [Astro](https://astro.build) + [Svelte](https://svelte.dev)
site with Tailwind/shadcn-svelte available for new work, deployed to GitHub Pages. The original Flask
implementation is intentionally preserved at the repository root for the code samples referenced on my YouTube
channel.

## Stack

- **Astro** for static page generation and routing
- **Svelte** for interactive pages (PDF tools, QR generator, album art search, pool schedule, map, etc.)
- **Tailwind CSS v4** + a shadcn-svelte-compatible `components.json`
- The original `static/css/base.css`, `light.css`, and `dark.css` remain the visual source of truth
- Server-side features live on [lenerva.com](../lenerva.com) under `/api`: PDF split/combine, QR codes,
  Spotify album art, RBHS announcements, and the WLU pool schedule

## What it contains

- My prominent software projects
- An aesthetic version of my resume
- Album art search
- Articles I have written
- Prettified WLU pool schedule
- Useful software I use
- Resources for learning
- Socials
- QR code generator, PDF splitter, and PDF combiner

## Local development

```sh
pnpm install
pnpm dev
```

Astro copies the Flask-era `static/` directory to `public/static/` before dev/build (it is git-ignored), so there
is still one source of truth for assets.

## Environment variables

Create a `.env` file:

```env
# Server API. Optional: local dev already defaults to production lenerva.com.
PUBLIC_TOOLS_API_BASE=https://lenerva.com

# Optional: Google Maps key for /skateboarding-toronto/
PUBLIC_GOOGLE_MAPS_API_KEY=

# Optional: use /<repo>/ when deploying as a GitHub Pages project site
# BASE_PATH=/website
# SITE_URL=https://elibroftw.github.io
```

## Build and preview

```sh
pnpm build
pnpm preview
```

## Deploying to GitHub Pages

`.github/workflows/deploy-pages.yml` builds the site and publishes `dist/` using GitHub Actions. Enable
**Settings → Pages → Source: GitHub Actions** in the repository.

The workflow uses these repository variables (all optional):

| Variable | Default | Purpose |
| --- | --- | --- |
| `BASE_PATH` | `/` | Set to `/<repo>/` for a project site without a custom domain |
| `SITE_URL` | `https://elijahlopez.ca` | Used for canonical URLs/sitemap |
| `PUBLIC_TOOLS_API_BASE` | `https://lenerva.com` | Server-side tools API |
| `PUBLIC_GOOGLE_MAPS_API_KEY` | empty | Enables the Toronto skate map |

`public/CNAME` contains `elijahlopez.ca`. Remove it if you deploy without that custom domain.

## Original Flask app (preserved)

The old full-stack implementation is still in `app.py`, `blueprints/`, `modules/`, `templates/`, and
`static/`. It can be run with:

```sh
pip install -r requirements.txt --upgrade
# create a .env file before running
flask --debug --env-file .env run
```

Nothing was deleted so links to old Python code samples remain valid.
