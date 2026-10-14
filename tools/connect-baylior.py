"""Apply Phase 3 shared navigation without replacing existing page bodies."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
pages=[*root.glob('*.html'),*(root/p/'index.html' for p in ('terms','refund-policy','privacy-policy','data-deletion','products/baylior'))]
def action(label,kind='signup'):
    return f'<a class="bp-action" data-baylior-destination="{kind}" href="/products/baylior/#preview-links">{label}<small class="bp-placeholder">Preview link</small></a>'
quick=[('Billing and invoices','receipt_long','billing-invoices'),('Job cards','assignment','job-cards'),('Customers and vehicles','directions_car','customers-vehicles'),('Staff','groups','staff'),('Reports','monitoring','reports'),('Franchise and showroom','hub','modules')]
panel=f'''<div class="bp-products"><button class="bp-products-toggle" type="button" aria-expanded="false" aria-controls="baylior-products-panel">Products <span aria-hidden="true">⌄</span></button>
<div class="bp-panel" id="baylior-products-panel" hidden>
<div class="bp-panel-main"><a href="/products/baylior/" class="bp-logo-link"><img src="/assets/baylior/baylior-lockup-on-dark.svg" width="220" height="59" alt="Baylior Business Suite"></a><p class="bp-tagline">One suite. <span>Every detail.</span></p><p class="bp-description">Business software for car wash and detailing businesses, on Windows and Android.</p><div class="bp-panel-actions">{action('Sign up')}{action('View pricing','pricing')}</div><a href="/products/baylior/" class="bp-explore">Explore Baylior <span aria-hidden="true">↗</span></a></div>
<div class="bp-quick"><p class="bp-eyebrow">Explore the suite</p>{''.join(f'<a href="/products/baylior/#{anchor}"><span class="material-symbols-outlined" aria-hidden="true">{icon}</span>{label}<span class="bp-quick-arrow" aria-hidden="true">↗</span></a>' for label,icon,anchor in quick)}</div><p class="bp-panel-footer">Built by Trovo Tech Solutions · More products coming</p>
</div></div>'''
band=f'''<section class="bp-home-band" aria-labelledby="baylior-home-heading"><div class="container bp-home-inner"><div><p class="bp-eyebrow">Meet our business suite</p><img src="/assets/baylior/baylior-lockup-on-dark.svg" width="220" height="59" alt="Baylior Business Suite"><h2 id="baylior-home-heading">One suite. <span>Every detail.</span></h2><p>Manage your car spa’s customers, job cards, invoices, payments and staff on Windows and Android.</p><div class="bp-band-actions"><a class="bp-explore" href="/products/baylior/">Explore Baylior ↗</a>{action('Sign up')}</div></div><a class="bp-home-screen" href="/products/baylior/" aria-label="Explore Baylior"><img src="/assets/baylior/dashboard.png" width="1387" height="810" loading="lazy" alt="Baylior Windows app suite home with demo business data"></a></div></section>'''
for path in pages:
    if not path.exists():continue
    html=path.read_text(encoding='utf-8-sig')
    if 'bp-products-toggle' in html:continue
    match=re.search(r'<header class="navbar">.*?</header>',html,re.S)
    if not match:raise ValueError(path)
    old=match[0]
    brand=re.search(r'<a[^>]*class="brand-lockup".*?</a>',old,re.S)[0]
    brand=re.sub(r'(href|src)="(?!https?:|/)([^"]+)"',r'\1="/\2"',brand)
    current=path.name if path.parent==root else ''
    links=''.join(f'<a href="/{url}"{(" aria-current="+chr(34)+"page"+chr(34)) if current==url else ""}>{label}</a>' for url,label in [('services.html','Services'),('projects.html','Portfolio'),('about.html','About'),('contact.html','Contact')])
    header=f'''<header class="navbar bp-header"><div class="container navbar__inner">{brand}<nav class="nav-links" id="site-navigation" aria-label="Primary">{panel}{links}<div class="bp-mobile-actions"><a href="/products/baylior/#get-the-app">Get the app</a>{action('Sign up')}</div></nav><div class="bp-header-actions"><a class="bp-get-app" href="/products/baylior/#get-the-app">Get the app</a>{action('Sign up')}</div><button class="nav-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="site-navigation"><span class="material-symbols-outlined" aria-hidden="true">menu</span></button></div></header>'''
    html=html[:match.start()]+header+html[match.end():]
    html=html.replace('</head>','<link rel="stylesheet" href="/css/baylior-discovery.css?v=1">\n<script src="/js/baylior-navigation.js?v=1" defer></script>\n<script src="/js/baylior-destinations.js?v=1" defer></script>\n</head>')
    footer_start=html.index('<footer class="footer">')
    footer=html[footer_start:]
    # Add a fourth footer column, without touching company/portfolio descriptions.
    end=footer.index('<div class="footer__bottom">')
    prefix=footer[:end]
    closing=prefix.rfind('</div>')
    prefix=prefix[:closing]+'''<div class="bp-footer-products"><h2>Products</h2><ul class="footer__links"><li><a href="/products/baylior/">Baylior Business Suite</a></li><li><a href="/products/baylior/#get-the-app">Get the app</a></li><li><a href="/products/baylior/#preview-links" data-baylior-destination="pricing">View pricing <small class="bp-placeholder">Preview link</small></a></li></ul></div>\n'''+prefix[closing:]
    html=html[:footer_start]+prefix+footer[end:]
    if path==root/'index.html':
        hero_end=html.index('</section>',html.index('<section class="hero">'))+len('</section>')
        html=html[:hero_end]+'\n'+band+html[hero_end:]
    # Version the existing script so old cached toggle handlers do not conflict.
    html=html.replace('main.js?v=7','main.js?v=9')
    path.write_text(html,encoding='utf-8')
    print(path.relative_to(root))
main=root/'js/main.js'; js=main.read_text(encoding='utf-8-sig')
if '  /* ---- Mobile nav toggle ---- */' in js:
    start=js.index('  /* ---- Mobile nav toggle ---- */'); end=js.index('  /* ---- Navbar shadow',start)
    js=js[:start]+'  // Shared navigation is handled by baylior-navigation.js.\n\n'+js[end:]
main.write_text(js,encoding='utf-8')
