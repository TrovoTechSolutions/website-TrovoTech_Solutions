"""Build product landing pages, the /products/ hub directory, and site menus.

Reads every products/<slug>/product.json.
- Draft products (status == 'draft') are ignored for hub, menus and sitemap.
- Live preview and live products are generated into products/<slug>/index.html.
- Fenced blocks in products/index.html are updated idempotently.
- Calls or updates site header & footer menus.

Usage:
    python tools/build-products.py
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
import importlib

def load_products():
    """Load all product.json files under products/ directory."""
    products_dir = ROOT / "products"
    products = []
    for product_json in sorted(products_dir.glob("*/product.json")):
        slug = product_json.parent.name
        if slug.startswith("_"):
            # Template or internal folder
            try:
                data = json.loads(product_json.read_text(encoding="utf-8"))
                # Always ensure template has draft status
                if data.get("status") == "draft":
                    continue
            except Exception:
                continue
        try:
            data = json.loads(product_json.read_text(encoding="utf-8"))
            if data.get("status") != "draft":
                products.append(data)
        except Exception as e:
            print(f"Error loading {product_json}: {e}", file=sys.stderr)
    return products


def get_site_header_and_footer(page_path):
    """Retrieve site header and footer from build-site-header module."""
    bsh = importlib.import_module("build-site-header")
    header_html = bsh.header_for(page_path)
    footer_products_html = bsh.FOOTER_PRODUCTS
    return header_html, footer_products_html


def render_product_page(product, site_header_html, site_footer_products_html):
    """Render full HTML for a product landing page."""
    slug = product["slug"]
    name = product["name"]
    short_name = product.get("shortName", name)
    platform_key = product.get("platformKey", slug)
    status = product.get("status", "draft")
    is_preview = (status == "live-preview")
    seo = product.get("seo", {})
    accents = product.get("accentColours", {})
    logos = product.get("logoFiles", {})
    hero_visual = product.get("heroVisual", {})
    closing = product.get("closing", {})
    primary_btn_text = closing.get("primaryButton", "Sign up")

    # CSS variables for root container
    css_vars = []
    if accents.get("primary"): css_vars.append(f"--product-primary:{accents['primary']}")
    if accents.get("secondary"): css_vars.append(f"--product-secondary:{accents['secondary']}")
    if accents.get("highlight"): css_vars.append(f"--product-highlight:{accents['highlight']}")
    if accents.get("night"): css_vars.append(f"--product-night:{accents['night']}")
    if accents.get("panel"): css_vars.append(f"--product-panel:{accents['panel']}")
    if accents.get("line"): css_vars.append(f"--product-line:{accents['line']}")
    if accents.get("text"): css_vars.append(f"--product-text:{accents['text']}")
    if accents.get("muted"): css_vars.append(f"--product-muted:{accents['muted']}")
    if accents.get("gradient"): css_vars.append(f"--product-gradient:{accents['gradient']}")
    style_attr = f' style="{"; ".join(css_vars)}"' if css_vars else ""

    # Robots & release meta
    robots_meta = '<meta name="robots" content="noindex,nofollow"><meta name="baylior-release" content="local-preview-only">' if is_preview else ''

    # JSON-LD
    json_ld = json.dumps(seo.get("jsonLd", {}), ensure_ascii=False)

    # Local preview bar
    preview_banner = '<aside class="b-preview"><div class="b-wrap"><strong>LOCAL PREVIEW</strong> Signup and pricing destinations are placeholders. This page is not released.</div></aside>' if is_preview else ''

    # Hero headline and subline
    hl = product.get("headline", {})
    hl_html = f"{hl.get('main', '')}<span>{hl.get('highlight', '')}</span>" if isinstance(hl, dict) else str(hl)
    sub = product.get("subline", {})
    sub_html = f"{sub.get('text', '')}<span>{sub.get('highlight', '')}</span>" if isinstance(sub, dict) else str(sub)

    # Hero visual screenshot
    hero_shot = hero_visual.get("screenshot", {})
    glow_logo = hero_visual.get("glowLogo", {})
    glow_html = f'<img class="b-glow-logo" src="{glow_logo["src"]}" alt="{glow_logo.get("alt","")}" width="{glow_logo.get("width", 280)}" height="{glow_logo.get("height", 280)}">' if glow_logo else ''
    v_label = hero_visual.get("visualLabel", "")
    v_label_html = f'<div class="b-visual-label"><span class="b-dot"></span> {v_label}</div>' if v_label else ''

    # Sub-header section links (only existing sections!)
    nav_links_html = []
    for item in product.get("sectionBar", []):
        sec_id = item["id"]
        # Only include if section exists in product data
        if sec_id == "features" and not product.get("features"): continue
        if sec_id == "platforms" and not product.get("platformsSection"): continue
        if sec_id == "how-it-works" and not product.get("howItWorks"): continue
        if sec_id == "pricing" and not product.get("pricingTeaser"): continue
        if sec_id == "faq" and not product.get("faq"): continue
        nav_links_html.append(f'<a href="#{sec_id}">{item["label"]}</a>')
    nav_links_str = "".join(nav_links_html)

    # Features Section
    features_html = ""
    feats = product.get("features")
    if feats:
        f_hl = feats.get("headline", {})
        f_hl_str = f"{f_hl.get('main', '')}<span>{f_hl.get('highlight', '')}</span>" if isinstance(f_hl, dict) else str(f_hl)
        f_items_html = []
        for item in feats.get("items", []):
            f_items_html.append(
                f'<article class="b-feature" id="{item["id"]}"><span class="b-number">{item["number"]}</span>'
                f'<h3>{item["title"]}</h3><p>{item["description"]}</p></article>'
            )
        f_grid_str = "".join(f_items_html)

        # Showcase
        showcase_html = ""
        sc = feats.get("showcase", {})
        if sc:
            split = sc.get("split", {})
            inv = sc.get("invoice", {})
            split_shot = split.get("screenshot", {})
            inv_shot = inv.get("screenshot", {})

            split_part = ""
            if split:
                split_part = (
                    f'<div class="b-wrap b-split"><div><p class="b-label">{split.get("label", "")}</p>'
                    f'<h2>{split.get("title", "")}</h2><p>{split.get("description", "")}</p>'
                    f'<p class="b-note">{split.get("note", "")}</p></div>'
                    f'<figure class="b-shot"><a href="{split_shot.get("src", "")}" target="_blank" rel="noopener" aria-label="Open full screenshot: {split_shot.get("alt", "")}">'
                    f'<img src="{split_shot.get("src", "")}" width="{split_shot.get("width", 1387)}" height="{split_shot.get("height", 810)}" alt="{split_shot.get("alt", "")}" loading=lazy></a>'
                    f'<figcaption>{split_shot.get("caption", "")}</figcaption></figure></div>'
                )

            inv_part = ""
            if inv:
                inv_part = (
                    f'<div class="b-wrap b-invoice"><figure class="b-shot"><a href="{inv_shot.get("src", "")}" target="_blank" rel="noopener" aria-label="Open full screenshot: {inv_shot.get("alt", "")}">'
                    f'<img src="{inv_shot.get("src", "")}" width="{inv_shot.get("width", 1387)}" height="{inv_shot.get("height", 810)}" alt="{inv_shot.get("alt", "")}" loading=lazy></a>'
                    f'<figcaption>{inv_shot.get("caption", "")}</figcaption></figure></div>'
                )
            showcase_html = f'<section class="b-section b-tint">{split_part}{inv_part}</section>'

        features_html = (
            f'<section class="b-section b-wrap" id="{feats.get("id", "features")}">'
            f'<div class="b-section-head"><p class="b-label">{feats.get("label", "")}</p>'
            f'<h2>{f_hl_str}</h2><p>{feats.get("lead", "")}</p></div>'
            f'<div class="b-feature-grid">{f_grid_str}</div></section>'
            f'{showcase_html}'
        )

    # Modules Section
    modules_html = ""
    mods = product.get("modules")
    if mods:
        m_hl = mods.get("headline", {})
        m_hl_str = f"{m_hl.get('main', '')}<span>{m_hl.get('highlight', '')}</span>" if isinstance(m_hl, dict) else str(m_hl)
        m_items_html = []
        for item in mods.get("items", []):
            m_items_html.append(
                f'<article class="b-module"><p class="b-label">{item["label"]}</p>'
                f'<h3>{item["title"]}</h3><p>{item["description"]}</p></article>'
            )
        m_grid_str = "".join(m_items_html)
        note_str = f'<p class="b-note">{mods["note"]}</p>' if mods.get("note") else ""
        modules_html = (
            f'<section class="b-section b-wrap" id="{mods.get("id", "modules")}">'
            f'<div class="b-section-head"><p class="b-label">{mods.get("label", "")}</p>'
            f'<h2>{m_hl_str}</h2></div><div class="b-modules">{m_grid_str}</div>{note_str}</section>'
        )

    # Platforms Section
    platforms_html = ""
    plat_sec = product.get("platformsSection")
    if plat_sec:
        p_shot = plat_sec.get("screenshot", {})
        badges_str = "".join(f"<span>{b}</span>" for b in plat_sec.get("badges", []))
        app_link = plat_sec.get("appLink", {})
        platforms_html = (
            f'<section class="b-section b-tint" id="{plat_sec.get("id", "platforms")}">'
            f'<div class="b-wrap b-split"><div><p class="b-label">{plat_sec.get("label", "")}</p>'
            f'<h2>{plat_sec.get("headline", "")}</h2><p>{plat_sec.get("description", "")}</p>'
            f'<div class="b-platforms">{badges_str}</div><div class="b-actions">'
            f'<a class="b-button b-outline" data-destination="pricing" data-product="{platform_key}" href="#preview-links">View pricing<span class="b-placeholder">Preview link</span></a>'
            f'<a class="b-text-link" href="{app_link.get("href", "#get-the-app")}">{app_link.get("text", "Get the app ↗")}</a></div></div>'
            f'<figure class="b-shot"><a href="{p_shot.get("src", "")}" target="_blank" rel="noopener" aria-label="Open full screenshot: {p_shot.get("alt", "")}">'
            f'<img src="{p_shot.get("src", "")}" width="{p_shot.get("width", 1387)}" height="{p_shot.get("height", 810)}" alt="{p_shot.get("alt", "")}" loading=lazy></a>'
            f'<figcaption>{p_shot.get("caption", "")}</figcaption></figure></div></section>'
        )

    # How it works Section
    how_html = ""
    how = product.get("howItWorks")
    if how:
        h_hl = how.get("headline", {})
        h_hl_str = f"{h_hl.get('main', '')}<span>{h_hl.get('highlight', '')}</span>" if isinstance(h_hl, dict) else str(h_hl)
        steps_html = []
        for s in how.get("steps", []):
            steps_html.append(f'<li><span>{s["step"]}</span><h3>{s["title"]}</h3><p>{s["description"]}</p></li>')
        steps_str = "".join(steps_html)
        how_html = (
            f'<section class="b-section b-wrap" id="{how.get("id", "how-it-works")}">'
            f'<div class="b-section-head"><p class="b-label">{how.get("label", "")}</p>'
            f'<h2>{h_hl_str}</h2></div><ol class="b-steps">{steps_str}</ol></section>'
        )

    # Pricing Teaser Section (NO prices)
    pricing_html = ""
    price_sec = product.get("pricingTeaser")
    if price_sec:
        pricing_html = (
            f'<section class="b-section b-wrap" id="{price_sec.get("id", "pricing")}">'
            f'<div class="b-pricing"><div><p class="b-label">{price_sec.get("label", "")}</p>'
            f'<h2>{price_sec.get("headline", "")}</h2><p>{price_sec.get("description", "")}</p></div>'
            f'<a class="b-button b-primary" data-destination="pricing" data-product="{platform_key}" href="#preview-links">{price_sec.get("buttonText", "View pricing")}<span class="b-placeholder">Preview link</span></a></div></section>'
        )

    # FAQ Section
    faq_html = ""
    faq = product.get("faq")
    if faq:
        f_hl = faq.get("headline", {})
        f_hl_str = f"{f_hl.get('main', '')}<span>{f_hl.get('highlight', '')}</span>" if isinstance(f_hl, dict) else str(f_hl)
        faq_items_html = []
        for q in faq.get("items", []):
            faq_items_html.append(f'<details><summary>{q["question"]}</summary><p>{q["answer"]}</p></details>')
        faq_items_str = "".join(faq_items_html)
        faq_html = (
            f'<section class="b-section b-wrap" id="{faq.get("id", "faq")}">'
            f'<div class="b-faq-layout"><div><p class="b-label">{faq.get("label", "")}</p>'
            f'<h2>{f_hl_str}</h2></div><div class="b-faq">{faq_items_str}</div></div></section>'
        )

    # Get the app Section
    app_html = ""
    get_app = product.get("getTheApp")
    if get_app:
        act = get_app.get("action", {})
        app_html = (
            f'<section class="b-section b-wrap" id="{get_app.get("id", "get-the-app")}">'
            f'<div class="b-download"><img src="{get_app.get("logo", "")}" width="72" height="72" alt="">'
            f'<div><p class="b-label">{get_app.get("label", "")}</p>'
            f'<h2>{get_app.get("headline", "")}</h2><p>{get_app.get("description", "")}</p></div>'
            f'<a class="b-button b-outline" href="{act.get("href", "#")}">{act.get("text", "Call Trovo ↗")}</a></div></section>'
        )

    # Closing Section
    closing_html = ""
    if closing:
        sec_btn = closing.get("secondaryButton", {})
        closing_html = (
            f'<section class="b-section b-wrap b-closing"><p class="b-label">{closing.get("label", "")}</p>'
            f'<h2>{closing.get("headline", "")}</h2><div class="b-actions">'
            f'<a class="b-button b-primary" data-destination="signup" data-product="{platform_key}" href="#preview-links">{primary_btn_text}<span class="b-placeholder">Preview link</span></a>'
            f'<a class="b-button b-outline" href="{sec_btn.get("href", "#")}">{sec_btn.get("text", "Talk to us ↗")}</a></div></section>'
        )

    # Preview links aside
    preview_aside_html = (
        '<aside id="preview-links" class="b-preview-links b-wrap" tabindex="-1">'
        '<h2>Preview links only</h2>'
        '<p>Signup and pricing are not connected yet. Their web address will be chosen and verified in Phase 5. These buttons stay here until then.</p>'
        '<p>For now, <a href="tel:+919042672148">talk to Trovo</a> or continue exploring this local preview.</p></aside>'
    ) if is_preview else ''

    # Compose full HTML
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{seo.get("title", "")}</title>
<meta name="description" content="{seo.get("description", "")}">
{robots_meta}
<link rel="canonical" href="{seo.get("canonical", "")}">
<meta property="og:type" content="{seo.get("ogType", "website")}"><meta property="og:title" content="{seo.get("ogTitle", "")}">
<meta property="og:description" content="{seo.get("ogDescription", "")}">
<meta property="og:url" content="{seo.get("canonical", "")}"><meta property="og:image" content="{seo.get("ogImage", "")}">
<meta property="og:image:width" content="{seo.get("ogImageWidth", 1200)}"><meta property="og:image:height" content="{seo.get("ogImageHeight", 630)}"><meta property="og:image:alt" content="{seo.get("ogImageAlt", "")}">
<meta name="twitter:card" content="{seo.get("twitterCard", "summary_large_image")}"><meta name="twitter:title" content="{seo.get("twitterTitle", "")}"><meta name="twitter:description" content="{seo.get("twitterDescription", "")}"><meta name="twitter:image" content="{seo.get("twitterImage", "")}">
<link rel="icon" type="image/svg+xml" href="{seo.get("icon", logos.get("icon", ""))}">
<link rel="stylesheet" href="/css/variables.css?v=8"><link rel="stylesheet" href="/css/style.css?v=8"><link rel="stylesheet" href="/css/responsive.css?v=8"><link rel="stylesheet" href="/css/product-page.css?v=1"><link rel="stylesheet" href="./baylior.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet"><link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined&amp;display=swap" rel="stylesheet">
<script type="application/ld+json">{json_ld}</script>
<script src="/js/product-page.js?v=1" defer></script><script src="./destinations.js" defer></script><script src="/js/main.js?v=9" defer></script><script src="/js/product-destinations.js?v=1" defer></script><script src="/js/baylior-destinations.js?v=1" defer></script>
  <link rel="stylesheet" href="/css/products.css?v=1">
  <script src="/js/site-navigation.js?v=1" defer></script>
</head><body>
<a href="#main" class="skip-link">Skip to content</a>{site_header_html}
<main id="main" class="product-page {slug}"{style_attr}>
{preview_banner}
<section class="b-hero b-wrap" id="overview"><div class="b-hero-copy"><img class="b-lockup" src="{logos.get("onDark", "")}" alt="{name} Business Suite" width="{logos.get("width", 268)}" height="{logos.get("height", 72)}"><p class="b-label">{product.get("heroLabel", "")}</p><h1>{hl_html}</h1><p class="b-tagline">{sub_html}</p><p class="b-lead">{product.get("description", "")}</p><div class="b-actions"><a class="b-button b-primary" data-destination="signup" data-product="{platform_key}" href="#preview-links">{primary_btn_text}<span class="b-placeholder">Preview link</span></a><a class="b-button b-outline" data-destination="pricing" data-product="{platform_key}" href="#preview-links">View pricing<span class="b-placeholder">Preview link</span></a><a class="b-text-link" href="tel:+919042672148">Talk to us ↗</a></div><p class="b-meta">{product.get("meta", "")}</p></div><div class="b-hero-visual">{glow_html}{v_label_html}<figure class="b-shot"><a href="{hero_shot.get("src", "")}" target="_blank" rel="noopener" aria-label="Open full screenshot: {hero_shot.get("alt", "")}"><img src="{hero_shot.get("src", "")}" width="{hero_shot.get("width", 1387)}" height="{hero_shot.get("height", 810)}" alt="{hero_shot.get("alt", "")}" fetchpriority=high></a><figcaption>{hero_shot.get("caption", "")}</figcaption></figure></div></section>
<nav class="b-product-nav" aria-label="{short_name} sections"><div class="b-wrap"><a class="b-nav-brand" href="#overview">{short_name}<span class="b-dot"></span></a><div class="b-nav-links">{nav_links_str}</div><a class="b-button b-primary" data-destination="signup" data-product="{platform_key}" href="#preview-links">{primary_btn_text}<span class="b-placeholder">Preview link</span></a></div></nav>
{features_html}
{modules_html}
{platforms_html}
{how_html}
{pricing_html}
{faq_html}
{app_html}
{closing_html}
{preview_aside_html}
</main><footer class="footer">
    <div class="container">
      <div class="footer__grid">
        <div>
          <a href="/index.html" class="brand-lockup">
          <img loading="lazy" src="/assets/logo-navbar.webp" alt="Trovo Tech Solutions" class="brand-lockup__icon" width="72" height="72" />
          <div class="brand-lockup__text">
            <span class="brand-lockup__title">Trovo Tech</span>
            <span class="brand-lockup__subtitle">Solutions</span>
            <span class="brand-lockup__tagline">Beyond Today</span>
          </div>
        </a>
          <p class="footer__about">A founder-led software studio building websites, custom software, web apps, Android apps and desktop software for growing businesses.</p>
          <div class="socials">
            <a href="https://www.linkedin.com/company/trovotechsolutions/?viewAsMember=true" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></a>
          </div>
        </div>
        <div>
          <h2>Solutions</h2>
          <ul class="footer__links">
            <li><a href="/services.html#custom-software">Custom Software</a></li>
            <li><a href="/services.html#web-design">Web Design</a></li>
            <li><a href="/services.html#web-apps">Web Apps</a></li>
            <li><a href="/services.html#android">Android Apps</a></li>
            <li><a href="/services.html#desktop">Desktop Software</a></li>
            <li><a href="/services.html#automation">Business Automation</a></li>
          </ul>
        </div>
        <div>
          <h2>Company</h2>
          <ul class="footer__links">
            <li><a href="/about.html">About</a></li>
            <li><a href="/projects.html">Portfolio</a></li>
            <li><a href="/contact.html">Contact</a></li>
          </ul>
        </div>
      {site_footer_products_html}
</div>
      <div class="footer__bottom">
        <p>&copy; <span data-year>2026</span> Trovo Tech Solutions. All rights reserved.</p>
        <nav class="footer__legal" aria-label="Legal">
          <a href="/privacy-policy/">Privacy Policy</a>
          <a href="/data-deletion/">Data Deletion</a>
          <a href="/terms/">Terms</a>
          <a href="/refund-policy/">Refund Policy</a>
        </nav>
      </div>
    </div>
  </footer></body></html>
"""
    return html


