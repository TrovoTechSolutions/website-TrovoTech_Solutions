"""Source/asset checks only; does not replace rendered browser review."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json, hashlib
import xml.etree.ElementTree as ET
from PIL import Image
root=Path(__file__).resolve().parents[1]
page=root/'products/baylior/index.html'
class Parser(HTMLParser):
    def __init__(self): super().__init__(); self.nodes=[]; self.text=[]; self.in_script=False
    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag,dict(attrs)))
        if tag=='script': self.in_script=True
    def handle_endtag(self,tag):
        if tag=='script': self.in_script=False
    def handle_data(self,data):
        if not self.in_script:self.text.append(data)
p=Parser(); html=page.read_text(encoding='utf-8'); p.feed(html)
ids=[a['id'] for t,a in p.nodes if 'id' in a]; assert len(ids)==len(set(ids))
checked=0
for tag,attrs in p.nodes:
    for key in ('src','href'):
        url=attrs.get(key,''); parsed=urlparse(url)
        if not url or parsed.scheme or parsed.netloc: continue
        if url.startswith('#'): assert url[1:] in ids,url; continue
        path=(root/parsed.path.lstrip('/')) if parsed.path.startswith('/') else page.parent/parsed.path
        assert path.exists(),str(path); checked+=1
    if 'data-destination' in attrs:
        assert attrs['href']=='#preview-links'
        assert attrs['data-destination'] in ('signup','pricing')
schemas=__import__('re').findall(r'<script type="application/ld\+json">(.*?)</script>',html,__import__('re').S)
assert len(schemas)==1
schema=json.loads(schemas[0]); assert schema['@type']=='SoftwareApplication'
assert not any(k in json.dumps(schema).lower() for k in ('price','offers','aggregaterating'))
assert any(a.get('name')=='robots' and a.get('content')=='noindex,nofollow' for t,a in p.nodes)
assert 'LOCAL PREVIEW' in html and 'Preview link' in html
text=' '.join(p.text).lower()
for forbidden in ('sign up free','7-day','7 day','₹','one-click','e6'):
    assert forbidden not in text,forbidden
assert Image.open(root/'assets/baylior/share-card.png').size==(1200,630)
approved=Path('E:/TTS/Projects/Desktop_Apps/E6_Car_spa_new/docs/signup-phase1/screenshots')
for name in ('dashboard','job-card','invoice','subscription'):
    assert hashlib.sha256((approved/f'{name}.png').read_bytes()).digest()==hashlib.sha256((root/f'assets/baylior/{name}.png').read_bytes()).digest()
tree=ET.parse(root/'sitemap.xml'); assert any(e.text=='https://trovotechsolutions.in/products/baylior/' for e in tree.iter() if e.tag.endswith('loc'))
assert 'Require local' in (page.parent/'.htaccess').read_text()
print(f'PASS: {checked} local references, anchors, unique IDs, safe preview links, no-price schema, wording, approved screenshot hashes, share-card size and sitemap XML.')
