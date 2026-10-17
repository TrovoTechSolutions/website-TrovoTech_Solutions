# SaaS Product Pages Architecture & Developer Guide

This document describes the data-driven product page system for the TrovoTech Solutions company website.

The system replaces manually coded product landing pages and hardcoded hub cards with a single configuration-driven architecture modeled after modern enterprise SaaS landing pages (Zoho-style). Adding a new product requires creating its configuration file and local image assets—no copying or handcrafting HTML.

---

## 1. Quick Start: Adding a New Product

Follow these steps to add a new SaaS product (e.g., Civil, ERP, CRM):

1. **Copy the Template**
   Duplicate `products/_template/` into `products/<slug>/`:
   ```bash
   cp -r products/_template products/<slug>
   ```

2. **Configure `product.json`**
   Open `products/<slug>/product.json`.
   - Update `slug`, `platformKey`, `name`, `industry`, `tagline`, and content sections.
   - Set accent colours under `accent` (primary, dark, subtle background, surface, border).
   - Keep `"status": "draft"` while drafting. When ready for local preview or release, update `"status": "live-preview"`.

3. **Add Assets**
   Place your product images and logos in `assets/<slug>/`:
   - Logos: dark-mode logo SVG/PNG, light-mode logo SVG/PNG, mark/icon SVG/PNG.
   - Hero preview image and card image.
   - Feature screenshots and module diagrams (recommended 1200×675 or 1200×630).
   - Social share card (OG image, exactly 1200×630 PNG).

4. **Run the Generator**
   Execute the generator script:
   ```bash
   python tools/build-products.py
   ```
   This generates:
   - `products/<slug>/index.html` (the landing page).
   - Fenced product cards in `products/index.html`.
   - Filter count buttons for industries in `products/index.html`.
   - Header dropdown and footer product lists across all site pages via `tools/build-site-header.py`.

5. **Run Verification Suites**
   Run the test and verification tools to ensure integrity:
   ```bash
   python tools/check-baylior-preview.py
   node tools/check-baylior-links.cjs
   node tools/review-browser.js
   ```

---

## 2. Product Schema & Field Reference (`product.json`)

All fields are defined in `products/<slug>/product.json`. Every content section is optional and is safely omitted from the generated page and sub-header navigation if absent or empty.

| Field | Type | Description |
|---|---|---|
| `slug` | string | URL slug matching the folder name (e.g. `"baylior"`). |
| `platformKey` | string | Trovo Platform identifier used by the signup application (e.g. `"carspa"`, `"civil"`, `"erp"`). |
| `name` | string | Official product name (e.g. `"Baylior"`). |
| `shortName` | string | Abbreviated or colloquial name (e.g. `"Baylior"`). |
| `industry` | string | Industry classification matching hub filters (e.g. `"Automotive"`, `"Construction"`, `"Enterprise"`). |
| `tagline` | string | One-line market positioning statement used in cards and meta headers. |
| `heroLabel` | string | Small pill/kicker label displayed above the hero headline. |
| `headline` | object | `{ "text": "Full headline...", "em": "Emphasized Phrase" }`. The `em` substring is wrapped in an `<em>` accent tag. |
| `subline` | string | Introductory subline displayed beneath the headline. |
| `description` | string | Detailed multi-sentence product overview. |
| `platforms` | string[] | Array of supported platforms displayed as tags (e.g. `["Windows desktop", "Android app", "Web browser"]`). |
| `heroImage` | object | `{ "src": "/assets/.../hero.png", "alt": "..." }`. Primary interface preview. |
| `cardImage` | object | `{ "src": "/assets/.../card.png", "alt": "..." }`. Image displayed on the `/products/` hub card. |
| `accent` | object | `{ "primary": "#...", "dark": "#...", "subtle": "#...", "surface": "#...", "border": "#..." }`. Generates scoped CSS variables for the product. |
| `logos` | object | `{ "onDark": "...", "onLight": "...", "mark": "..." }`. Scalable vector or raster logo variations. |
| `sectionBar` | object[] | Array of `{ "id": "features", "label": "Features" }`. Drives the sticky product sub-header navigation. |
| `features` | object[] | Array of `{ "id": "...", "title": "...", "text": "...", "image": { "src": "...", "alt": "..." }, "highlights": [...] }`. Alternating image/text layout. |
| `modules` | object[] | Array of `{ "title": "...", "description": "...", "points": [...] }`. Rendered as module cards or grid. |
| `platformsSection` | object | Details about platform licensing, native apps, and offline support. |
| `howItWorks` | object[] | Array of `{ "step": 1, "title": "...", "text": "..." }`. Onboarding / workflow steps. |
| `pricingTeaser` | object | `{ "title": "...", "description": "...", "cta": "..." }`. **Text only — strictly NO currency figures or prices.** |
| `faq` | object[] | Array of `{ "question": "...", "answer": "..." }`. Rendered as native, accessible `<details>/<summary>` elements. |
| `getTheApp` | object | Direct links / instructions for native installers (Windows EXE/MSI, Android APK). |
| `closing` | object | Closing banner with primary trial CTA and secondary contact options. |
| `seo` | object | `{ "title": "...", "description": "...", "canonical": "...", "ogImage": "..." }`. Meta tags and Open Graph. |
| `status` | string | `"draft"` or `"live-preview"`. Drafts are strictly excluded from hub cards, menus, sitemap, and search. |

