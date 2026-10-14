"""Prepare the local-only Phase 2 page in the existing company website."""
from pathlib import Path
import re, shutil, json
from PIL import Image, ImageDraw, ImageFont

root = Path('E:/TTS/Projects/Websites/TrovoTech_Solutions')
page = root / 'products/baylior'
page.mkdir(parents=True, exist_ok=True)
assets = root / 'assets/baylior'
for src in (Path('E:/TTS/Projects/Desktop_Apps/E6_Car_spa_new/docs/signup-phase1/screenshots')).glob('*.png'):
    shutil.copy2(src, assets / src.name)
home = (root / 'index.html').read_text(encoding='utf-8')
header = re.search(r'<header class="navbar">.*?</header>', home, re.S)[0]
footer = re.search(r'<footer class="footer">.*?</footer>', home, re.S)[0]
def rooted(fragment):
    return re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/)([^"]+)"', r'\1="/\2"', fragment).replace(' class="is-active"', '')
header, footer = rooted(header), rooted(footer)
for url, label in (("/terms/", "Terms"), ("/refund-policy/", "Refund Policy")):
    if f'href="{url}"' not in footer:
        footer = footer.replace('</nav>', f'<a href="{url}">{label}</a></nav>')
def action(label='Sign up', kind='signup', primary=True):
    return f'<a class="b-button {"b-primary" if primary else "b-outline"}" data-destination="{kind}" href="#preview-links">{label}<span class="b-placeholder">Preview link</span></a>'
def shot(name, alt, caption, eager=False):
    return f'<figure class="b-shot"><a href="/assets/baylior/{name}.png" target="_blank" rel="noopener" aria-label="Open full screenshot: {alt}"><img src="/assets/baylior/{name}.png" width="1387" height="810" alt="{alt}" {"fetchpriority=high" if eager else "loading=lazy"}></a><figcaption>{caption}</figcaption></figure>'
core = [
 ('01','Customers and vehicles','Keep customer and vehicle records together with the jobs you create for them.'),
 ('02','Job cards','Track work from draft and in progress through quality check, ready and delivered. Keep services and job status in the job card.'),
 ('03','Billing and invoices','Create GST and cash invoices with your business details, service lines and totals.'),
 ('04','Payments','Record payments and review collections and outstanding invoice balances.'),
 ('05','Staff and attendance','Maintain your staff directory and record attendance. Add the Staff advances &amp; salary module for advances and salary workflows.'),
 ('06','Reports and exports','Review sales, collections and outstanding balances, and export reports to Excel. Additional report access depends on your modules and permissions.')]
modules = [
 ('Outside jobs &amp; vendors','Send work to outside vendors and track its cost and your margin.'),
 ('Staff advances &amp; salary','Track advances and monthly salary, including advance recovery.'),
 ('WhatsApp automation','Send invoice and payment messages to customers on WhatsApp.'),
 ('Advanced reports','Explore GST, staff productivity, job turnaround and margins.'),
 ('Audit trail','Review recorded actions such as invoice cancellations, payments and attendance changes.'),
 ('Showroom / B2B module','Manage dealership showroom work with staff, daily vehicle logs and dealer billing.'),
 ('Franchise network','View approved totals shared by your franchise branches.')]
feature_ids = ['customers-vehicles', 'job-cards', 'billing-invoices', 'payments', 'staff', 'reports']
features = ''.join(f'<article class="b-feature" id="{anchor}"><span class="b-number">{n}</span><h3>{title}</h3><p>{desc}</p></article>' for (n,title,desc),anchor in zip(core,feature_ids))
modulehtml = ''.join(f'<article class="b-module"><p class="b-label">{"Professional, or add-on" if i<5 else "Add-on, any plan"}</p><h3>{title}</h3><p>{desc}</p></article>' for i,(title,desc) in enumerate(modules))
faqs = [
 ('How does licensing work?','Each user needs a licence for Windows, Android or both. See the pricing page for current options.'),
 ('Is a trial available?','Check the signup page for current trial availability, eligibility and duration.'),
 ('Can I add users later?','The Owner can manage the subscription inside the app; available changes and charges are shown there.'),
 ('How do I pay?','Follow the payment options shown during signup, or contact Trovo for assistance.'),
 ('Where do I sign in?','Install Baylior on Windows or Android, register with your codes and sign in inside the app.'),
 ('What about privacy?','Read the <a href="/privacy-policy/">Privacy Policy</a> for how information is handled.'),
 ('How can I get help?','Contact Trovo Tech Solutions on <a href="tel:+919042672148">+91 90426 72148</a> or <a href="mailto:info@trovotechsolutions.in">info@trovotechsolutions.in</a>.')]
schema={'@context':'https://schema.org','@type':'SoftwareApplication','name':'Baylior','applicationCategory':'BusinessApplication','operatingSystem':'Windows, Android','description':'Business software for car wash and detailing businesses: customers, job cards, invoices, payments and staff.','url':'https://trovotechsolutions.in/products/baylior/','publisher':{'@type':'Organization','name':'Trovo Tech Solutions'}}
html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Baylior — Business Suite for car spas | Trovo Tech Solutions</title>
<meta name="description" content="Manage your car spa with Baylior: customers, job cards, invoices, payments and staff on Windows and Android. A product of Trovo Tech Solutions.">
<meta name="robots" content="noindex,nofollow"><meta name="baylior-release" content="local-preview-only">
<link rel="canonical" href="https://trovotechsolutions.in/products/baylior/">
<meta property="og:type" content="website"><meta property="og:title" content="Baylior — One suite. Every detail.">
<meta property="og:description" content="Business software for car wash and detailing businesses. Windows and Android. By Trovo Tech Solutions.">
<meta property="og:url" content="https://trovotechsolutions.in/products/baylior/"><meta property="og:image" content="https://trovotechsolutions.in/assets/baylior/share-card.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Baylior Business Suite. One suite. Every detail. For car wash and detailing businesses, on Windows and Android.">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Baylior — One suite. Every detail."><meta name="twitter:description" content="Business software for car wash and detailing businesses."><meta name="twitter:image" content="https://trovotechsolutions.in/assets/baylior/share-card.png">
<link rel="icon" type="image/svg+xml" href="/assets/baylior/baylior-icon.svg">
<link rel="stylesheet" href="/css/variables.css?v=8"><link rel="stylesheet" href="/css/style.css?v=8"><link rel="stylesheet" href="/css/responsive.css?v=8"><link rel="stylesheet" href="./baylior.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet"><link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined&amp;display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(schema)}</script>
<script src="./destinations.js" defer></script><script src="/js/main.js?v=7" defer></script></head><body>
<a href="#main" class="skip-link">Skip to content</a>{header}
<main id="main" class="baylior">
<aside class="b-preview"><div class="b-wrap"><strong>LOCAL PREVIEW</strong> Signup and pricing destinations are placeholders. This page is not released.</div></aside>
<section class="b-hero b-wrap" id="overview"><div class="b-hero-copy"><img class="b-lockup" src="/assets/baylior/baylior-lockup-on-dark.svg" alt="Baylior Business Suite" width="268" height="72"><p class="b-label">Built for car wash &amp; detailing businesses</p><h1>Run your car spa<br>on <span>one suite.</span></h1><p class="b-tagline">One suite. <span>Every detail.</span></p><p class="b-lead">Manage customers, vehicles, job cards, invoices, payments and staff with Baylior for Windows and Android. Choose the modules your business needs.</p><div class="b-actions">{action()}{action('View pricing','pricing',False)}<a class="b-text-link" href="tel:+919042672148">Talk to us ↗</a></div><p class="b-meta">Windows · Android <span> / </span> A product of Trovo Tech Solutions</p></div><div class="b-hero-visual"><img class="b-glow-logo" src="/assets/baylior/baylior-logo-original.webp" alt="" width="280" height="280"><div class="b-visual-label"><span class="b-dot"></span> YOUR BUSINESS. TOGETHER.</div>{shot('dashboard','Baylior Detailing demo suite home with Billing, Staff, Reports and Settings','Real Windows app · Demo data',True)}</div></section>
<nav class="b-product-nav" aria-label="Baylior sections"><div class="b-wrap"><a class="b-nav-brand" href="#overview">Baylior<span class="b-dot"></span></a><div class="b-nav-links"><a href="#features">Features</a><a href="#platforms">Windows &amp; Android</a><a href="#how-it-works">How it works</a><a href="#pricing">Pricing</a><a href="#faq">FAQ</a></div>{action()}</div></nav>
<section class="b-section b-wrap" id="features"><div class="b-section-head"><p class="b-label">From vehicle in to delivery</p><h2>The everyday work.<br><span>All connected.</span></h2><p>Keep your daily jobs together, with optional modules for outside vendors, dealership work and franchise networks.</p></div><div class="b-feature-grid">{features}</div></section>
<section class="b-section b-tint"><div class="b-wrap b-split"><div><p class="b-label">Job cards → invoices</p><h2>Keep the details<br>with the job.</h2><p>Services, vehicle information and work status stay in the job card. Create GST and cash invoices with your business details, service lines and totals.</p><p class="b-note">Screenshots show the real app with approved demo data. Select an image to see it full size.</p></div>{shot('job-card','Baylior job card for Customer_1 showing services, vehicle and invoiced status','Job card · Services, vehicle and work status')}</div><div class="b-wrap b-invoice">{shot('invoice','Baylior tax invoice showing Full body wash, GST breakdown and total','Invoice · Service lines, tax breakdown and totals')}</div></section>
<section class="b-section b-wrap" id="modules"><div class="b-section-head"><p class="b-label">Room for the way you work</p><h2>Add the modules<br><span>your business needs.</span></h2></div><div class="b-modules">{modulehtml}</div><p class="b-note">Franchise network capacity can be extended with the “10 more franchise branches” add-on. Plan and module availability is confirmed on the pricing page.</p></section>
<section class="b-section b-tint" id="platforms"><div class="b-wrap b-split"><div><p class="b-label">Windows · Android</p><h2>At the desk.<br>On the move.</h2><p>Choose a Windows, Android or combined licence for each user. View current licence options and prices on the pricing page.</p><div class="b-platforms"><span>▣ Windows</span><span>▯ Android</span><span>↔ Both</span></div><div class="b-actions">{action('View pricing','pricing',False)}<a class="b-text-link" href="#get-the-app">Get the app ↗</a></div></div>{shot('subscription','Baylior Professional subscription with user licences and included modules','Subscription · Demo data, not current pricing')}</div></section>
<section class="b-section b-wrap" id="how-it-works"><div class="b-section-head"><p class="b-label">A clear start</p><h2>From signup<br><span>to your first job.</span></h2></div><ol class="b-steps"><li><span>01</span><h3>Your business</h3><p>Enter your business details.</p></li><li><span>02</span><h3>Your plan</h3><p>Choose an available plan or trial. Check current eligibility during signup.</p></li><li><span>03</span><h3>Your app</h3><p>Install the app and register with your company and registration codes.</p></li></ol></section>
<section class="b-section b-wrap" id="pricing"><div class="b-pricing"><div><p class="b-label">Plans for your business</p><h2>Choose your licences.<br>Make room to grow.</h2><p>Choose licences and modules on the live pricing page.</p></div>{action('View pricing','pricing')}</div></section>
<section class="b-section b-wrap" id="faq"><div class="b-faq-layout"><div><p class="b-label">A few useful answers</p><h2>Before you<br><span>get started.</span></h2></div><div class="b-faq">{''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)}</div></div></section>
<section class="b-section b-wrap" id="get-the-app"><div class="b-download"><img src="/assets/baylior/baylior-mark.svg" width="72" height="72" alt=""><div><p class="b-label">Get Baylior</p><h2>Your next job starts here.</h2><p>Contact Trovo for the Windows and Android installers.</p></div><a class="b-button b-outline" href="tel:+919042672148">Call Trovo ↗</a></div></section>
<section class="b-section b-wrap b-closing"><p class="b-label">One suite. Every detail.</p><h2>Ready to get started?</h2><div class="b-actions">{action()}<a class="b-button b-outline" href="tel:+919042672148">Talk to us ↗</a></div></section>
<aside id="preview-links" class="b-preview-links b-wrap" tabindex="-1"><h2>Preview links only</h2><p>Signup and pricing are not connected yet. Their web address will be chosen and verified in Phase 5. These buttons stay here until then.</p><p>For now, <a href="tel:+919042672148">talk to Trovo</a> or continue exploring this local preview.</p></aside>
</main>{footer}</body></html>'''
if 'bp-header' in header:
    html = html.replace('</head>', '<link rel="stylesheet" href="/css/baylior-discovery.css?v=1"><script src="/js/baylior-navigation.js?v=1" defer></script><script src="/js/baylior-destinations.js?v=1" defer></script></head>')
    html = html.replace('main.js?v=7', 'main.js?v=9')
(page/'index.html').write_text(html,encoding='utf-8')
# A composed, original share card from the approved logo. No invented app imagery.
im=Image.new('RGB',(1200,630),'#0A0F1C'); d=ImageDraw.Draw(im)
for x in range(1200):
    t=x/1199; d.line((x,0,x,7),fill=(int(45+(20-45)*t),int(107+(200-107)*t),int(255+(240-255)*t)))
d.rounded_rectangle((815,72,1140,558),radius=32,fill='#121A2B',outline='#25334D',width=2)
logo=Image.open(assets/'baylior-logo-original.webp').convert('RGBA'); logo.thumbnail((285,285)); im.paste(logo,(835+(285-logo.width)//2,152),logo)
def font(size,bold=False): return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)
d.text((65,65),'BAYLIOR  /  BUSINESS SUITE',font=font(24,True),fill='#14C8F0')
d.text((62,155),'One suite.',font=font(78,True),fill='white'); d.text((62,245),'Every detail.',font=font(78,True),fill='#14C8F0')
d.text((67,371),'For car wash and detailing businesses.',font=font(28),fill='#BDCADD')
d.text((67,431),'Windows  ·  Android',font=font(26,True),fill='white')
d.line((67,505,740,505),fill='#26344B',width=2); d.text((67,541),'A product of Trovo Tech Solutions',font=font(22),fill='#A6B6CD')
im.save(assets/'share-card.png')
sitemap=root/'sitemap.xml'; xml=sitemap.read_text(encoding='utf-8')
if '/products/baylior/' not in xml: sitemap.write_text(xml.replace('</urlset>','  <!-- Phase 2: local preview only; do not publish until Phase 5 integration is verified. -->\n  <url><loc>https://trovotechsolutions.in/products/baylior/</loc><lastmod>2026-10-14</lastmod><priority>0.8</priority></url>\n</urlset>'),encoding='utf-8')
print('Page, approved screenshots, 1200x630 share card and local sitemap entry prepared.')


