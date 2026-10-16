"""Write the shared site header and footer Products column into every page.

The site is static HTML with no build step, so the header is copied into each
page. Change the header here and re-run:

    python tools/build-site-header.py

Safe to run repeatedly: it replaces the existing <header> and Products column.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# Menu order agreed 14 Oct 2026. Products is a plain link to the products page.
NAV = [
    ("/index.html", "Home", "home"),
    ("/about.html", "About", "about"),
    ("/services.html", "Services", "services"),
    ("/products/", "Products", "products"),
    ("/projects.html", "Portfolio", "projects"),
    ("/contact.html", "Contact", "contact"),
]

BRAND = """<a href="/index.html" class="brand-lockup">
        <img src="/assets/logo-navbar.webp" alt="Trovo Tech Solutions" class="brand-lockup__icon" width="72" height="72" />
        <div class="brand-lockup__text">
          <span class="brand-lockup__title">Trovo Tech</span>
          <span class="brand-lockup__subtitle">Solutions</span>
          <span class="brand-lockup__tagline">Beyond Today</span>
        </div>
      </a>"""

FOOTER_PRODUCTS = """<div class="footer-products">
          <h2>Products</h2>
          <ul class="footer__links">
            <li><a href="/products/">All products</a></li>
            <li><a href="/products/baylior/">Baylior Business Suite</a></li>
            <li><a href="/products/baylior/#get-the-app">Get the app</a></li>
          </ul>
        </div>"""

HEAD_INCLUDES = [
    '<link rel="stylesheet" href="/css/products.css?v=1">',
    '<script src="/js/site-navigation.js?v=1" defer></script>',
    '<script src="/js/baylior-destinations.js?v=1" defer></script>',
    '<script src="/js/product-destinations.js?v=1" defer></script>',
]
RETIRED_INCLUDES = re.compile(
    r'[ \t]*<(?:link[^>]*baylior-discovery\.css|script[^>]*baylior-navigation\.js)[^>]*>(?:</script>)?\n?'
)


def pages():
    yield from sorted(ROOT.glob("*.html"))
    for folder in ("products", "products/baylior", "terms", "refund-policy", "privacy-policy", "data-deletion"):
        page = ROOT / folder / "index.html"
        if page.exists():
            yield page


def current_section(page):
    relative = page.relative_to(ROOT).as_posix()
    if relative.startswith("products/"):
        return "products"
    return {
        "index.html": "home",
        "about.html": "about",
        "services.html": "services",
        "projects.html": "projects",
        "contact.html": "contact",
    }.get(relative)


def header_for(page):
    current = current_section(page)
    links = "\n        ".join(
        f'<a href="{href}"{" aria-current=" + chr(34) + "page" + chr(34) if key == current else ""}>{label}</a>'
        for href, label, key in NAV
    )
    return f"""<header class="navbar site-header">
    <div class="container navbar__inner">
      {BRAND}
      <nav class="nav-links" id="site-navigation" aria-label="Primary">
        {links}
        <a class="nav-quote" href="/contact.html">Get a Quote</a>
      </nav>
      <a href="/contact.html" class="btn btn--primary">Get a Quote</a>
      <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="site-navigation">
        <span class="material-symbols-outlined" aria-hidden="true">menu</span>
      </button>
    </div>
  </header>"""


def update(page):
    html = page.read_text(encoding="utf-8-sig")
    original = html

    html, count = re.subn(r'<header class="navbar[^"]*">.*?</header>', lambda _: header_for(page), html, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"{page}: no site header found")

    html = RETIRED_INCLUDES.sub("", html)
    missing = [line for line in HEAD_INCLUDES if re.search(r'(?:href|src)="([^"?]+)', line)[1] not in html]
    if missing:
        html = html.replace("</head>", "".join(f"  {line}\n" for line in missing) + "</head>", 1)

    html, count = re.subn(
        r'<div class="(?:bp-footer-products|footer-products)">.*?</div>(?=\s*</div>\s*<div class="footer__bottom">)',
        lambda _: FOOTER_PRODUCTS,
        html,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise ValueError(f"{page}: no footer Products column found")

    if html != original:
        page.write_text(html, encoding="utf-8")
        print("updated", page.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    for page in pages():
        update(page)