---

## 3. Destination Mapping & Security (`js/product-destinations.js`)

All product signup and pricing buttons use data attributes rather than hardcoded URLs:
```html
<a href="#preview-links"
   class="btn btn-primary"
   data-destination="signup"
   data-product="carspa">
  Start free trial <span class="btn-subtext">Preview link</span>
</a>
```

### Destination Resolution Rules
1. **Unverified / Default State (`integrationVerified: false`):**
   - All buttons keep `href="#preview-links"`.
   - The visible `<span class="btn-subtext">Preview link</span>` remains present to honestly indicate a local preview.
2. **Verified Integration State (`integrationVerified: true`):**
   - Must have a valid HTTPS origin (or `http://localhost:...` / `http://127.0.0.1:...` during local platform development).
   - `data-destination="signup"` resolves to:
     ```
     {signupOrigin}/signup/{platformKey}
     ```
   - `data-destination="pricing"` resolves to:
     ```
     {signupOrigin}/pricing/{platformKey}
     ```
   - The script removes the `"Preview link"` subtext once live destinations are engaged.

### Safety Invariants
- Origin validation strictly forbids credentials (`user:pass`), query parameters (`?key=...`), and hash fragments (`#...`).
- Cross-origin URLs must use `https://`.
- No user personal data is ever passed via URL parameters.

---

## 4. Architectural Policies & Content Constraints

1. **No Fixed Marketing Prices or Rates:**
   - Trovo product pages do not advertise fixed pricing, currency figures (₹, $, etc.), or discount promises in teasers.
   - Pricing teasers explain the subscription tiers, licensing model, or included modules in words only.
2. **No Fake Claims or Unverified Testimonials:**
   - No customer counts, fabricated user testimonials, or unverified rating badges.
   - E6 remains a Portfolio development project; it must not be cited as a commercial customer testimonial for Baylior.
3. **Template & Draft Isolation:**
   - Any product marked with `"status": "draft"` (such as `products/_template/`) is skipped by `tools/build-products.py`.
   - Draft products are never rendered into `/products/` hub cards, site navigation, footer columns, or sitemap.
4. **Idempotent Generators:**
   - Running `python tools/build-products.py` twice consecutively produces zero `git diff`.
   - Page sections in hand-edited files (`products/index.html`, site header/footer) are fenced with standard comment blocks:
     `<!-- BEGIN PRODUCT_CARDS --> ... <!-- END PRODUCT_CARDS -->`
     `<!-- BEGIN INDUSTRY_FILTERS --> ... <!-- END INDUSTRY_FILTERS -->`

---

## 5. Hub Layout & Extension Points

The `/products/` hub is implemented in `products/index.html`:
- **Header:** Title, subtitle, and responsive industry filter buttons with real-time active counts.
- **Product Cards:** Generated from active `product.json` data. Features logo, product title, industry tag, tagline, key feature pills, platforms supported, primary "Try now" action, and "Explore [Product]" link.
- **Zoho-Style Featured Banner Extension Point:**
  The hub includes an optional fenced slot `<!-- BEGIN FEATURED_PRODUCT -->` positioned directly above the card grid. When enabled in future iterations, a highlighted product can feature a full-bleed horizontal banner with interactive demo tabs without altering card grid styling.
- **Custom Software CTA:** Sits beneath the card grid inviting clients requiring bespoke solutions to contact Trovo engineers.

---

## 6. Verification and Test Suite

All tests must pass before committing or previewing:

1. **Link & Anchor Validation (`tools/check-baylior-links.cjs`):**
   - Verifies all internal links, anchors, local assets, and script references.
   - Validates active product pages and hub links.
   - Checks JSON-LD schema validity (SoftwareApplication without offers/prices).

2. **Preview & Policy Invariants (`tools/check-baylior-preview.py`):**
   - Validates all active `product.json` files against the required schema.
   - Ensures no price text (`₹`, `$`, `/month`, `per year`) exists in teasers or schema.
   - Verifies generator idempotence (git diff check across 2 runs).
   - Validates draft isolation (ensures template product does not leak into hub or menus).
   - Checks destination resolver states (verified vs preview).

3. **Browser & Responsive Review (`tools/review-browser.js`):**
   - Runs headless Chrome across 375px, 768px, and 1366px viewports.
   - Verifies zero horizontal overflow (`scrollWidth <= clientWidth`).
   - Verifies keyboard navigability of the sticky sub-header and details/summary FAQ.
   - Confirms 0 console errors.