def update_hub_page(products):
    """Update products/index.html with industry filter buttons and product cards."""
    hub_file = ROOT / "products" / "index.html"
    html = hub_file.read_text(encoding="utf-8")

    # 1. Industry filter buttons
    industries = {}
    for p in products:
        ind_key = p.get("industryFilter", "all")
        ind_label = p.get("industry", "").split("·")[0].strip() or ind_key.capitalize()
        industries[ind_key] = industries.get(ind_key, 0) + 1

    filter_buttons = [
        f'          <button type="button" data-industry="all" aria-pressed="true">All<span class="products-filter__count">{len(products)}</span></button>'
    ]
    for ind_key, count in industries.items():
        if ind_key == "all": continue
        label = ind_key.capitalize()
        for p in products:
            if p.get("industryFilter") == ind_key:
                label = p.get("industry", "").split("·")[0].strip()
                break
        filter_buttons.append(
            f'          <button type="button" data-industry="{ind_key}" aria-pressed="false">{label}<span class="products-filter__count">{count}</span></button>'
        )

    filter_inner = (
        '          <span class="products-filter__label">Industry</span>\n' +
        "\n".join(filter_buttons)
    )

    # Check for fence comments or existing buttons
    filter_pattern = r'(<div class="products-filter"[^>]*>).*?(</div>\s*<div class="products-grid")'
    filter_replacement = rf'\1\n{filter_inner}\n        \2'
    html, count = re.subn(filter_pattern, filter_replacement, html, count=1, flags=re.S)
    if count != 1:
        raise ValueError("Could not update products-filter in products/index.html")

    # 2. Product cards
    cards_html = []
    for p in products:
        slug = p["slug"]
        platform_key = p.get("platformKey", slug)
        name = p["name"]
        industry_tag = p.get("industry", "")
        ind_filter = p.get("industryFilter", "all")
        logos = p.get("logoFiles", {})
        tagline = p.get("tagline", "")
        # parse tagline span if needed
        tag_parts = tagline.split(". ")
        if len(tag_parts) == 2:
            tagline_html = f"{tag_parts[0]}. <span>{tag_parts[1]}</span>"
        else:
            tagline_html = tagline

        desc = p.get("description", "")
        platforms = " · ".join(p.get("platforms", [])).upper()
        card_img = p.get("cardImage", p.get("heroVisual", {}).get("screenshot", {}))

        highlights = []
        for h in p.get("cardHighlights", []):
            highlights.append(f'                <li><span class="material-symbols-outlined" aria-hidden="true">{h["icon"]}</span>{h["text"]}</li>')
        highlights_str = "\n".join(highlights)

        card_action_label = p.get("cardSignupLabel", "Try now")
        card = f"""          <article class="product-card" data-industry="{ind_filter}" aria-labelledby="{slug}-card-title">
            <div>
              <span class="product-card__tag">{industry_tag}</span><br />
              <img class="product-card__logo" src="{logos.get("onDark", "")}" width="{logos.get("width", 220)}" height="{logos.get("height", 59)}" alt="{name} Business Suite" />
              <h2 id="{slug}-card-title">{tagline_html}</h2>
              <p>{desc}</p>
              <ul class="product-card__features">
{highlights_str}
              </ul>
              <p class="product-card__platforms">{platforms}</p>
              <div class="product-card__actions">
                <a class="bp-action" href="/products/{slug}/">Explore {name}</a>
                <a class="bp-action bp-action--outline" data-destination="signup" data-product="{platform_key}" data-baylior-destination="signup" href="/products/{slug}/#preview-links">{card_action_label}<small class="bp-placeholder">Preview link</small></a>
              </div>
            </div>
            <a class="product-card__shot" href="/products/{slug}/" aria-label="Explore {name}">
              <img src="{card_img.get("src", "")}" width="{card_img.get("width", 1387)}" height="{card_img.get("height", 810)}" loading="lazy" alt="{card_img.get("alt", "")}" />
            </a>
          </article>"""
        cards_html.append(card)

    cards_str = "\n\n".join(cards_html)
    # Documented extension point for optional Zoho-style featured panel:
    extension_point = "<!-- EXTENSION POINT: Optional Zoho-style featured product banner/panel (not built now; render here if product.get('featured')) -->\n"
    grid_pattern = r'(<div class="products-grid"[^>]*>\s*)(.*?)(<div class="products-next">)'
    grid_replacement = rf'\1{extension_point}          {cards_str}\n\n          \3'
    html, count = re.subn(grid_pattern, grid_replacement, html, count=1, flags=re.S)
    if count != 1:
        raise ValueError("Could not update products-grid in products/index.html")

    hub_file.write_text(html, encoding="utf-8")
    print("Updated products/index.html (hub)")


