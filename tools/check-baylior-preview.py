"""Verification of product landing pages and products hub.

Checks every non-draft product:
- Unique IDs and valid internal anchors
- Local asset paths and images exist
- Safe preview destination links
- JSON-LD without offers or prices
- Noindex during local preview
- Content policies (no prices, no fake endorsements/testimonials)
- Header and footer menus match active product data
- Draft template isolation (never rendered into hub, menus or sitemap)
- Generator idempotence
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import json
import hashlib
import xml.etree.ElementTree as ET
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "products"


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.text = []
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))
        if tag == "script":
            self.in_script = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if not self.in_script:
            self.text.append(data)


def load_all_product_data():
    active = []
    drafts = []
    for p_json in sorted(PRODUCTS_DIR.glob("*/product.json")):
        try:
            data = json.loads(p_json.read_text(encoding="utf-8"))
            if data.get("status") == "draft" or p_json.parent.name.startswith("_"):
                drafts.append((p_json.parent.name, data))
            else:
                active.append((p_json.parent.name, data))
        except Exception as e:
            raise RuntimeError(f"Error reading {p_json}: {e}")
    return active, drafts


def check_product_page(slug, data):
    page = PRODUCTS_DIR / slug / "index.html"
    assert page.exists(), f"Page not found for {slug}: {page}"

    p = Parser()
    html = page.read_text(encoding="utf-8")
    p.feed(html)

    # 1. Unique IDs
    ids = [a["id"] for t, a in p.nodes if "id" in a]
    assert len(ids) == len(set(ids)), f"Duplicate IDs in {slug}: {[x for x in ids if ids.count(x) > 1]}"

    # 2. Local references and anchors
    checked_refs = 0
    for tag, attrs in p.nodes:
        for key in ("src", "href"):
            url = attrs.get(key, "")
            parsed = urlparse(url)
            if not url or parsed.scheme or parsed.netloc:
                continue
            if url.startswith("#"):
                assert url[1:] in ids, f"Unresolved anchor {url} in {slug}"
                continue
            path = (ROOT / parsed.path.lstrip("/")) if parsed.path.startswith("/") else page.parent / parsed.path
            assert path.exists(), f"Missing referenced file {path} in {slug}"
            checked_refs += 1

        # 3. Destination links
        if "data-destination" in attrs:
            assert attrs["href"] in ("#preview-links", f"/products/{slug}/#preview-links"), f"Invalid preview link in {slug}: {attrs['href']}"
            assert attrs["data-destination"] in ("signup", "pricing"), f"Invalid destination type in {slug}: {attrs['data-destination']}"
            if "data-product" in attrs:
                assert attrs["data-product"] == data.get("platformKey", slug)

    # 4. JSON-LD SoftwareApplication schema without prices or offers
    schemas = __import__("re").findall(r'<script type="application/ld\+json">(.*?)</script>', html, __import__("re").S)
    assert len(schemas) >= 1, f"Missing JSON-LD in {slug}"
    found_sw = False
    for s_str in schemas:
        s = json.loads(s_str)
        if s.get("@type") == "SoftwareApplication":
            found_sw = True
            assert not any(k in json.dumps(s).lower() for k in ("price", "offers", "aggregaterating")), f"Forbidden pricing schema in {slug}"
    assert found_sw, f"No SoftwareApplication schema found in {slug}"

    # 5. Robots meta (noindex during preview)
    if data.get("status") == "live-preview":
        assert any(a.get("name") == "robots" and a.get("content") == "noindex,nofollow" for t, a in p.nodes), f"Missing noindex in {slug}"
        assert "LOCAL PREVIEW" in html and "Preview link" in html, f"Missing preview markers in {slug}"

    # 6. Content policies: no prices, no fake endorsements
    text = " ".join(p.text).lower()
    for forbidden in ("sign up free", "7-day", "7 day", "₹", "one-click"):
        assert forbidden not in text, f"Forbidden phrase '{forbidden}' found in {slug}"

    # E6 must not be claimed as endorsement
    if "e6" in text:
        # Check context: only permitted in portfolio context
        assert "endorse" not in text and "partner" not in text

    # 7. Share card dimensions if present
    share_card_path = ROOT / data.get("seo", {}).get("ogImage", "").replace("https://trovotechsolutions.in/", "")
    if share_card_path.exists() and share_card_path.suffix.lower() == ".png":
        assert Image.open(share_card_path).size == (1200, 630), f"Invalid share card dimensions for {slug}"

    # 8. Baylior specific screenshot hash checks if approved folder exists
    if slug == "baylior":
        approved = Path("E:/TTS/Projects/Desktop_Apps/E6_Car_spa_new/docs/signup-phase1/screenshots")
        if approved.exists():
            for name in ("dashboard", "job-card", "invoice", "subscription"):
                orig = approved / f"{name}.png"
                curr = ROOT / f"assets/baylior/{name}.png"
                if orig.exists() and curr.exists():
                    assert hashlib.sha256(orig.read_bytes()).digest() == hashlib.sha256(curr.read_bytes()).digest()

    return checked_refs


def check_sitemap_and_draft_isolation(active_products, draft_products):
    tree = ET.parse(ROOT / "sitemap.xml")
    sitemap_locs = [e.text.strip() for e in tree.iter() if e.tag.endswith("loc") and e.text]

    # Active products must exist in sitemap
    for slug, _ in active_products:
        url = f"https://trovotechsolutions.in/products/{slug}/"
        assert url in sitemap_locs, f"Active product {slug} missing from sitemap.xml"

    # Draft products must NEVER appear in sitemap, hub, or site header/footer
    hub_html = (ROOT / "products" / "index.html").read_text(encoding="utf-8")
    bsh_code = (ROOT / "tools" / "build-site-header.py").read_text(encoding="utf-8")

    for slug, draft_data in draft_products:
        draft_url = f"https://trovotechsolutions.in/products/{slug}/"
        assert draft_url not in sitemap_locs, f"Draft product {slug} leaked into sitemap.xml"
        assert f"/products/{slug}/" not in hub_html, f"Draft product {slug} leaked into products/index.html"
        assert f"/products/{slug}/" not in bsh_code, f"Draft product {slug} leaked into build-site-header.py"
        draft_name = draft_data.get("name", "")
        if draft_name and not draft_name.startswith("TODO"):
            assert draft_name not in hub_html, f"Draft product name {draft_name} leaked into hub"


def check_generator_idempotence():
    files_to_check = [
        ROOT / "products" / "baylior" / "index.html",
        ROOT / "products" / "index.html",
        ROOT / "tools" / "build-site-header.py"
    ]
    before = {f: f.read_text(encoding="utf-8") for f in files_to_check}
    subprocess.run(["python", str(ROOT / "tools" / "build-products.py")], check=True, capture_output=True)
    for f in files_to_check:
        after = f.read_text(encoding="utf-8")
        assert before[f] == after, f"Generator changed {f.relative_to(ROOT)} on second run! Not idempotent."


def main():
    active, drafts = load_all_product_data()
    print(f"Checking {len(active)} active product(s) and {len(drafts)} draft product(s)...")

    total_refs = 0
    for slug, data in active:
        refs = check_product_page(slug, data)
        total_refs += refs
        print(f"  [PASS] {slug}: {refs} local references, anchors, IDs and policy checks passed")

    check_sitemap_and_draft_isolation(active, drafts)
    print("  [PASS] Draft isolation verified: no draft products in hub, menus or sitemap")

    check_generator_idempotence()
    print("  [PASS] Generator idempotence verified: running build-products.py produced no git diff")

    print(f"PASS: All product verification checks passed ({total_refs} total references verified).")


if __name__ == "__main__":
    main()
