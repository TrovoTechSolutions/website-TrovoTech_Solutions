# Trovotech Solutions — Website

Clean, production-ready static frontend for Trovotech Solutions (IT services:
web, web apps, Android, desktop software).

## Structure
```
trovotech-website/
├── index.html          # Home
├── about.html          # About (mission, founder, tech stack)
├── services.html       # 4 services with features + use cases
├── projects.html       # Portfolio — projects + clients combined
├── css/
│   ├── variables.css   # Design tokens (colors, type, spacing, shadows)
│   ├── style.css       # Base + layout + components + page sections
│   └── responsive.css  # Mobile-first breakpoints (640 / 768 / 1024)
├── js/
│   └── main.js         # Nav toggle, scroll shadow, reveal, project filter
└── assets/             # (reserved for local images/logos)
```

## Design system
| Token | Value |
|-------|-------|
| Primary | `#0B1F3A` |
| Secondary | `#2563EB` |
| Accent | `#06B6D4` |
| Background | `#F8FAFC` / `#FFFFFF` |
| Text | `#111827` |
| Font | Inter (Google Fonts) |

All colors, spacing, radius and shadows are CSS custom properties in
`variables.css` — change them once, everywhere updates.

## Reusable components
`.btn` (`--primary/--solid/--outline/--ghost/--white/--lg`), `.card`
(`--hover/--feature`), `.section`, `.container`, `.badge`, `.project-card`
(`__banner` icon variant), `.client` logo card, `.navbar`, `.footer`.

## Adding client logos
Drop logo images into `assets/` and update the `<img src>` in `projects.html`
(Clients section). Suggested filenames: `assets/e6-logo.png`,
`assets/nsakthivelanco-logo.png`. If a logo file is missing, the card
automatically falls back to an icon + the client name, so nothing breaks.

## Run locally
Any static server works, e.g.:
```
python -m http.server 5501 --directory trovotech-website
```
Then open http://localhost:5501

No build step, no framework, no inline CSS.
```