def update_site_headers_and_footers(products):
    """Update build-site-header FOOTER_PRODUCTS and run across all site pages."""
    bsh_file = TOOLS / "build-site-header.py"
    bsh_code = bsh_file.read_text(encoding="utf-8")

    # Generate footer products list
    links = ['<li><a href="/products/">All products</a></li>']
    for p in products:
        links.append(f'<li><a href="/products/{p["slug"]}/">{p["name"]} Business Suite</a></li>')
        if p.get("getTheApp"):
            sec_id = p["getTheApp"].get("id", "get-the-app")
            links.append(f'<li><a href="/products/{p["slug"]}/#{sec_id}">Get the app</a></li>')
    items = "\n            ".join(links)
    new_footer = f"""<div class="footer-products">
          <h2>Products</h2>
          <ul class="footer__links">
            {items}
          </ul>
        </div>"""

    bsh_code, count = re.subn(
        r'FOOTER_PRODUCTS = """.*?"""',
        f'FOOTER_PRODUCTS = """{new_footer}"""',
        bsh_code,
        count=1,
        flags=re.S
    )

    # Ensure product-destinations.js is in HEAD_INCLUDES
    if '<script src="/js/product-destinations.js?v=1" defer></script>' not in bsh_code:
        bsh_code = bsh_code.replace(
            "'<script src=\"/js/baylior-destinations.js?v=1\" defer></script>',",
            "'<script src=\"/js/baylior-destinations.js?v=1\" defer></script>',\n    '<script src=\"/js/product-destinations.js?v=1\" defer></script>',"
        )

    bsh_file.write_text(bsh_code, encoding="utf-8")
    print("Updated tools/build-site-header.py")

    # Run update across pages
    bsh = importlib.import_module("build-site-header")
    bsh.FOOTER_PRODUCTS = new_footer
    for page in bsh.pages():
        bsh.update(page)


def build_all():
    products = load_products()
    print(f"Loaded {len(products)} active product(s): {', '.join(p['slug'] for p in products)}")

    # 1. Update site header & footer tool and pages
    update_site_headers_and_footers(products)

    # 2. Render each non-draft product page
    for p in products:
        slug = p["slug"]
        page_dir = ROOT / "products" / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        page_file = page_dir / "index.html"

        header_html, footer_products_html = get_site_header_and_footer(page_file)
        html = render_product_page(p, header_html, footer_products_html)

        # Write product page
        page_file.write_text(html, encoding="utf-8")
        print(f"Rendered products/{slug}/index.html")

    # 3. Update the hub page
    update_hub_page(products)
    print("Build products completed successfully.")


if __name__ == "__main__":
    build_all()
